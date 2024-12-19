import base64

from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from djoser.serializers import UserSerializer
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueTogetherValidator

from api.constant import WRONGUSERNAME
from recipes.models import (Favorite, Ingredients, IngredientsRecipe, Recipe,
                            ShoppingList, Tags, TagsRecipe)
from user.models import Follow, User


class Base64ImageField(serializers.ImageField):
    """Сериализатор для аватарок."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class UserCastomSerializer(UserSerializer):
    """Сериализатор для отображения пользователя."""

    is_subscribed = serializers.SerializerMethodField()
    avatar = Base64ImageField(required=False, allow_null=True)

    class Meta:
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'avatar',)
        model = User

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if not user.is_anonymous:
            return Follow.objects.filter(subscriber=user, author=obj).exists()
        return False


class UserAvatar(serializers.ModelSerializer):
    avatar = Base64ImageField(required=True)

    class Meta:
        fields = ('avatar',)
        model = User


class UserCustomCreateSerializer(UserSerializer):
    """Сериализатор для создания пользователя."""

    class Meta:
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'password')
        model = User
        extra_kwargs = {"password": {"write_only": True}}

    def validate(self, data):
        username = data.get('username')
        email = data.get('email')
        if username == WRONGUSERNAME:
            raise serializers.ValidationError(
                "Invalid Username"
            )
        if User.objects.filter(username=username):
            raise serializers.ValidationError(
                'That username is taken'
            )
        if User.objects.filter(email=email):
            raise serializers.ValidationError(
                'That email is taken'
            )
        return data

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class ShowFollowRecipesSerializer(serializers.ModelSerializer):
    """Сериализатор для представления рецептов подписчиков."""

    class Meta:
        fields = ('id', 'tags', 'author', 'ingredients',
                  'name', 'image', 'text', 'cooking_time')
        model = Recipe


class FollowSerializer(serializers.ModelSerializer):
    """Сериализатор для представления подписчиков."""

    class Meta:
        model = Follow
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('subscriber', 'author',),
                message='Already subscribed'
            )
        ]

    def validate(self, data):
        """Проверка, что пользователь не подписывается на себя."""
        if data['subscriber'] == data['author']:
            raise serializers.ValidationError(
                'Dont self following'
            )
        return data


class FollowShowRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения рецептов в подписке."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FollowShowSerialize(UserCastomSerializer):
    """Сериализатор отображения подписок."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count', 'avatar',)

    def get_recipes(self, obj):
        author_recipes = obj.recipes.all()
        return ShowFollowRecipesSerializer(author_recipes, many=True).data

    def get_recipes_count(self, object):
        return object.recipes.count()


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор для избранного."""

    class Meta:
        model = Favorite
        fields = ('author', 'recipe')


class RecipeFavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор для избранного рецептов."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class ShoppingListSerializer(serializers.ModelSerializer):
    """Сериализатор для списка покупок."""

    class Meta:
        model = ShoppingList
        fields = ('author', 'recipe')


class RecipeShoppingListSerializer(serializers.ModelSerializer):
    """Сериализатор для списка покупок рецептов."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class TagsSerializer(serializers.ModelSerializer):
    """Сериализатор для тегов."""

    class Meta:
        fields = '__all__'
        model = Tags


class TagsRecipeSerializer(serializers.ModelSerializer):
    """Сериализатор для тегов рецептов."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Tags.objects.all()
    )

    class Meta:
        fields = ('id',)
        model = TagsRecipe


class IngredientsSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов."""

    class Meta:
        fields = '__all__'
        model = Ingredients


class IngredientsRecipeSerializerPOST(serializers.ModelSerializer):
    """Сериализатор для создания ингредиентов рецептов."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredients.objects.all()
    )

    class Meta:
        fields = ('id', 'amount',)
        model = IngredientsRecipe


class IngredientsRecipeSerializerGET(serializers.ModelSerializer):
    """Сериализатор для чтения ингредиентов рецептов."""

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        fields = ('id', 'name', 'measurement_unit', 'amount')
        model = IngredientsRecipe


class RecipeSerializerGET(serializers.ModelSerializer):
    """Сериализатор для чтения рецептов."""

    author = UserCastomSerializer()
    ingredients = IngredientsRecipeSerializerGET(
        required=True, many=True, source='recipe_ingredients',)
    tags = TagsSerializer(many=True, read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)

    class Meta:
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time',
        )
        model = Recipe

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return request.user.shopping_list.filter(recipe=obj).exists()

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return request.user.favorite.filter(recipe=obj).exists()


class RecipeSerializerPOST(serializers.ModelSerializer):
    """Сериализатор для создания рецептов."""

    image = Base64ImageField(required=True)
    author = UserCastomSerializer(read_only=True)
    ingredients = IngredientsRecipeSerializerPOST(
        many=True, write_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tags.objects.all(),
        many=True
    )

    class Meta:
        fields = ('author', 'ingredients', 'tags', 'image',
                  'name', 'text', 'cooking_time',)
        model = Recipe

    def validate_ingredients(self, value):
        ingredients = value
        if not ingredients:
            raise ValidationError(
                {'ingredients': 'Необходимы ингредиенты!'})
        ingredients_list = []
        for item in ingredients:
            ingredient = get_object_or_404(Ingredients, name=item['id'])
            if ingredient in ingredients_list:
                raise ValidationError(
                    {'ingredients': 'Ингредиент уже добавлен!'})
            ingredients_list.append(ingredient)
        return value

    def validate_tags(self, value):
        tags = value
        if not tags:
            raise ValidationError(
                {'tags': 'Необходим хотя-бы один тег!'})
        tags_list = []
        for tag in tags:
            if tag in tags_list:
                raise ValidationError(
                    {'tags': 'Тег уже добавлен!'})
            tags_list.append(tag)
        return value

    def create(self, validated_data):
        """Для создания рецептов."""
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = super().create(validated_data)
        for ingredient_data in ingredients:
            ingredient_id = ingredient_data.get('id')
            amount = ingredient_data.get('amount')
            IngredientsRecipe.objects.update_or_create(
                ingredient=ingredient_id,
                recipe=recipe,
                amount=amount,
            )
        recipe.tags.set(tags)
        return recipe

    def update(self, instance, validated_data):
        """Для обновления рецептов."""
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time)
        instance.image = validated_data.get('image', instance.image)
        instance.save()
        if ingredients is not None:
            instance.ingredients.set(ingredients)
            for ingredient_data in ingredients:
                ingredient_id = ingredient_data.get('id')
                amount = ingredient_data.get('amount')
                IngredientsRecipe.objects.update_or_create(
                    ingredient=ingredient_id,
                    recipe=instance,
                    amount=amount,
                )
        if tags is not None:
            instance.tags.set(tags)
        return instance

    def to_representation(self, recipe):
        """Переопределяет сериализатор для чтения."""
        serializer = RecipeSerializerGET(recipe, context=self.context)
        return serializer.data
