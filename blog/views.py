from django.shortcuts import render

from blog.blog_tools import (
    serialize_post_optimized, serialize_tag_optimized, get_most_popular_posts,
)
from blog.models import Comment, Post, Tag


def index(request):
    top_obj_amount = 5
    most_popular_posts, posts_prefetch = get_most_popular_posts(top_obj_amount)

    fresh_posts = Post.objects.prefetch_related('author').prefetch_related(posts_prefetch).\
        comments().order_by('-published_at')
    most_fresh_posts = list(fresh_posts)[:top_obj_amount]

    most_popular_tags = Tag.objects.popular()[:top_obj_amount]

    context = {
        'most_popular_posts': [serialize_post_optimized(post) for post in most_popular_posts],
        'page_posts': [serialize_post_optimized(post) for post in most_fresh_posts],
        'popular_tags': [serialize_tag_optimized(tag) for tag in most_popular_tags],
    }
    return render(request, 'index.html', context)


def post_detail(request, slug):
    top_obj_amount = 5
    serialized_comments = []
    most_popular_posts, posts_prefetch = get_most_popular_posts(top_obj_amount)
    post = Post.objects.prefetch_related('author').likes().get(slug=slug)
    comments = Comment.objects.prefetch_related('author').filter(post=post)
    most_popular_tags = Tag.objects.popular()[:top_obj_amount]
    related_tags = post.tags.popular()

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
        'tags': [serialize_tag_optimized(tag) for tag in related_tags],
    }
    context = {
        'post': serialized_post,
        'popular_tags': [serialize_tag_optimized(tag) for tag in most_popular_tags],
        'most_popular_posts': [
            serialize_post_optimized(post) for post in most_popular_posts
        ],
    }
    return render(request, 'post-details.html', context)


def tag_filter(request, tag_title):
    top_obj_amount = 5
    tags_with_posts = Tag.objects.popular()
    tag = tags_with_posts.get(title=tag_title)

    most_popular_posts, posts_prefetch = get_most_popular_posts(top_obj_amount)
    most_popular_tags = tags_with_posts[:top_obj_amount]
    related_posts = tag.posts.prefetch_related('author').prefetch_related(posts_prefetch).comments()[:20]

    context = {
        'tag': tag.title,
        'popular_tags': [serialize_tag_optimized(tag) for tag in most_popular_tags],
        'posts': [serialize_post_optimized(post) for post in related_posts],
        'most_popular_posts': [serialize_post_optimized(post) for post in most_popular_posts],
    }

    return render(request, 'posts-list.html', context)


def contacts(request):
    # позже здесь будет код для статистики заходов на эту страницу
    # и для записи фидбека
    return render(request, 'contacts.html', {})
