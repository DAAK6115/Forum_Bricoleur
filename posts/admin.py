from django.contrib import admin
from users.models import Notification
from posts.models import Post, Comment

admin.site.register(Notification)
admin.site.register(Post)
admin.site.register(Comment)
