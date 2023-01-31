from django.contrib import admin
from blog.models import Post, Tag, Comment


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'post',)
    raw_id_fields = ('post', 'author',)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'published_at',)
    raw_id_fields = ('author', 'likes', 'tags',)


admin.site.register(Tag)
