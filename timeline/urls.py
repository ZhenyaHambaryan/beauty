from django.conf.urls import include, url
from rest_framework.routers import DefaultRouter
from django.urls import path
from . import views

router = DefaultRouter()
router.register(r'post', views.PostViewSet)
router.register(r'post-comment', views.PostCommentViewSet)
router.register(r'review', views.ReviewViewSet)
router.register(r'post-report', views.ReportPostViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
    path('like-or-dislike/<int:pk>/',views.like_or_dislike),
    path('get-user-posts-only-file/<int:pk>/',views.get_user_posts_only_file),
    path('reply-to-review/<int:pk>/',views.reply_to_review),

    path('accept-post/<int:pk>/',views.accept_post),
    path('accept-comment/<int:pk>/',views.accept_comment),
    path('accept-review/<int:pk>/',views.accept_review),

    path('cancel-post/<int:pk>/',views.cancel_post),
    path('cancel-comment/<int:pk>/',views.cancel_comment),
    path('cancel-review/<int:pk>/',views.cancel_review),

    path('hide-post/<int:pk>/',views.hide_post),
]
