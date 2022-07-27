"""Module, that manipulates with database objects."""
from typing import Tuple

from django.db.models import Prefetch, Count, QuerySet

from blog.models import Post, Tag


def serialize_post(post: Post) -> dict:
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


def serialize_tag(tag: Tag) -> dict:
    return {
        'title': tag.title,
        'posts_with_tag': tag.posts_amount,
    }


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
