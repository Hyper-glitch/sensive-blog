"""Module, that manipulates with database objects."""
from django.db.models import Prefetch, Count

from blog.models import Comment, Post, Tag


def get_related_posts_count(tag):
    return tag.posts__count


def get_likes_count(post):
    return post.likes__count


def serialize_post(post):
    return {
        'title': post.title,
        'teaser_text': post.text[:200],
        'author': post.author.username,
        'comments_amount': len(Comment.objects.filter(post=post)),
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': [serialize_tag(tag) for tag in post.tags.all()],
        'first_tag_title': post.tags.all()[0].title,
    }


def serialize_post_optimized(post):
    return {
        'title': post.title,
        'teaser_text': post.text[:200],
        'author': post.author.username,
        'comments_amount': post.comments_count,
        'image_url': post.image.url if post.image else None,
        'published_at': post.published_at,
        'slug': post.slug,
        'tags': [serialize_tag_optimized(tag) for tag in post.tags.all()],
        'first_tag_title': post.tags.all()[0].title,
    }


def serialize_tag(tag):
    return {
        'title': tag.title,
        'posts_with_tag': len(Post.objects.filter(tags=tag)),
    }


def serialize_tag_optimized(tag):
    return {
        'title': tag.title,
        'posts_with_tag': tag.posts_amount,
    }


def get_most_popular_posts(top_obj_amount):
    posts_prefetch = Prefetch('tags', queryset=Tag.objects.annotate(posts_amount=Count('posts')))
    popular_posts = Post.objects.popular().prefetch_related('author').prefetch_related(posts_prefetch)[:top_obj_amount] \
        .fetch_with_comments_count()
    most_popular_posts = popular_posts[:top_obj_amount]
    return most_popular_posts, posts_prefetch
