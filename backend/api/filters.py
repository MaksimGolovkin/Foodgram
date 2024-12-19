from django_filters import rest_framework as filters

from recipes.models import Ingredients, Recipe


class IngredientSearchFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredients
        fields = ('name',)


class RecipeFilter(filters.FilterSet):
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')
    is_favorited = filters.BooleanFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = ('tags', 'author',)

    def filter_is_favorited(self, queryset, name, value):
        user = self.request.user
        if user.is_authenticated:
            if value:
                return queryset.filter(favorite__author=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if user.is_authenticated:
            if value:
                return queryset.filter(shopping_list__author=self.request.user)
        return queryset
