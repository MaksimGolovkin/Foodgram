from django.contrib import admin

from recipes.models import (Favorite, Ingredients, IngredientsRecipe, Recipe,
                            ShoppingList, Tags, TagsRecipe)

admin.site.empty_value_display = "-пусто-"


@admin.register(Tags)
class TagAdmin(admin.ModelAdmin):
    """Класс настройки раздела Тэгов."""
    list_display = ('id', 'name', 'slug')
    list_filter = ('name',)
    search_fields = ('name',)


@admin.register(Ingredients)
class IngredientsAdmin(admin.ModelAdmin):
    """Класс настройки раздела Ингредиенты."""
    list_display = ('id', 'name', 'measurement_unit')
    list_filter = ('name',)
    search_fields = ('name',)


class IngredientsInline(admin.TabularInline):
    """Класс, позволяющий добавлять ингредиенты в рецепты."""
    model = IngredientsRecipe
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Класс настройки раздела рецепты."""
    list_display = ('id', 'name', 'author', 'text',
                    'cooking_time', 'image',
                    'pub_date')
    inlines = [IngredientsInline,]
    list_filter = ('author', 'name', 'tags')
    list_editable = ('author',)
    search_fields = ('author', 'name')


@admin.register(IngredientsRecipe)
class IngredientsRecipeAdmin(admin.ModelAdmin):
    """Класс настройки раздела ингредиентов и рецептов."""
    list_display = ('id', 'ingredient', 'recipe', 'amount')
    list_filter = ('ingredient', 'recipe')
    search_fields = ('ingredient', 'recipe')


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Класс настройки раздела избранное."""
    list_display = ('id', 'author', 'recipe')
    list_editable = ('author', 'recipe')
    list_filter = ('author',)
    search_fields = ('author',)


@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    """Класс настройки раздела ингредиентов и рецептов."""
    list_display = ('id', 'author', 'recipe')
    list_editable = ('author', 'recipe')
    list_filter = ('author',)
    search_fields = ('author',)


@admin.register(TagsRecipe)
class TagsRecipetAdmin(admin.ModelAdmin):
    """Класс настройки раздела ингредиентов и рецептов."""
    list_display = ('id', 'name', 'recipe')
    list_filter = ('name', 'recipe')
    search_fields = ('name', 'recipe')
