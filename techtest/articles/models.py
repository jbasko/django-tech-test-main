from django.db import models


class Article(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField(blank=True)
    regions = models.ManyToManyField(
        'regions.Region', related_name='articles', blank=True
    )
    author = models.ForeignKey(
        'Author', related_name='articles', blank=True, null=True,
        on_delete=models.SET_NULL,
    )


class Author(models.Model):
    first_name = models.CharField(max_length=128)
    last_name = models.CharField(max_length=128)
