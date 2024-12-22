import uuid

from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import (SAFE_METHODS, AllowAny,
                                        IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from api.filters import IngredientSearchFilter, RecipeFilter
from api.permissions import AnonimOrAuthenticatedReadOnly, IsAuthorOrReadOnly
from api.serializers import (FavoriteSerializer, FollowSerializer,
                             FollowShowSerialize, IngredientsSerializer,
                             RecipeFavoriteSerializer, RecipeSerializerGET,
                             RecipeSerializerPOST,
                             RecipeShoppingListSerializer,
                             ShoppingListSerializer, TagsSerializer,
                             UserAvatar, UserCastomSerializer)
from recipes.models import Favorite, Ingredients, Recipe, ShoppingList, Tags
from user.models import Follow, User


class RecipeViewSet(viewsets.ModelViewSet):
    """Представление Рецептов."""

    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializerGET
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly, )
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от запроса."""
        if self.request.method in SAFE_METHODS:
            return RecipeSerializerGET
        return RecipeSerializerPOST

    @action(
        methods=['GET'],
        detail=True,
        url_path='get-link',
        url_name='get_link',
    )
    def get_short_link(self, request, pk=None):
        """Получение короткой ссылки."""
        recipe = self.get_object()
        if not recipe.short_link:
            recipe.short_link = self.generate_link()
            recipe.save()
        full_url = request.build_absolute_uri(
            reverse('short-link', args=[recipe.short_link]))
        return Response({'short-link': full_url}, status=status.HTTP_200_OK)

    def generate_link(self):
        """Функция для получения короткой ссылки
        и проверки на оригинальность."""
        short_link = uuid.uuid4().hex[:3]
        while Recipe.objects.filter(short_link=short_link).exists():
            short_link = uuid.uuid4().hex[:3]
        return short_link

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        url_path='favorite',
        url_name='favorite',
        permission_classes=(IsAuthenticated,)
    )
    def add_favorite(self, request, pk=None):
        """Добавление и удаление избранное."""
        recipe = self.get_object()
        author = self.request.user
        if request.method == 'POST':
            if Favorite.objects.filter(
                    author=author,
                    recipe=recipe).exists():
                return Response({'errors': 'Рецепт уже в избранном'},
                                status=status.HTTP_400_BAD_REQUEST)
            serializer = FavoriteSerializer(
                data={'author': request.user.id, 'recipe': recipe.id})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            favorite_serializer = RecipeFavoriteSerializer(recipe)
            return Response(
                favorite_serializer.data, status=status.HTTP_201_CREATED)
        favorite_recipe = get_object_or_404(
            Favorite, author=request.user, recipe=recipe
        )
        favorite_recipe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        url_path='shopping_cart',
        url_name='shopping_cart',
        permission_classes=(IsAuthenticated,)
    )
    def add_shopping_cart(self, request, pk=None):
        """Добавление и удаление список покупко."""
        recipe = self.get_object()
        author = self.request.user
        if request.method == 'POST':
            if ShoppingList.objects.filter(
                    author=author,
                    recipe=recipe).exists():
                return Response({'errors': 'Рецепт уже в спискe покупок'},
                                status=status.HTTP_400_BAD_REQUEST)
            serializer = ShoppingListSerializer(
                data={'author': request.user.id, 'recipe': recipe.id})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            shopping_cart_serializer = RecipeShoppingListSerializer(recipe)
            return Response(
                shopping_cart_serializer.data, status=status.HTTP_201_CREATED)
        shopping_cart = get_object_or_404(
            ShoppingList, author=request.user, recipe=recipe
        )
        shopping_cart.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['GET'],
        detail=False,
        url_path='download_shopping_cart',
        url_name='download_shopping_cart',
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        """Скачивание списка покупок."""
        author = request.user
        shopping_list_items = ShoppingList.objects.filter(
            author=author).select_related('recipe')
        if not shopping_list_items:
            return Response(
                {'message': 'Список покупок пуст.'},
                status=status.HTTP_204_NO_CONTENT
            )
        ingredients = {}
        for item in shopping_list_items:
            recipe = item.recipe
            for ingredient in recipe.recipe_ingredients.all():
                ingr_name = ingredient.ingredient.name
                ingr_amount = ingredient.amount
                ingr_measurement_unit = (
                    ingredient.ingredient.measurement_unit
                )
                if ingr_name in ingredients:
                    ingredients[ingr_name]['amount'] += ingr_amount
                else:
                    ingredients[ingr_name] = {
                        'amount': ingr_amount,
                        'measurement_unit': ingr_measurement_unit
                    }
        response_content = "Список ингредиентов для покупоки:\n\n"
        for name, amount in ingredients.items():
            response_content += (
                f"{name}: {amount['amount']}"
                f"{amount['measurement_unit']}\n"
            )
        response = HttpResponse(
            response_content,
            content_type='text/plain'
        )
        response['Content-Disposition'] = (
            'attachment; filename="shopping_cart.txt"'
        )

        return response


@api_view(['GET'])
@permission_classes([AllowAny])
def short_link(request, short_link):
    """Представление Короткой ссылки"""
    recipe = get_object_or_404(Recipe, short_link=short_link)
    return redirect('recipes-detail', pk=recipe.pk)


class TagsViewSet(viewsets.ModelViewSet):
    """Представление тегов."""

    queryset = Tags.objects.all()
    serializer_class = TagsSerializer
    http_method_names = ('get',)
    pagination_class = None
    permission_classes = (AllowAny,)


class IngredientsViewSet(viewsets.ModelViewSet):
    """Представление ингредиентов."""

    queryset = Ingredients.objects.all()
    serializer_class = IngredientsSerializer
    http_method_names = ('get',)
    filter_backends = (DjangoFilterBackend, )
    filterset_class = IngredientSearchFilter
    search_fields = ('$name',)
    pagination_class = None
    permission_classes = (AllowAny,)


class UserCustomViewSet(UserViewSet):
    """Представление пользователя."""

    queryset = User.objects.all()
    serializer_class = UserCastomSerializer
    permission_classes = (AnonimOrAuthenticatedReadOnly, )

    @action(
        methods=['GET'],
        detail=False,
        url_path='me',
        url_name='me',
        permission_classes=(IsAuthenticated,)
    )
    def me(self, request):
        """Представление профиля залогиненым пользователям."""
        user = self.request.user
        result = self.get_serializer(user, context={'request': request})
        return Response(result.data, status=status.HTTP_200_OK)

    @action(
        methods=['PUT', 'DELETE'],
        detail=False,
        url_path='me/avatar',
        url_name='me_avatar',
        permission_classes=(IsAuthenticated, IsAuthorOrReadOnly)
    )
    def update_avatar(self, request):
        """Добавление и удаление аватарки."""
        user = request.user
        avatar = request.data.get('avatar')
        if request.method == 'PUT':
            result = UserAvatar(
                data={'avatar': avatar}, instance=user, partial=True)
            if result.is_valid():
                result.save()
                return Response(
                    {'avatar': self.get_serializer(user).data.get('avatar')},
                    status=status.HTTP_200_OK
                )
            return Response(result.errors, status=status.HTTP_400_BAD_REQUEST)
        elif request.method == 'DELETE':
            user.avatar = None
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['GET'],
        detail=False,
        url_path='subscriptions',
        url_name='subscriptions',
        permission_classes=(IsAuthenticated,)
    )
    def get_following_me(self, request):
        """Получение списка подписок рецептов пользователя."""
        users = User.objects.filter(author__subscriber=request.user)
        paginator = PageNumberPagination()
        result_pg = paginator.paginate_queryset(
            queryset=users, request=request
        )
        result_sr = FollowShowSerialize(
            result_pg, context={'request': request}, many=True)
        return paginator.get_paginated_response(result_sr.data)

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        url_path='subscribe',
        url_name='subscribe',
        permission_classes=(IsAuthenticated,)
    )
    def add_or_delete_follow(self, request, id):
        """Подписка и отписка от автора рецепта."""
        author = get_object_or_404(User, id=id)
        if request.method == 'POST':
            serializer = FollowSerializer(
                data={'subscriber': request.user.id, 'author': author.id}
            )
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                author_serializer = FollowShowSerialize(
                    author, context={'request': request}
                )
                return Response(
                    author_serializer.data,
                    status=status.HTTP_201_CREATED
                )

        subscribed = get_object_or_404(
            Follow, subscriber=request.user, author=author
        )
        subscribed.delete()
        return Response(
            {'Successful unsubscription'},
            status=status.HTTP_204_NO_CONTENT
        )
