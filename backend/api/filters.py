from django_filters import rest_framework as filters

from recipes.models import Ingredient, Recipe


class IngredientSearchFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(filters.FilterSet):
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = ('tags', 'author',)

    def is_user_authenticated(self):
        return self.request.user.is_authenticated

    def filter_is_favorited(self, queryset, name, value):
        if self.is_user_authenticated() and value:
            return queryset.filter(favorites__author=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if self.is_user_authenticated() and value:
            return queryset.filter(shopping_lists__author=self.request.user)
        return queryset
