import datetime as dt

from django.db.models import Avg
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueTogetherValidator

from reviews.models import Title, Genre, Category, Review, Comment
from users.models import User

START_SCORE = 1
END_SCORE = 10


class UserCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('email', 'username')

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError(
                'Имя пользователя не может быть "me"'
            )
        return value


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio', 'role')

    def validate_role(self, role):
        request_user = self.context['request'].user
        user = User.objects.get(username=request_user)
        if user.is_user:
            role = user.role
        return role


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        fields = ('name', 'slug')


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ('name', 'slug')


class TitlePostSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        many=True,
        slug_field='slug', queryset=Genre.objects.all()
    )
    category = serializers.SlugRelatedField(
        slug_field='slug', queryset=Category.objects.all()
    )

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'rating',
                  'description', 'genre', 'category')

    def validate_year(self, value):
        year_now = dt.date.today().year
        if year_now < value:
            raise serializers.ValidationError(
                'Нельзя добавлять произведения, которые еще не появились'
            )
        return value


class TitleGetSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(many=True)
    category = CategorySerializer()
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'rating',
                  'description', 'genre', 'category')

    def get_rating(self, obj):
        if obj.reviews.all().exists():
            return int(obj.reviews.aggregate(Avg('score'))['score__avg'])
        return None


class ValueTitleDefault(serializers.CurrentUserDefault):
    """
    Позволяет получить значение title из контекста.
    Для реализации проверки уникальности полей в Review.
    """
    requires_context = True

    def __call__(self, serializer_field):
        return serializer_field.context.get('view').kwargs.get('title_id')

    def __repr__(self):
        return '%s()' % self.__class__.__name__


class ReviewSerializer(serializers.ModelSerializer):
    """
    Преобразует информацию для работы через API по модели Review.
    """
    author = SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault()
    )
    title = serializers.HiddenField(default=ValueTitleDefault())

    class Meta:
        fields = ('id', 'text', 'author', 'score', 'pub_date', 'title')
        model = Review

        validators = [
            UniqueTogetherValidator(
                queryset=Review.objects.all(),
                fields=('author', 'title'),
                message='На это произведение можно оставлять только 1 отзыв!'
            )
        ]

    def validate_score(self, value):
        if not (isinstance(value, int)
                and START_SCORE <= value <= END_SCORE):
            raise serializers.ValidationError(
                'Оценка - целое число в диапазоне от 1 до 10!')
        return value


class CommentSerializer(serializers.ModelSerializer):
    """
    Преобразует информацию для работы через API по модели Comment.
    """
    author = SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        fields = ('id', 'text', 'author', 'pub_date')
        model = Comment
