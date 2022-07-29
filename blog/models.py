from django.contrib.auth.models import User
from django.db import models
from django.db.models import Count
from django.urls import reverse


class PostQuerySet(models.QuerySet):
    """Custom Post queryset manager."""

    def filter_by_year(self, year):
        """
        Manager that filter posts by year.
        :params year: value for filtering by.
        :return: filtered posts.
        """
        posts_at_year = self.filter(published_at__year=year).order_by('published_at')
        return posts_at_year

    def count_comments(self):
        """
        Manager that counts comments.
        :return: posts with comments amount.
        """
        return self.annotate(comments_count=Count('comments'))

    def count_likes(self):
        """
        Manager that counts likes.
        :return: posts with likes amount.
        """
        return self.annotate(likes_count=Count('likes'))

    def fetch_with_comments_count(self):
        """
        Manager that counts comments and assign their to post objects. Use to avoid problem with using two annotates.
        :return: posts with comments amount.
        """
        most_popular_posts_ids = [post.id for post in self]
        posts_with_comments = Post.objects.filter(id__in=most_popular_posts_ids).annotate(
            comments_count=Count('comments'))
        ids_and_comments = posts_with_comments.values_list('id', 'comments_count')
        count_for_id = dict(ids_and_comments)

        for post in self:
            post.comments_count = count_for_id[post.id]
        return self

    def get_most_popular_posts(self, posts_prefetch, top_obj_amount):
        """
        Manager that annotate and prefetch posts with likes and authors.
        :params posts_prefetch: amount of slicing posts.
        :params top_obj_amount: amount of slicing posts.
        :return: queryset ordered by likes, with authors and posts with comments amount; post's prefetch.
        """
        popular_posts = self.count_likes().order_by('-likes_count').prefetch_related('author').prefetch_related(
            posts_prefetch)[:top_obj_amount].fetch_with_comments_count()
        most_popular_posts = popular_posts[:top_obj_amount]
        return most_popular_posts


class TagQuerySet(models.QuerySet):
    """Custom Tag queryset manager."""

    def get_popular_posts(self):
        """
        Manager that count posts on tag.
        :return: popular tags order from max to min.
        """
        return self.count_posts().order_by('-posts_amount')

    def count_posts(self):
        """
        Manager that count posts on tag.
        :return: tags with posts amount.
        """
        return self.annotate(posts_amount=Count('posts'))


class Post(models.Model):
    """Model that describes post object."""

    title = models.CharField('Заголовок', max_length=200)
    text = models.TextField('Текст')
    slug = models.SlugField('Название в виде url', max_length=200)
    image = models.ImageField('Картинка')
    published_at = models.DateTimeField('Дата и время публикации')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        limit_choices_to={'is_staff': True},
    )
    likes = models.ManyToManyField(
        User,
        related_name='liked_posts',
        verbose_name='Кто лайкнул',
        blank=True,
    )
    tags = models.ManyToManyField(
        'Tag',
        related_name='posts',
        verbose_name='Теги',
    )
    objects = PostQuerySet.as_manager()

    class Meta:
        ordering = ['-published_at']
        verbose_name = 'пост'
        verbose_name_plural = 'посты'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('post_detail', args={'slug': self.slug})


class Tag(models.Model):
    """Model that describes tag object."""

    title = models.CharField('Тег', max_length=20, unique=True)
    objects = TagQuerySet.as_manager()

    class Meta:
        ordering = ['title']
        verbose_name = 'тег'
        verbose_name_plural = 'теги'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('tag_filter', args={'tag_title': self.slug})

    def clean(self):
        self.title = self.title.lower()


class Comment(models.Model):
    """Model that describes comment object."""

    text = models.TextField('Текст комментария')
    published_at = models.DateTimeField('Дата и время публикации')

    post = models.ForeignKey(
        'Post',
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Пост, к которому написан')

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
    )

    class Meta:
        ordering = ['published_at']
        verbose_name = 'комментарий'
        verbose_name_plural = 'комментарии'

    def __str__(self):
        return f'{self.author.username} under {self.post.title}'
