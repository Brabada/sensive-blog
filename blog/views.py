from django.shortcuts import render
from blog.models import Post, Tag, User
from django.db.models import Count, Prefetch
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404


def serialize_post(post):
    return {
        'title': post.title,
        'teaser_text': post.text[:200],
        'author': post.author.username,
        'comments_amount': post.comments_count,
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': [serialize_tag(tag) for tag in post.tags.all()],
        'first_tag_title': post.tags.all()[0].title,
    }


def serialize_tag(tag):
    return {
        'title': tag.title,
        'posts_with_tag': tag.posts_count,
    }


def index(request):
    queryset_tags = Tag.objects.annotate(posts_count=Count('posts'))
    prefetched_tags = Prefetch('tags', queryset=queryset_tags)
    most_popular_posts = Post.objects.popular() \
        .prefetch_related(prefetched_tags) \
        .select_related('author')[:5] \
        .fetch_with_comments_count()

    fresh_posts = Post.objects.annotate(comments_count=Count('comments'))
    most_fresh_posts = fresh_posts.order_by('-published_at') \
        .prefetch_related(prefetched_tags).select_related('author')[:5]

    prefetched_posts = Prefetch('posts',
                                queryset=Post.objects.order_by('title'))
    most_popular_tags = Tag.objects.popular()[:5] \
        .prefetch_related(prefetched_posts)

    context = {
        'most_popular_posts': [
            serialize_post(post) for post in most_popular_posts
        ],
        'page_posts': [
            serialize_post(post) for post in most_fresh_posts
        ],
        'popular_tags': [
            serialize_tag(tag) for tag in most_popular_tags
        ],
    }
    return render(request, 'index.html', context)


def post_detail(request, slug):
    queryset_tags = Tag.objects.annotate(posts_count=Count('posts'))
    prefetched_tags = Prefetch('tags', queryset=queryset_tags)
    try:
        post = Post.objects.annotate(likes_count=Count('likes')) \
            .prefetch_related(prefetched_tags) \
            .get(slug=slug)
    except ObjectDoesNotExist:
        raise Http404("Can't get Post model object")

    comments = post.comments.all().select_related('author')

    serialized_comments = []
    for comment in comments:
        serialized_comments.append({
            'text': comment.text,
            'published_at': comment.published_at,
            'author': comment.author.username,
        })

    serialized_post = {
        'title': post.title,
        'text': post.text,
        'author': post.author.username,
        'comments': serialized_comments,
        'likes_amount': post.likes_count,
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': [serialize_tag(tag) for tag in post.tags.all()],
    }

    most_popular_posts = Post.objects.popular() \
        .prefetch_related(prefetched_tags).select_related('author')[:5] \
        .fetch_with_comments_count()

    prefetched_posts = Prefetch('posts',
                                queryset=Post.objects.order_by('title'))
    most_popular_tags = Tag.objects.popular() \
        .prefetch_related(prefetched_posts)[:5]

    context = {
        'post': serialized_post,
        'popular_tags': [
            serialize_tag(tag) for tag in most_popular_tags
        ],
        'most_popular_posts': [
            serialize_post(post) for post in most_popular_posts
        ],
    }
    return render(request, 'post-details.html', context)


def tag_filter(request, tag_title):
    queryset_tags = Tag.objects.annotate(posts_count=Count('posts'))
    prefetched_tags = Prefetch('tags', queryset=queryset_tags)
    prefetched_authors = Prefetch(
        'author',
        queryset=User.objects.order_by('username'))

    most_popular_posts = Post.objects.popular() \
        .prefetch_related(prefetched_tags, prefetched_authors)[:5] \
        .fetch_with_comments_count()

    prefetched_posts = Prefetch(
        'posts',
        queryset=Post.objects.order_by('title'))
    most_popular_tags = Tag.objects.popular() \
        .prefetch_related(prefetched_posts)[:5]

    try:
        tag = Tag.objects.get(title=tag_title)
        related_posts = tag.posts.all() \
            .prefetch_related(prefetched_tags, prefetched_authors)[:20] \
            .fetch_with_comments_count()
    except ObjectDoesNotExist:
        raise Http404("Can't get Tag model object")

    context = {
        'tag': tag.title,
        'popular_tags': [
            serialize_tag(tag) for tag in most_popular_tags
        ],
        'posts': [serialize_post(post) for post in related_posts],
        'most_popular_posts': [
            serialize_post(post) for post in most_popular_posts
        ],
    }
    return render(request, 'posts-list.html', context)


def contacts(request):
    # позже здесь будет код для статистики заходов на эту страницу
    # и для записи фидбека
    return render(request, 'contacts.html', {})
