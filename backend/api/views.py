import uuid

from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import (SAFE_METHODS, AllowAny,
                                        IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from api.filters import IngredientSearchFilter, RecipeFilter
from api.paginators import CustomPagination
from api.permissions import IsAuthorOrReadOnly
from api.serializers import (FavoriteAndShoppingCartSerializer,
                             FavoriteSerializer, FollowSerializer,
                             FollowShowSerialize, IngredientsSerializer,
                             RecipeSerializerGET, RecipeSerializerPOST,
                             ShoppingListSerializer, TagsSerializer,
                             UserAvatar, UserCastomSerializer)
from api.utils import dowload_shoppig_list
from recipes.models import Ingredient, IngredientsRecipe, Recipe, Tag
from user.models import Follow, User


class RecipeViewSet(viewsets.ModelViewSet):
    """Представление Рецептов."""

    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializerGET
    permission_classes = (IsAuthorOrReadOnly, IsAuthenticatedOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

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
        return self.add_favorite_or_shopping_cart(
            request, pk, FavoriteSerializer
        )

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        url_path='shopping_cart',
        url_name='shopping_cart',
        permission_classes=(IsAuthenticated,)
    )
    def add_shopping_cart(self, request, pk=None):
        return self.add_favorite_or_shopping_cart(
            request, pk, ShoppingListSerializer
        )

    def add_favorite_or_shopping_cart(self, request, pk, serializer_class):
        recipe = self.get_object()
        author = request.user

        if request.method == 'POST':
            serializer = serializer_class(
                data={'author': author.id, 'recipe': recipe.id})
            serializer.is_valid(raise_exception=True)
            instance = serializer.save()
            serializer_data = FavoriteAndShoppingCartSerializer(
                instance.recipe).data
            return Response(
                serializer_data,
                status=status.HTTP_201_CREATED
            )
        instance = serializer_class.Meta.model.objects.filter(
            author=author, recipe=recipe
        )
        if instance:
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'errors'}, status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=['GET'],
        detail=False,
        url_path='download_shopping_cart',
        url_name='download_shopping_cart',
        permission_classes=(IsAuthenticated,)
    )
    def preparing_shopping_list(self, request):
        """Подготовка к скачиванию списка покупок."""
        ingredients = (
            IngredientsRecipe.objects
            .filter(recipe__shopping_lists__author=request.user)
            .values('ingredient__name', 'ingredient__measurement_unit')
            .annotate(total_amount=Sum('amount'))
        )
        if not ingredients:
            return Response(
                {'message': 'Список покупок пуст.'},
                status=status.HTTP_204_NO_CONTENT
            )
        return dowload_shoppig_list(self, request, ingredients)


@api_view(['GET'])
@permission_classes([AllowAny])
def short_link(request, short_link):
    """Представление Короткой ссылки"""
    recipe = get_object_or_404(Recipe, short_link=short_link)
    return redirect('recipes-detail', pk=recipe.pk)


class TagsViewSet(viewsets.ModelViewSet):
    """Представление тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagsSerializer
    http_method_names = ('get',)
    pagination_class = None
    permission_classes = (AllowAny,)


class IngredientsViewSet(viewsets.ModelViewSet):
    """Представление ингредиентов."""

    queryset = Ingredient.objects.all()
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
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = CustomPagination

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
            result.is_valid(raise_exception=True)
            result.save()
            return Response(
                {'avatar': self.get_serializer(user).data.get('avatar')},
                status=status.HTTP_200_OK
            )
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
        authors = Follow.objects.filter(subscriber=self.request.user)
        paginator = self.paginate_queryset(authors)
        serializer = FollowSerializer(
            paginator, context={'request': request}, many=True
        )
        return self.get_paginated_response(serializer.data)

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
            serializer.is_valid(raise_exception=True)
            serializer.save()
            author_serializer = FollowShowSerialize(
                author, context={'request': request}
            )
            return Response(
                author_serializer.data,
                status=status.HTTP_201_CREATED
            )
        subscribed = Follow.objects.filter(
            subscriber=request.user, author=author
        )
        if subscribed:
            subscribed.delete()
            return Response(
                {'Successful unsubscription'},
                status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'errors'}, status=status.HTTP_400_BAD_REQUEST)
