from django.core.validators import MinValueValidator
from django.db import models

from api.constant import (MAX_LEN_CHARFIELD, MAX_LEN_MINI, MAX_LEN_SLUGFIELD,
                          MIN_SCORE, UNIT_MEASUREMENT)
from user.models import User


class Tags(models.Model):
    name = models.CharField(
        max_length=MAX_LEN_CHARFIELD,
        verbose_name='Название'
    )
    slug = models.SlugField(
        max_length=MAX_LEN_SLUGFIELD,
        unique=True,
        verbose_name='Слаг Тега',
    )

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

    def __str__(self):
        return self.name


class Ingredients(models.Model):
    name = models.CharField(
        max_length=MAX_LEN_CHARFIELD,
        verbose_name='Наименование'
    )
    measurement_unit = models.CharField(
        max_length=MAX_LEN_MINI,
        verbose_name='Единица измерения',
        choices=UNIT_MEASUREMENT
    )

    class Meta:
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор',
        help_text='Автор рецепта',
    )
    name = models.CharField(
        max_length=MAX_LEN_CHARFIELD,
        verbose_name='Наименование',
        help_text='Название рецепта',
    )
    image = models.ImageField(
        upload_to='recipes/images/',
        null=True,
        blank=True,
        default=None,
        verbose_name='Картинка',
    )
    text = models.TextField(
        verbose_name='Описание'
    )
    ingredients = models.ManyToManyField(
        Ingredients,
        through='IngredientsRecipe',
        verbose_name='Ингредиенты для рецепта',
        related_name='recipes',
    )
    tags = models.ManyToManyField(
        Tags,
        through='TagsRecipe',
        verbose_name='Теги для рецепта',
        related_name='recipes',
    )
    cooking_time = models.IntegerField(
        validators=[MinValueValidator(
            MIN_SCORE,
            message=f'Минимальное время приготовления {MIN_SCORE} мин.')],
        verbose_name='Время Приготовления',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
    )
    short_link = models.CharField(
        max_length=MAX_LEN_MINI,
        unique=True,
        blank=True,
        null=True,
        verbose_name='Короткая ссылка',
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"

    def __str__(self):
        return f'Рецепт:{self.name} Автора:{self.author}'


class IngredientsRecipe(models.Model):
    ingredient = models.ForeignKey(
        Ingredients,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Название рецепта',
        related_name='recipe_ingredients',
    )
    amount = models.IntegerField(
        validators=[MinValueValidator(
            MIN_SCORE,
            message=f'Минимальное количество {MIN_SCORE}.')],
        verbose_name='Количество',
    )

    class Meta:
        verbose_name = "Ингредиенты"
        verbose_name_plural = "Ингредиенты"
        constraints = [
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='unique_ingredients')]

    def __str__(self):
        return f'{self.ingredient.name} в рецепте: {self.recipe}'


class TagsRecipe(models.Model):
    name = models.ForeignKey(
        Tags,
        on_delete=models.CASCADE,
        verbose_name='Тег',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

    def __str__(self):
        return f'{self.name} в рецепте: {self.recipe}'


class Favorite(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='favorite'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='favorite'
    )

    class Meta:
        verbose_name = "Избранное"
        verbose_name_plural = "Избранное"
        constraints = [
            models.UniqueConstraint(
                fields=('author', 'recipe'),
                name='unique_favorite'),]

    def __str__(self):
        return f'У пользователя {self.author} в избранном: {self.recipe}'


class ShoppingList(models.Model):

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='shopping_list'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='shopping_list'
    )

    class Meta:
        verbose_name = "Сприсок покупок"
        verbose_name_plural = "Сприсок покупок"
        constraints = [
            models.UniqueConstraint(
                fields=('author', 'recipe'),
                name='unique_shopping_list'),]

    def __str__(self):
        return f'У пользователя {self.author} в списке покупок: {self.recipe}'
