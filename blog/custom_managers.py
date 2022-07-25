"""Module for custom managers."""
from django.db import models


class PostQuerySet(models.QuerySet):

    def year(self, year):
        """
        Manager that filter posts by year.
        :params year: value for filtering by.
        :return: filtered posts.
        """
        posts_at_year = self.filter(published_at__year=year).order_by('published_at')
        return posts_at_year
