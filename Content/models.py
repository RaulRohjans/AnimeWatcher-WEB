from django.db import models
from django.conf import settings


# Create your models here.

class Anime_class(models.Model):
    mNameEN = models.CharField(primary_key=True, max_length=150, unique=True, null=False)
    mNameJP = models.CharField(null=True, max_length=150)
    mDescription = models.TextField(null=False)
    mCategories = models.ManyToManyField('Category_class')
    mThumbnail = models.CharField(null=True, max_length=255)
    mEpisodeCount = models.IntegerField(null=False, default=0)
    mOnGoing = models.BooleanField(default=False)


class Episode_class(models.Model):
    mID = models.BigAutoField(primary_key=True)
    mEpisodeNumber = models.IntegerField(null=False)
    mNameEN = models.CharField(null=False, max_length=150)
    mNameJP = models.CharField(null=True, max_length=150)
    mAnime = models.ForeignKey(Anime_class, on_delete=models.CASCADE, null=False)
    mLengthSecs = models.IntegerField(null=False)
    mViews = models.IntegerField(null=False)
    mReleaseDate = models.DateTimeField(null=False)
    mThumbnail = models.CharField(null=True, max_length=255)
    mVideoFileLink = models.CharField(null=True, max_length=1500)
    mVCDN = models.BooleanField(default=False)
    mIsSpecial = models.BooleanField(default=False)


class Category_class(models.Model):
    mCategoryName = models.CharField(primary_key=True, null=False, max_length=100, unique=True)
    mAnimeCount = models.IntegerField(null=False, default=0)


class SubmitAnime_class(models.Model):
    mID = models.BigAutoField(primary_key=True)
    mAnimeName = models.CharField(null=False, max_length=150)
    mUserEmail = models.EmailField(null=False)
    mUsername = models.CharField(null=False, max_length=50)
    mMoreInfo = models.TextField(null=True)
    mSubDate = models.DateTimeField(null=True)


class MyList_class(models.Model):
    mID = models.BigAutoField(primary_key=True)
    mUser = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=False)
    mAnime = models.ForeignKey(Anime_class, on_delete=models.CASCADE, null=False)
    mAddedDate = models.DateTimeField(null=False)


class Comment_class(models.Model):
    mID = models.BigAutoField(primary_key=True)
    mEpisode = models.ForeignKey(Episode_class, on_delete=models.CASCADE, null=False)
    mUser = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=False)
    mBody = models.TextField(null=False)
    mPostDate = models.DateTimeField(auto_now_add=True)
    mRepliedTo = models.ForeignKey('self', on_delete=models.CASCADE, null=True)
    mRepliedUser = models.CharField(max_length=255, null=True)


class Report_Comment_Class(models.Model):
    mID = models.BigAutoField(primary_key=True)
    mUser = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=False)
    mComment = models.ForeignKey(Comment_class, on_delete=models.CASCADE, null=False)
    mReportDate = models.DateTimeField(auto_now_add=True)


class Apps_class(models.Model):
    mID = models.BigAutoField(primary_key=True)
    mAppVersion = models.CharField(null=False, max_length=255)
    mPlatform = models.CharField(null=False, max_length=255)
    mIsLatestVersion = models.BooleanField(default=True)
    mDownloadURL = models.CharField(null=True, max_length=1500)
