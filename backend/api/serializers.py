from djoser.serializers import UserSerializer
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueTogetherValidator

from api.constant import WRONGUSERNAME
from api.fields import Base64ImageField
from recipes.models import (Favorite, Ingredient, IngredientsRecipe, Recipe,
                            ShoppingList, Tag)
from user.models import Follow, User


class UserFoodgramSerializer(UserSerializer):
    """Сериализатор для отображения пользователя."""

    is_subscribed = serializers.SerializerMethodField()
    avatar = Base64ImageField(required=False, allow_null=True)

    class Meta:
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'avatar',)
        model = User

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        return user.is_authenticated and Follow.objects.filter(
            subscriber=user, author=obj).exists()


class UserAvatar(serializers.ModelSerializer):
    """Сериализатор для отображения аватара."""

    avatar = Base64ImageField(required=True)

    class Meta:
        fields = ('avatar',)
        model = User


class UserFoodgramCreateSerializer(UserSerializer):
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


class FavoriteAndShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор для избранного рецептов."""

    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class ShowFollowRecipesSerializer(serializers.ModelSerializer):
    """Сериализатор для представления рецептов подписчиков."""

    class Meta:
        fields = ('id', 'tags', 'author', 'ingredients',
                  'name', 'image', 'text', 'cooking_time')
        model = Recipe


class FollowShowSerializer(UserFoodgramSerializer):
    """Сериализатор отображения подписок."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = UserFoodgramSerializer.Meta.fields + (
            'recipes', 'recipes_count',
        )

    def get_recipes(self, obj):
        request = self.context.get('request')
        author_recipes = obj.recipes.all()
        limit = request.query_params.get('recipes_limit')
        if limit and limit.isdigit():
            author_recipes = author_recipes[:int(limit)]
        return FavoriteAndShoppingCartSerializer(
            author_recipes, context={'request': request}, many=True).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class FollowSerializer(serializers.ModelSerializer):
    """Сериализатор для представления подписчиков."""

    class Meta:
        model = Follow
        fields = ('subscriber', 'author')
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

    def to_representation(self, instance):
        serializer = FollowShowSerializer(
            instance.author,
            context=self.context,
        )
        return serializer.data


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор для избранного."""

    class Meta:
        model = Favorite
        fields = ('author', 'recipe')

    def validate(self, data):
        if Favorite.objects.filter(
                author=data['author'], recipe=data['recipe']).exists():
            raise serializers.ValidationError('Рецепт уже в избранном')
        return data

    def to_representation(self, instance):
        serializer = FavoriteAndShoppingCartSerializer(
            instance,
            context=self.context
        )
        return serializer.data


class ShoppingListSerializer(serializers.ModelSerializer):
    """Сериализатор для списка покупок."""

    class Meta:
        model = ShoppingList
        fields = ('author', 'recipe')

    def validate(self, data):
        if ShoppingList.objects.filter(
                author=data['author'], recipe=data['recipe']).exists():
            raise serializers.ValidationError('Рецепт уже в списке покупок')
        return data

    def to_representation(self, instance):
        serializer = FavoriteAndShoppingCartSerializer(
            instance,
            context=self.context
        )
        return serializer.data


class TagsSerializer(serializers.ModelSerializer):
    """Сериализатор для тегов."""

    class Meta:
        fields = '__all__'
        model = Tag


class IngredientsSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов."""

    class Meta:
        fields = '__all__'
        model = Ingredient


class IngredientsRecipeSerializerPOST(serializers.ModelSerializer):
    """Сериализатор для создания ингредиентов рецептов."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
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

    author = UserFoodgramSerializer()
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
        """Для вывода в списке покупок."""
        request = self.context.get('request')
        return (
            request and request.user.is_authenticated
            and request.user.shopping_lists.filter(recipe=obj).exists()
        )

    def get_is_favorited(self, obj):
        """Для вывода избранного."""
        request = self.context.get('request')
        return (
            request and request.user.is_authenticated
            and request.user.favorites.filter(recipe=obj).exists()
        )


class RecipeSerializerPOST(serializers.ModelSerializer):
    """Сериализатор для создания рецептов."""

    image = Base64ImageField(required=True)
    author = UserFoodgramSerializer(read_only=True)
    ingredients = IngredientsRecipeSerializerPOST(
        many=True, write_only=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
    )

    class Meta:
        fields = ('author', 'ingredients', 'tags', 'image',
                  'name', 'text', 'cooking_time',)
        model = Recipe

    @staticmethod
    def add_ingredients_and_tags(ingredients, tags, recipe):
        """Добавляет ингредиенты."""
        ingredients_data = ingredients
        tags_data = tags
        recipe.tags.set(tags_data)
        IngredientsRecipe.objects.bulk_create(
            IngredientsRecipe(
                ingredient=ingredient.get('id'),
                recipe=recipe,
                amount=ingredient.get('amount')
            )
            for ingredient in ingredients_data
        )

    def validate(self, value):
        tags = value.get('tags')
        ingredients = value.get('ingredients')

        if not tags:
            raise ValidationError(
                {'tags': 'Необходим хотя-бы один тег!'})
        if len(tags) != len(set(tags)):
            raise ValidationError(
                {'tags': 'Тег не должны повторяться!'})

        if not ingredients:
            raise ValidationError(
                {'ingredients': 'Необходимы ингредиенты!'})
        ingredient_id = (item['id'] for item in ingredients)
        unique_id = set(ingredient_id)
        if len(unique_id) != len(ingredients):
            raise ValidationError(
                {'ingredients': 'Ингредиенты не должны повторяться!'}
            )
        return value

    def create(self, validated_data):
        """Для создания рецептов."""
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(
            author=self.context.get('request').user,
            **validated_data,
        )
        self.add_ingredients_and_tags(
            ingredients,
            tags,
            recipe
        )
        return recipe

    def update(self, instance, validated_data):
        """Для обновления рецептов."""
        instance.ingredients.clear()
        instance.tags.clear()
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        self.add_ingredients_and_tags(
            ingredients,
            tags,
            instance,
        )
        return super().update(instance, validated_data)

    def to_representation(self, recipe):
        """Переопределяет сериализатор для чтения."""
        serializer = RecipeSerializerGET(recipe, context=self.context)
        return serializer.data
