from django.db import models

from django.contrib.auth import get_user_model

User = get_user_model()


class Genre(models.Model):

    name = models.TextField(max_length=256)
    slug = models.SlugField(unique=True, max_length=50)

    def __str__(self):
        return f'Жанр: {self.name}'


class Category(models.Model):

    name = models.TextField(max_length=256)
    slug = models.SlugField(unique=True, max_length=50)

    def __str__(self):
        return f'Категория: {self.name}'


class Title(models.Model):

    name = models.TextField(max_length=150)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL,
        null=True,
        related_name="titles"
    )
    genre = models.ManyToManyField(
        Genre
    )
    description = models.TextField(max_length=1000, blank=True, null=True)
    year = models.IntegerField()
    rating = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f'Название: {self.name}'


class Review(models.Model):
    """Модель для создания отзыва о произведении."""

    text = models.TextField(max_length=10000)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reviews')
    score = models.IntegerField()
    pub_date = models.DateTimeField('Дата создания', auto_now_add=True)
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE, related_name='reviews')

    def __str__(self):
        return self.text

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title'],
                name='unique_author_title'
            )
        ]


class Comment(models.Model):
    """Модель для создания комментария к отзыву."""

    text = models.TextField(max_length=1000)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comments')
    pub_date = models.DateTimeField('Дата создания', auto_now_add=True)
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name='comments')

    def __str__(self):
        return self.text
