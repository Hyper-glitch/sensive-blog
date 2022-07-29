"""Module, that manipulates with database objects."""
from typing import Tuple

from django.db.models import Prefetch, Count, QuerySet

from blog.models import Post, Tag


def get_most_popular_posts(top_obj_amount: int) -> Tuple[QuerySet, Prefetch]:
    """
    Annotate and prefetch posts with likes and authors.
    :params: amount of slicing posts.
    :return: queryset ordered by likes, with authors and posts with comments amount; post's prefetch.
    """
    posts_prefetch = Prefetch('tags', queryset=Tag.objects.annotate(posts_amount=Count('posts')))
    popular_posts = Post.objects.likes().order_by('-likes_count').prefetch_related('author').prefetch_related(
        posts_prefetch)[:top_obj_amount].fetch_with_comments_count()
    most_popular_posts = popular_posts[:top_obj_amount]

    return most_popular_posts, posts_prefetch
