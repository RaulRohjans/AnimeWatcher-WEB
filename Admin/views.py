import datetime

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import logout
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from Content.models import *


# Create your views here.
@staff_member_required
def admin_home_view(request):
    userCount = User.objects.count()
    episodeCount = Episode_class.objects.count()
    animeCount = Anime_class.objects.count()
    commentsCount = Comment_class.objects.count()

    content = {
        'PageTitle': 'Dashboard',
        'userCount': userCount,
        'episodeCount': episodeCount,
        'animeCount': animeCount,
        'commentsCount': commentsCount,
    }
    return render(request, "admin/index.html", content)


@staff_member_required
def redirect_view(request):
    return redirect('admin')


@staff_member_required
def admin_user_create_view(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        chkAdmin = request.POST.get('adminCheck')

        if email and password1 and password2:
            if password2 == password1:
                # Check if the email is already in use
                userObjs = User.objects.all()
                InUse = False
                for obj in userObjs:
                    if obj.email == email:
                        InUse = True

                if not InUse:
                    user = User.objects.create_user(username, email, password1)
                    if first_name:
                        user.first_name = first_name
                    if last_name:
                        user.last_name = last_name
                    if chkAdmin:
                        user.is_staff = True
                        user.is_admin = True
                        user.is_superuser = True
                    user.save()
                    messages.success(request, 'User created successfully!')
                else:
                    messages.error(request, 'That email is already in use!', extra_tags='error')
            else:
                messages.error(request, 'Passwords don\'t match!', extra_tags='error')
        else:
            messages.error(request, 'Please fill all the mandatory fields!', extra_tags='error')

    content = {
        'PageTitle': 'Create User'
    }
    return render(request, "admin/create-user.html", content)


@staff_member_required
def admin_user_edit_view(request):
    searchRes = request.GET.get('s', '')

    if searchRes:
        userObjs = User.objects.filter(username__contains=searchRes).order_by('username')
    else:
        userObjs = User.objects.order_by('username')

    content = {
        'PageTitle': 'All Users',
        'userObjs': userObjs,
    }
    return render(request, "admin/edit-user.html", content)


@staff_member_required
def admin_user_edit_username_view(request, username):
    userObj = ''
    userObjs = User.objects.filter(username=username)
    # Convert objs into obj
    for obj in userObjs:
        userObj = obj

    if request.method == 'POST':
        if request.POST.get("save"):
            first_name = request.POST.get("first_name")
            last_name = request.POST.get("last_name")
            form_username = request.POST.get("username")
            email = request.POST.get("email")
            password1 = request.POST.get("password1")
            password2 = request.POST.get("password2")
            chkAdmin = request.POST.get('adminCheck')

            if form_username and email:
                userObj.username = form_username
                userObj.email = email

                if first_name:
                    userObj.first_name = first_name
                if last_name:
                    userObj.last_name = last_name

                passChange = False
                if password1 or password2:
                    if password2 == password1:
                        userObj.set_password(password1)
                        passChange = True
                    else:
                        messages.error(request, 'Passwords don\'t match!', extra_tags='error')

                if chkAdmin:
                    userObj.is_staff = True
                    userObj.is_admin = True
                    userObj.is_superuser = True

                if request.user == userObj and passChange:
                    logout(request)
                    userObj.save()
                    messages.success(request, 'Account settings saved successfully!')
                    return redirect('login')
                else:
                    userObj.save()
                    messages.success(request, 'Account settings saved successfully!')
            else:
                messages.error(request, 'Please fill all the mandatory fields!', extra_tags='error')

        elif request.POST.get("delete"):
            if request.user == userObj:
                logout(request)
                userObj.delete()
                messages.success(request, 'User deleted successfully!')
                return redirect('login')
            else:
                userObj.delete()
                return redirect('admin-user-all')

    content = {
        'PageTitle': 'Edit - ' + username,
        'userObj': userObj,
    }
    return render(request, "admin/user.html", content)


@staff_member_required
def admin_anime_create_view(request):
    catObjs = Category_class.objects.order_by('mCategoryName')

    if request.method == 'POST':
        nameEN = request.POST.get('nameEn')
        nameJP = request.POST.get('nameJP')
        Desc = request.POST.get('description')
        Cats = request.POST.getlist('categories')
        onGoing = request.POST.get('onGoing')
        thumbnail = request.POST.get('thumbnail')

        if nameEN and Desc and Cats and thumbnail:
            anime = Anime_class(mNameEN=nameEN.lower(), mDescription=Desc,
                                mThumbnail=thumbnail, mEpisodeCount=0)
            if onGoing:
                anime.mOnGoing = True
            else:
                anime.mOnGoing = False

            if nameJP:
                anime.mNameJP = nameJP

            anime.save()
            # Increment category count and add it to the anime
            for cat in Cats:
                category = Category_class.objects.get(mCategoryName=cat)
                category.mAnimeCount = category.mAnimeCount + 1
                category.save()
                anime.mCategories.add(category)

            messages.success(request, 'Anime added successfully!')
        else:
            messages.error(request, 'Please fill all the mandatory fields!', extra_tags='error')

    content = {
        'PageTitle': 'Add Anime',
        'catObjs': catObjs,
    }
    return render(request, "admin/add-anime.html", content)


@staff_member_required
def admin_anime_edit_view(request):
    searchRes = request.GET.get('s', '')

    if searchRes:
        animeObjs = Anime_class.objects.filter(mNameEN__contains=searchRes.lower()).order_by('mNameEN')
    else:
        animeObjs = Anime_class.objects.order_by('mNameEN')

    content = {
        'PageTitle': 'All Animes',
        'animeObjs': animeObjs
    }
    return render(request, "admin/edit-anime.html", content)


@staff_member_required
def admin_anime_edit_id_view(request, id):
    animeObj = Anime_class.objects.get(pk=id)
    catObjs = Category_class.objects.order_by('mCategoryName')
    animeCatObjs = animeObj.mCategories.order_by('mCategoryName')

    if request.method == 'POST':
        if request.POST.get("save"):
            nameJP = request.POST.get('nameJP')
            Desc = request.POST.get('description')
            Cats = request.POST.getlist('categories')
            onGoing = request.POST.get('onGoing')
            thumbnail = request.POST.get('thumbnail')

            if Desc and Cats:
                # Decrement all the categories
                for delCat in animeObj.mCategories.all():
                    delCat.mAnimeCount = delCat.mAnimeCount - 1
                    delCat.save()

                # Remove all the categories from the object
                animeObj.mCategories.clear()

                if nameJP:
                    animeObj.mNameJP = nameJP
                animeObj.mDescription = Desc

                if onGoing:
                    animeObj.mOnGoing = True
                else:
                    animeObj.mOnGoing = False

                animeObj.mThumbnail = thumbnail
                animeObj.save()
                for cat in Cats:
                    category = Category_class.objects.get(mCategoryName=cat)
                    category.mAnimeCount = category.mAnimeCount + 1
                    category.save()
                    animeObj.mCategories.add(category)
                messages.success(request, 'Anime edited successfully!')
            else:
                messages.error(request, 'Please fill all the mandatory fields!', extra_tags='error')

        elif request.POST.get("delete"):
            # decrement anime from counter
            for catobj in animeObj.mCategories.all():
                catobj.mAnimeCount = catobj.mAnimeCount - 1
                catobj.save()

            animeObj.delete()
            return redirect('admin-anime-all')

    content = {
        'PageTitle': 'Edit Anime - ' + id,
        'catObjs': catObjs,
        'animeObj': animeObj,
        'animeCatObjs': animeCatObjs
    }
    return render(request, "admin/anime.html", content)


@staff_member_required
def admin_anime_list_create_view(request):
    userObjs = User.objects.order_by('username')
    animeObjs = Anime_class.objects.order_by('mNameEN')

    if request.method == 'POST':
        user = request.POST.get('user')
        anime = request.POST.get('anime')

        userObjs = User.objects.filter(username=user)
        # Convert objs into obj
        userObj = ''
        for obj in userObjs:
            userObj = obj

        # check if this anime is already added to the user's list
        mylistObjs = MyList_class.objects.all()
        repeated = False
        for obj in mylistObjs:
            if obj.mUser == userObj and obj.mAnime == Anime_class.objects.get(pk=anime):
                repeated = True
                break

        if not repeated:
            mylist = MyList_class(mUser=userObj, mAnime=Anime_class.objects.get(pk=anime), mAddedDate=datetime.datetime.now())
            mylist.save()
            messages.success(request, 'Anime successfully added to ' + user + '\'s list!')
        else:
            messages.error(request, 'This user already has this anime added to the list!', extra_tags='error')

    content = {
        'animeObjs': animeObjs,
        'userObjs': userObjs,
        'PageTitle': 'Add List Item',
    }
    return render(request, "admin/add-mylist.html", content)


@staff_member_required
def admin_anime_list_edit_view(request):
    searchRes = request.GET.get('s', '')

    if searchRes:
        if "@" in searchRes:
            mylistObjs = MyList_class.objects.filter(mUser__email__contains=searchRes.lower()).order_by('mID')
        else:
            mylistObjs = MyList_class.objects.filter(mUser__username__contains=searchRes.lower()).order_by('mID')
    else:
        mylistObjs = MyList_class.objects.order_by('mID')

    content = {
        'PageTitle': 'All MyLists',
        'mylistObjs': mylistObjs
    }
    return render(request, "admin/edit-mylist.html", content)


@staff_member_required
def admin_anime_list_edit_id_view(request, id):
    mylistObj = MyList_class.objects.get(pk=id)
    userObjs = User.objects.order_by('username')
    animeObjs = Anime_class.objects.order_by('mNameEN')

    if request.method == 'POST':
        if request.POST.get("save"):
            user = request.POST.get('user')
            anime = request.POST.get('anime')

            userObjs = User.objects.filter(username=user)
            # Convert objs into obj
            userObj = ''
            for obj in userObjs:
                userObj = obj

            # check if this anime is already added to the user's list
            mylistObjs = MyList_class.objects.all()
            repeated = False
            for obj in mylistObjs:
                if obj.mUser == userObj and obj.mAnime == Anime_class.objects.get(pk=anime):
                    repeated = True
                    break

            if not repeated:
                mylistObj.mUser = userObj
                mylistObj.mAnime = Anime_class.objects.get(pk=anime)
                mylistObj.save()
                messages.success(request, 'Item edited successfully!')
            else:
                messages.error(request, 'This user already has this anime added to the list!', extra_tags='error')

        elif request.POST.get("delete"):
            mylistObj.delete()
            return redirect('admin-anime-list-all')

    content = {
        'PageTitle': 'Edit List Item',
        'mylistObj': mylistObj,
        'userObjs': userObjs,
        'animeObjs': animeObjs
    }
    return render(request, "admin/mylist.html", content)


@staff_member_required
def admin_anime_submitted_view(request):
    searchRes = request.GET.get('s', '')

    if searchRes:
        submittedObjs = SubmitAnime_class.objects.filter(mUsername__contains=searchRes).order_by('-mSubDate')
    else:
        submittedObjs = SubmitAnime_class.objects.order_by('-mSubDate')

    if request.method == 'POST':
        delItems = request.POST.getlist('delete')
        for item in delItems:
            if item != 'delete':
                tempItem = SubmitAnime_class.objects.get(pk=int(item))
                tempItem.delete()

    content = {
        'PageTitle': 'Submitted Animes',
        'submittedObjs': submittedObjs,
    }
    return render(request, "admin/submited-animes.html", content)


@staff_member_required
def admin_category_create_view(request):

    if request.method == 'POST':
        catName = request.POST.get('catName')

        if catName:
            category = Category_class(mCategoryName=catName.lower(), mAnimeCount=0)
            category.save()
            messages.success(request, 'Category added successfully!!')
        else:
            messages.error(request, 'Please fill all the mandatory fields!', extra_tags='error')

    content = {
        'PageTitle': 'Add Category',
    }
    return render(request, "admin/add-category.html", content)


@staff_member_required
def admin_category_edit_view(request):
    searchRes = request.GET.get('s', '')

    if searchRes:
        catObjs = Category_class.objects.filter(mCategoryName__contains=searchRes.lower()).order_by('mCategoryName')
    else:
        catObjs = Category_class.objects.order_by('mCategoryName')

    content = {
        'PageTitle': 'All Categories',
        'catObjs': catObjs
    }
    return render(request, "admin/edit-category.html", content)


@staff_member_required
def admin_category_edit_id_view(request, id):
    catObj = Category_class.objects.get(pk=id)

    if request.method == 'POST':
        if request.POST.get("save"):
            desc = request.POST.get('description')
            thumbnail = request.POST.get('thumbnail')

            if desc:
                catObj.mDescription = desc

            if thumbnail:
                catObj.mPicture = thumbnail
            catObj.save()
            messages.success(request, 'Category edited successfully!')

        elif request.POST.get("delete"):
            catObj.delete()
            return redirect('admin-category-all')

    content = {
        'PageTitle': 'Delete Category - ' + id,
        'catObj': catObj,
    }
    return render(request, "admin/category.html", content)


@staff_member_required
def admin_episode_create_view(request):
    animeObjs = Anime_class.objects.order_by('mNameEN')

    if request.method == 'POST':

        nameEN = request.POST.get('nameEn')
        nameJP = request.POST.get('nameJP')
        length = request.POST.get('length')
        epi = request.POST.get('epi')
        reldate = request.POST.get('reldate')
        reltime = request.POST.get('reltime')
        videoFile = request.POST.get('videoFile')
        anime = request.POST.get('anime')
        selfHosted = request.POST.get('selfHosted')
        thumbnail = request.POST.get('thumbnail')

        if nameEN and length and epi and reldate and videoFile and anime:
            episode = Episode_class(mEpisodeNumber=epi, mNameEN=nameEN.lower(), mViews=0,
                                    mThumbnail=thumbnail, mVideoFileLink=videoFile)

            # add episode to count
            anime = Anime_class.objects.get(pk=anime)
            anime.mEpisodeCount = anime.mEpisodeCount + 1
            anime.save()
            episode.mAnime = anime

            if nameJP:
                episode.mNameJP = nameJP

            # Split Date
            sepDate = reldate.split("-")

            if reltime:
                # Split Time
                sepTime = reltime.split(":")

                episode.mReleaseDate = datetime.datetime(int(sepDate[0]), int(sepDate[1]), int(sepDate[2]),
                                                         int(sepTime[0]), int(sepTime[1]))
            else:
                episode.mReleaseDate = datetime.datetime(int(sepDate[0]), int(sepDate[1]), int(sepDate[2]), 0, 0)

            # split length
            sepLength = length.split(":")
            secsH = int(sepLength[0]) * 3600
            secsM = int(sepLength[1]) * 60
            total = secsH + secsM + int(sepLength[2])
            episode.mLengthSecs = total

            episode.save()
            messages.success(request, 'Episode added successfully!')
        else:
            messages.error(request, 'Please fill all the mandatory fields!', extra_tags='error')

    content = {
        'PageTitle': 'Add Episode',
        'animeObjs': animeObjs,
    }
    return render(request, "admin/add-episode.html", content)


@staff_member_required
def admin_episode_edit_view(request):
    searchRes = request.GET.get('s', '')

    if searchRes:
        epObjs = Episode_class.objects.filter(mNameEN__contains=searchRes.lower()).order_by('mID')
    else:
        epObjs = Episode_class.objects.order_by('mID')

    content = {
        'PageTitle': 'All Episodes',
        'epObjs': epObjs
    }
    return render(request, "admin/edit-episode.html", content)


@staff_member_required
def admin_episode_edit_id_view(request, id):
    episodeObj = Episode_class.objects.get(pk=id)
    animeObjs = Anime_class.objects.order_by('mNameEN')

    # Separate release date and time
    relDate = episodeObj.mReleaseDate.strftime("%Y") + '-' + episodeObj.mReleaseDate.strftime(
        "%m") + '-' + episodeObj.mReleaseDate.strftime("%d")
    relTime = episodeObj.mReleaseDate.strftime("%H:%M")

    # convert length from secs to hh:mm:ss
    length = str(datetime.timedelta(seconds=episodeObj.mLengthSecs))

    if request.method == 'POST':
        if request.POST.get("save"):
            nameEn = request.POST.get('nameEn')
            nameJp = request.POST.get('nameJP')
            form_length = request.POST.get('length')
            epi = request.POST.get('epi')
            form_reldate = request.POST.get('reldate')
            form_reltime = request.POST.get('reltime')
            videoFile = request.POST.get('videoFile')
            anime = request.POST.get('anime')
            selfHosted = request.POST.get('selfHosted')
            thumbnail = request.POST.get('thumbnail')

            if nameEn and form_length and epi and form_reldate and videoFile and anime and thumbnail:
                episodeObj.mEpisodeNumber = epi
                episodeObj.mNameEN = nameEn
                if nameJp:
                    episodeObj.mNameJP = nameJp
                else:
                    episodeObj.mNameJP = None

                # decrement old anime, increment new and add it
                oldAnime = episodeObj.mAnime
                oldAnime.mEpisodeCount = oldAnime.mEpisodeCount - 1
                oldAnime.save()

                newAnime = Anime_class.objects.get(pk=anime)
                newAnime.mEpisodeCount = newAnime.mEpisodeCount + 1
                newAnime.save()
                episodeObj.mAnime = newAnime

                # Split Date
                sepDate = form_reldate.split("-")

                if form_reltime:
                    # Split Time
                    sepTime = form_reltime.split(":")
                    episodeObj.mReleaseDate = datetime.datetime(int(sepDate[0]), int(sepDate[1]), int(sepDate[2]),
                                                                int(sepTime[0]), int(sepTime[1]))
                else:
                    episodeObj.mReleaseDate = datetime.datetime(int(sepDate[0]), int(sepDate[1]), int(sepDate[2]), 0, 0)

                # split length
                sepLength = form_length.split(":")
                secsH = int(sepLength[0]) * 3600
                secsM = int(sepLength[1]) * 60
                total = secsH + secsM + int(sepLength[2])
                episodeObj.mLengthSecs = total

                episodeObj.mThumbnail = thumbnail

                episodeObj.mVideoFileLink = videoFile

                episodeObj.save()
                messages.success(request, 'Episode edited successfully!')
                return redirect('/admin/episode/edit/' + str(id))
            else:
                messages.error(request, 'Please fill all the mandatory fields!', extra_tags='error')

        elif request.POST.get("delete"):
            # decrement episode counter
            animeDel = episodeObj.mAnime
            animeDel.mEpisodeCount = animeDel.mEpisodeCount - 1
            animeDel.save()

            episodeObj.delete()
            return redirect('admin-episode-all')

    content = {
        'PageTitle': 'Edit Episode - ' + str(id),
        'animeObjs': animeObjs,
        'episodeObj': episodeObj,
        'relDate': relDate,
        'relTime': relTime,
        'length': length,
    }
    return render(request, "admin/episode.html", content)


@staff_member_required
def admin_subtitle_create_view(request):
    episodeObjs = Episode_class.objects.order_by('mID')

    content = {
        'PageTitle': 'Add Subtitle',
        'episodeObjs': episodeObjs
    }
    return render(request, "admin/add-subtitle.html", content)


@staff_member_required
def admin_subtitle_edit_view(request):

    content = {
        'PageTitle': 'All Subtitles'
    }
    return render(request, "admin/edit-subtitle.html", content)


@staff_member_required
def admin_subtitle_edit_id_view(request, id):
    episodeObjs = Episode_class.objects.order_by('mID')

    content = {
        'PageTitle': 'Edit Subtitle',
        'episodeObjs': episodeObjs
    }
    return render(request, "admin/subtitle.html", content)


@staff_member_required
def admin_rep_comments_view(request):
    searchRes = request.GET.get('s', '')

    if searchRes:
        repCommentsObjs = Report_Comment_Class.objects.filter(mUser__contains=searchRes).order_by('-mReportDate')
    else:
        repCommentsObjs = Report_Comment_Class.objects.order_by('-mReportDate')

    if request.method == 'POST':
        if request.POST.get('deleteRep'):
            delItems = request.POST.getlist('delete')
            for item in delItems:
                if item != 'delete':
                    tempItem = Report_Comment_Class.objects.get(pk=int(item))
                    tempItem.delete()

        elif request.POST.get('deleteCom'):
            delItems = request.POST.getlist('delete')
            for item in delItems:
                if item != 'delete':
                    tempItem = Report_Comment_Class.objects.get(pk=int(item))
                    tempComment = tempItem.mComment
                    tempComment.delete()


    content = {
        'PageTitle': 'Reported Comments',
        'repCommentsObjs': repCommentsObjs,
    }
    return render(request, "admin/reported-comments.html", content)