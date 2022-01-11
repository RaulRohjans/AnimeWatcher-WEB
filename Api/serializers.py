from django.contrib.auth.models import User
from rest_framework import serializers
from Content.models import *


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class AnimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Anime_class
        fields = '__all__'


class EpisodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Episode_class
        fields = '__all__'


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category_class
        fields = '__all__'


class MyListSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyList_class
        fields = '__all__'


class SubmitAnimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubmitAnime_class
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment_class
        fields = '__all__'


class ReportCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report_Comment_Class
        fields = '__all__'


class CategoryNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category_class
        fields = ['mCategoryName']
