from django.core.handlers.wsgi import WSGIRequest
from django.db.models import Prefetch, Count
from django.http import HttpResponse
from django.shortcuts import render

from blog.models import Comment, Post, Tag


def index(request: WSGIRequest) -> HttpResponse:
    top_obj_amount = 5
    posts_prefetch = Prefetch('tags', queryset=Tag.objects.annotate(posts_amount=Count('posts')))

    most_popular_posts = Post.objects.get_most_popular_posts(posts_prefetch, top_obj_amount)
    fresh_posts = Post.objects.prefetch_related('author').prefetch_related(posts_prefetch). \
        count_comments().order_by('-published_at')
    most_fresh_posts = list(fresh_posts)[:top_obj_amount]

    most_popular_tags = Tag.objects.get_popular_posts()[:top_obj_amount]

    context = {
        'most_popular_posts': [serialize_post(post) for post in most_popular_posts],
        'page_posts': [serialize_post(post) for post in most_fresh_posts],
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
    }
    return render(request, 'index.html', context)


def post_detail(request: WSGIRequest, slug: str) -> HttpResponse:
    top_obj_amount = 5
    posts_prefetch = Prefetch('tags', queryset=Tag.objects.annotate(posts_amount=Count('posts')))
    serialized_comments = []

    most_popular_posts = Post.objects.get_most_popular_posts(posts_prefetch, top_obj_amount)
    post = Post.objects.prefetch_related('author').count_likes().get(slug=slug)
    comments = Comment.objects.select_related('author').filter(post=post)
    most_popular_tags = Tag.objects.get_popular_posts()[:top_obj_amount]
    related_tags = post.tags.get_popular_posts()

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
        'tags': [serialize_tag(tag) for tag in related_tags],
    }
    context = {
        'post': serialized_post,
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
        'most_popular_posts': [serialize_post(post) for post in most_popular_posts],
    }
    return render(request, 'post-details.html', context)


def tag_filter(request: WSGIRequest, tag_title: str) -> HttpResponse:
    top_obj_amount = 5
    posts_prefetch = Prefetch('tags', queryset=Tag.objects.annotate(posts_amount=Count('posts')))

    tags_with_posts = Tag.objects.get_popular_posts()
    tag = tags_with_posts.get(title=tag_title)

    most_popular_posts = Post.objects.get_most_popular_posts(posts_prefetch, top_obj_amount)
    most_popular_tags = tags_with_posts[:top_obj_amount]
    related_posts = tag.posts.prefetch_related('author').prefetch_related(posts_prefetch).count_comments()[:20]

    context = {
        'tag': tag.title,
        'popular_tags': [serialize_tag(tag) for tag in most_popular_tags],
        'posts': [serialize_post(post) for post in related_posts],
        'most_popular_posts': [serialize_post(post) for post in most_popular_posts],
    }

    return render(request, 'posts-list.html', context)


def contacts(request: WSGIRequest) -> HttpResponse:
    # позже здесь будет код для статистики заходов на эту страницу
    # и для записи фидбека
    return render(request, 'contacts.html', {})


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
