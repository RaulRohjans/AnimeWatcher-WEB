import datetime
import os
import urllib.request

import requests
from random import shuffle

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage

from .models import *


def home_view(request):
    objs = Category_class.objects.all()

    LatestEpisodeObjs = Episode_class.objects.order_by('-mReleaseDate')[:32]
    MostViewsEpisodeObjs = Episode_class.objects.order_by('-mViews')[:32]
    RandomEpisodeObjs = list(Episode_class.objects.all()[:32])
    shuffle(RandomEpisodeObjs)

    content = {
        'request': request,
        'pageTitle': 'Home',
        'objs': objs,
        'LatestEpisodeObjs': LatestEpisodeObjs,
        'MostViewsEpisodeObjs': MostViewsEpisodeObjs,
        'RandomEpisodeObjs': RandomEpisodeObjs,
        'qtdAnimeObjs': Episode_class.objects.count()
    }
    return render(request, "content/index.html", content)


def about_us_view(request):
    content = {
        'request': request,
        'pageTitle': 'About us'
    }
    return render(request, "content/about-us.html", content)


def donate_view(request):
    content = {
        'request': request,
        'pageTitle': 'Donate'
    }
    return render(request, "content/donate.html", content)


def disclaimer_view(request):
    content = {
        'request': request,
        'pageTitle': 'Disclaimer'
    }
    return render(request, "content/disclaimer.html", content)


def privacy_policy_view(request):
    content = {
        'request': request,
        'pageTitle': 'Privacy Policy'
    }
    return render(request, "content/privacy-policy.html", content)


def anime_list_view(request):
    searchRes = request.GET.get('s', '')
    pageNumber = request.GET.get('page', '')
    IsSearch = False
    p = ''

    if not pageNumber.isdigit() or pageNumber is None or pageNumber == "":
        pageNumber = 1

    if searchRes:
        IsSearch = True

        objs = Anime_class.objects.filter(mNameEN__contains=searchRes.lower()).order_by('mNameEN')[:50]
        qtdAnimes = Anime_class.objects.filter(mNameEN__contains=searchRes.lower()).count()
    else:
        IsSearch = False

        objs = Anime_class.objects.order_by('mNameEN')
        p = Paginator(objs, 50)
        try:
            objs = p.page(pageNumber)
        except EmptyPage:
            objs = p.page(1)

        qtdAnimes = Anime_class.objects.count()

    EpisodeObjs = Episode_class.objects.all()

    content = {
        'request': request,
        'pageTitle': 'Anime List',
        'objs': objs,
        'qtdAnimes': qtdAnimes,
        'EpisodeObjs': EpisodeObjs,
        'IsSearch': IsSearch,
        'p': p
    }
    return render(request, "content/animes.html", content)


def anime_view(request, AnimeID):
    objAnime = Anime_class.objects.get(pk=AnimeID)
    EpObjs = Episode_class.objects.order_by('mEpisodeNumber')

    isInList = False
    # Check if the anime is already added to the list
    objs = MyList_class.objects.all()
    for obj in objs:
        if obj.mAnime == objAnime and obj.mUser == request.user:
            isInList = True
            break

    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('login')
        else:
            if not isInList:
                myListObj = MyList_class(mAnime=objAnime, mUser=request.user, mAddedDate=datetime.date.today())
                myListObj.save()
                messages.success(request, 'Anime added to your list successfully!')
                return redirect('/anime/' + AnimeID)
            else:
                obj.delete()
                messages.success(request, 'Anime removed from your list successfully!')
                isInList = False

    content = {
        'request': request,
        'pageTitle': objAnime.mNameEN,
        'objAnime': objAnime,
        'EpObjs': EpObjs,
        'isInList': isInList,
    }
    return render(request, "content/anime.html", content)


