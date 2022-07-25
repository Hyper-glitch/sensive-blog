"""Module for custom managers."""
from django.db import models
from django.db.models import Count


class PostQuerySet(models.QuerySet):

    def year(self, year):
        """
        Manager that filter posts by year.
        :params year: value for filtering by.
        :return: filtered posts.
        """
        posts_at_year = self.filter(published_at__year=year).order_by('published_at')
        return posts_at_year


class TagQuerySet(models.QuerySet):

    def popular(self):
        """
        Manager that count tags on posts.
        :return: popular tags.
        """
        popular_tags = self.annotate(tags_amount=Count('posts')).order_by('-tags_amount')
        return popular_tags