def play_anime_view(request, AnimeID, EpisodeID):
    objAnime = Anime_class.objects.get(pk=AnimeID)
    objEpisode = Episode_class.objects.get(pk=EpisodeID)
    objsEpisode = Episode_class.objects.order_by('mEpisodeNumber')
    commentObjs = Comment_class.objects.filter(mEpisode=objEpisode).order_by('mPostDate')

    # Add a view to the anime
    objEpisode.mViews = objEpisode.mViews + 1
    objEpisode.save()

    # Get mp4 link
    video1080p = objEpisode.mVideoFileLink
    if objEpisode.mVCDN:
        episode_file_link = objEpisode.mVideoFileLink
        if objEpisode.mVideoFileLink[-1] == '/':
            episode_file_link = objEpisode.mVideoFileLink[:-1]

        vcdn_url = "https://vcdn2.space/api/source/" + episode_file_link.rsplit('/', 1)[-1]
        vcdn_payload = "r=&d=vcdn2.space"
        vcdn_headers = {
            'authority': 'vcdn2.space',
            'sec-ch-ua': '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
            'accept': '*/*',
            'x-requested-with': 'XMLHttpRequest',
            'sec-ch-ua-mobile': '?0',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'origin': 'https://vcdn2.space',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': episode_file_link,
            'accept-language': 'en-US,en;q=0.9'
        }

        vcdn_response = requests.request("POST", vcdn_url, headers=vcdn_headers, data=vcdn_payload)
        vcdn_data = vcdn_response.json()

        vcdn_redirect_link = None
        for d in vcdn_data['data']:
            vcdn_redirect_link = d['file']

        if vcdn_redirect_link is not None:
            vcdn_r = requests.get(vcdn_redirect_link, stream=True)
            video1080p = vcdn_r.url

    # Get previous and next episode
    prevEp = ''
    nextEp = ''
    episodes = Episode_class.objects.all()
    for obj in episodes:
        if obj.mAnime == objAnime and obj.mEpisodeNumber == objEpisode.mEpisodeNumber + 1:
            nextEp = obj
        elif obj.mAnime == objAnime and obj.mEpisodeNumber == objEpisode.mEpisodeNumber - 1:
            prevEp = obj

    if request.method == 'POST':
        if request.user.is_authenticated:
            if request.POST.get('post') == 'new':
                commentText = request.POST.get('commentText')
                if commentText:
                    newComment = Comment_class(mEpisode=objEpisode, mUser=request.user, mBody=commentText)
                    newComment.save()
            elif request.POST.get('post') is not None:
                postReplied = request.POST.get('post')
                commentText = request.POST.get('commentText')
                postReplied = postReplied.split(",")
                if commentText:
                    comment = Comment_class(mEpisode=objEpisode, mUser=request.user, mBody=commentText,
                                            mRepliedTo=Comment_class.objects.get(pk=postReplied[0]),
                                            mRepliedUser='@' + postReplied[1])
                    comment.save()
        else:
            return redirect('login')

    content = {
        'request': request,
        'pageTitle': objAnime.mNameEN + ' Episode ' + str(objEpisode.mEpisodeNumber),
        'objAnime': objAnime,
        'objEpisode': objEpisode,
        'prevEp': prevEp,
        'nextEp': nextEp,
        'commentObjs': commentObjs,
        'objsEpisode': objsEpisode
    }
    return render(request, "content/anime-player.html", content)


@login_required(login_url='login')
def report_comment_view(request, id):
    comment = Comment_class.objects.get(pk=id)
    report = Report_Comment_Class(mUser=request.user, mComment=comment)
    report.save()
    return redirect('/anime/' + comment.mEpisode.mAnime.mNameEN + '/' + str(comment.mEpisode.mID))


@login_required(login_url='login')
def delete_comment_view(request, id):
    comment = Comment_class.objects.get(pk=id)
    animeName = comment.mEpisode.mAnime.mNameEN
    episodeID = str(comment.mEpisode.mID)
    comment.mBody = "deleted"
    comment.save()
    return redirect('/anime/' + animeName + '/' + episodeID)


@login_required(login_url='login')
def my_list_view(request):
    myListCount = MyList_class.objects.filter(mUser=request.user).count()
    AnimeObjs = MyList_class.objects.filter(mUser=request.user).values_list('mAnime', flat=True)
    pageNumber = request.GET.get('page', '')
    p = ''

    # Gather all the animes in the MyList
    animes = []
    for animeObj in Anime_class.objects.all():
        for InnerAnimeObj in AnimeObjs:
            if InnerAnimeObj == animeObj.mNameEN:
                animes.append(animeObj)

    if not pageNumber.isdigit() or pageNumber is None or pageNumber == "":
        pageNumber = 1

    p = Paginator(animes, 50)
    try:
        objs = p.page(pageNumber)
    except EmptyPage:
        objs = p.page(1)

    content = {
        'request': request,
        'pageTitle': 'My List',
        'objs': objs,
        'qtdAnimes': myListCount,
        'p': p
    }
    return render(request, "content/my-list.html", content)


def submit_anime_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        anime = request.POST.get('anime')
        description = request.POST.get('description')

        if username and email and anime:
            obj = SubmitAnime_class(mAnimeName=anime, mUserEmail=email, mUsername=username, mMoreInfo=description,
                                    mSubDate=datetime.datetime.now())
            obj.save()
            messages.success(request, 'Your request was submitted successfully!')
        else:
            messages.error(request, 'Please fill in all the mandatory fields!', extra_tags='error')

    content = {
        'request': request,
        'pageTitle': 'Submit Anime'
    }
    return render(request, "content/submit-anime.html", content)


def category_list_view(request):
    objs = Category_class.objects.all()
    anime_objs = Anime_class.objects.all()
    qtdCat = Category_class.objects.count()

    content = {
        'objs': objs,
        'request': request,
        'pageTitle': 'Categories',
        'qtdCat': qtdCat,
        'anime_objs': anime_objs
    }
    return render(request, "content/categories.html", content)


def category_view(request, id):
    CategoryObj = Category_class.objects.get(mCategoryName=id)
    AnimeObjs = Anime_class.objects.filter(mCategories=CategoryObj).order_by('mNameEN')
    pageNumber = request.GET.get('page', '')
    p = ''

    if not pageNumber.isdigit() or pageNumber is None or pageNumber == "":
        pageNumber = 1

    p = Paginator(AnimeObjs, 50)
    try:
        objs = p.page(pageNumber)
    except EmptyPage:
        objs = p.page(1)

    # find anime count with that category
    qtdAnimes = 0
    for AnimeObj in AnimeObjs:
        for CatObj in AnimeObj.mCategories.all():
            if CatObj.mCategoryName == CategoryObj.mCategoryName:
                qtdAnimes = qtdAnimes + 1

                break

    content = {
        'objs': objs,
        'request': request,
        'pageTitle': id,
        'qtdAnimes': qtdAnimes,
        'p': p
    }
    return render(request, 'content/category.html', content)
