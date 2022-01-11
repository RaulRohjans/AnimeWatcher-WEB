import datetime
import threading
from django.conf import settings

import requests
from random import shuffle

from django.contrib.auth import authenticate

from Content.models import *
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import EmailMessage
from django.contrib.auth.hashers import check_password
from django.contrib.sites.shortcuts import get_current_site
from django.core.paginator import Paginator, EmptyPage
from django.db.models import Q
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.html import strip_tags
from django.utils.http import urlsafe_base64_encode

from .serializers import *
from .utils import token_generator

from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.authtoken.models import Token


# Methods
class EmailThread(threading.Thread):

    # Constructor
    def __init__(self, email_message):
        self.email_message = email_message
        threading.Thread.__init__(self)

    def run(self):
        self.email_message.send()


# Create your views here.
@api_view(['GET'])
def ping_api(request):
    response_data = {
        'Status': 'success'
    }
    return Response(response_data)


@api_view(['POST'])
def check_app_updates(request):
    if request.method == 'POST':
        data = request.data
        try:
            if 'mAppVersion' in data and 'mPlatform' in data:
                app = Apps_class.objects.filter(mPlatform=data['mPlatform'].lower()).filter(mAppVersion=data['mAppVersion'])
                if len(app) > 0:
                    if app[0].mIsLatestVersion:
                        response_data = {
                            'Status': 'success'
                        }
                        return Response(response_data, status=200)
                    else:
                        new_app = Apps_class.objects.filter(mPlatform=data['mPlatform'].lower()).filter(mIsLatestVersion=True)
                        if len(new_app) > 0:
                            response_data = {
                                'Status': 'update',
                                'Version': new_app[0].mAppVersion,
                                'Download': new_app[0].mDownloadURL
                            }
                            return Response(response_data, status=200)
                        else:
                            response_data = {
                                'Status': 'success'
                            }
                            return Response(response_data, status=200)
                else:
                    response_data = {
                        'Status': 'error',
                        'Error': 'app version not found'
                    }
                    return Response(response_data, status=404)
            else:
                response_data = {
                    'Status': 'error',
                    'Error': 'invalid post data'
                }
                return Response(response_data, status=400)
        except Exception as e:
            response_data = {
                'Status': 'error',
                'Error': str(e)
            }
            return Response(response_data, status=400)


@api_view(['POST'])
def register_new_user(request):
    if request.method == 'POST':
        data = request.data
        if 'username' in data and 'password' in data and 'email' in data:
            if User.objects.filter(username=data['username']).exists() is False:
                if User.objects.filter(email=data['email']).exists() is False:
                    user = User.objects.create_user(data['username'], data['email'], data['password'])
                    if 'first_name' in data:
                        user.first_name = data['first_name']
                    if 'last_name' in data:
                        user.last_name = data['last_name']
                    user.is_active = False
                    user.save()

                    # Send Email
                    # Send a confirmation email to the user
                    domain = get_current_site(request).domain
                    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
                    link = reverse('account-activation',
                                   kwargs={'uidb64': uidb64, 'token': token_generator.make_token(user)})
                    activate_url = request.scheme + '://' + domain + link

                    email_subject = 'Please activate your account!'
                    message = render_to_string('authentication/email-activate-account.html',
                                               {
                                                   'user': user,
                                                   'protocol': request.scheme + '://',
                                                   'domain': get_current_site(request).domain,
                                                   'uid': urlsafe_base64_encode(
                                                       force_bytes(user.pk)),
                                                   'token': token_generator.make_token(user)
                                               })
                    email = EmailMessage(
                        email_subject,
                        message,
                        settings.EMAIL_HOST_USER,
                        [data['email']]
                    )
                    email.content_subtype = 'html'
                    EmailThread(email).start()

                    response_data = {
                        'Status': 'success'
                    }
                    return Response(response_data, status=200)
                else:
                    response_data = {
                        'Status': 'error',
                        'Error': 'email is taken'
                    }
                    return Response(response_data, status=401)
            else:
                response_data = {
                    'Status': 'error',
                    'Error': 'username is taken'
                }
                return Response(response_data, status=401)
        else:
            response_data = {
                'Status': 'error',
                'Error': 'missing form data'
            }
            return Response(response_data, status=406)


@api_view(['POST'])
def authenticate_user(request):
    if request.method == 'POST':
        data = request.data
        if User.objects.filter(username=data['username']).exists():
            user = User.objects.get(username=data['username'])
            if user.check_password(data['password']):
                if user.is_active:
                    # Check if there is a token for this user
                    try:
                        tokenObj = Token.objects.get(user_id=user.pk)
                        if tokenObj is not None:
                            token_key = tokenObj.key
                        else:
                            token = Token.objects.create(user=user)
                            token_key = token.key
                    except Exception:
                        token = Token.objects.create(user=user)
                        token_key = token.key

                    # Update last login
                    user.last_login = datetime.datetime.now()
                    user.save()

                    response_data = {
                        'Status': 'Authenticated',
                        'Token': token_key,
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'password': user.password,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'is_superuser': user.is_superuser,
                        'is_staff': user.is_staff,
                        'is_active': user.is_active,
                        'last_login': user.last_login,
                        'date_joined': user.date_joined
                    }
                    return Response(response_data)
                else:
                    response_data = {
                        'Status': 'error',
                        'Error': 'Your account is not active!'
                    }
                    return Response(response_data, status=403)
            else:
                response_data = {
                    'Status': 'error',
                    'Error': 'Invalid username or password!'
                }
                return Response(response_data, status=404)
        else:
            response_data = {
                'Status': 'error',
                'Error': 'Invalid username or password!'
            }
            return Response(response_data, status=404)


@api_view(['POST'])
def check_token(request):
    if request.method == 'POST':
        data = request.data
        try:
            token = Token.objects.get(key=data['Token'])
            if token is not None:
                response_data = {
                    'Status': 'success'
                }
                return Response(response_data)
            else:
                response_data = {
                    'Status': 'error',
                    'Error': 'Invalid Token'
                }
                return Response(response_data, status=404)

        except Exception:
            response_data = {
                'Status': 'error',
                'Error': 'Invalid Token'
            }
            return Response(response_data, status=404)


@api_view(['POST'])
def logout_user(request):
    if request.method == 'POST':
        data = request.data
        try:
            token = Token.objects.get(key=data['Token'])
            if token is not None:
                user = User.objects.get(pk=token.user_id)
                if user is not None:
                    token.delete()
                    response_data = {
                        'Status': 'success'
                    }
                    return Response(response_data)
                else:
                    response_data = {
                        'Status': 'error',
                        'Error': 'User non existent'
                    }
                    return Response(response_data, status=404)
            else:
                response_data = {
                    'Status': 'error',
                    'Error': 'Invalid Token'
                }
                return Response(response_data, status=404)
        except Token.doesNotExist:
            response_data = {
                'Status': 'error',
                'Error': 'Invalid Token'
            }
            return Response(response_data, status=404)


@api_view(['POST'])
def get_user_data(request):
    if request.method == 'POST':
        data = request.data
        try:
            token = Token.objects.get(key=data['Token'])
            if token is not None:
                user = User.objects.get(pk=token.user_id)
                if user is not None:
                    serializer = UserSerializer(user)
                    return Response(serializer.data)
                else:
                    response_data = {
                        'Status': 'error',
                        'Error': 'Invalid Token'
                    }
                    return Response(response_data, status=404)
            else:
                response_data = {
                    'Status': 'error',
                    'Error': 'Invalid Token'
                }
                return Response(response_data, status=404)
        except Exception:
            response_data = {
                'Status': 'error',
                'Error': 'Invalid Token'
            }
            return Response(response_data, status=404)


@api_view(['POST'])
def settings_change_user(request):
    if request.method == 'POST':
        data = request.data
        try:
            token = Token.objects.get(key=data['Token'])
            if token is not None:
                if 'username' in data and 'first_name' in data and 'last_name' in data:
                    user = User.objects.get(pk=token.user_id)
                    if user is not None:
                        user.username = data['username']
                        user.first_name = data['first_name']
                        user.last_name = data['last_name']
                        user.save()
                        response_data = {
                            'Status': 'success'
                        }
                        return Response(response_data, status=200)
                    else:
                        response_data = {
                            'Status': 'error',
                            'Error': 'Invalid Token'
                        }
                        return Response(response_data, status=404)
                else:
                    response_data = {
                        'Status': 'error',
                        'Error': 'Invalid Fields'
                    }
                    return Response(response_data, status=404)
            else:
                response_data = {
                    'Status': 'error',
                    'Error': 'Invalid Token'
                }
                return Response(response_data, status=404)

        except Exception:
            response_data = {
                'Status': 'error',
                'Error': 'Invalid Token'
            }
            return Response(response_data, status=404)


@api_view(['POST'])
def settings_change_email(request):
    if request.method == 'POST':
        data = request.data
        try:
            token = Token.objects.get(key=data['Token'])
            if token is not None:
                if 'email' in data:
                    if User.objects.filter(email=data['email']).exists() is False:
                        user = User.objects.get(pk=token.user_id)
                        if user is not None:
                            user.email = data['email']
                            user.save()
                            response_data = {
                                'Status': 'success'
                            }
                            return Response(response_data, status=200)
                        else:
                            response_data = {
                                'Status': 'error',
                                'Error': 'Invalid Token'
                            }
                            return Response(response_data, status=404)
                    else:
                        response_data = {
                            'Status': 'error',
                            'Error': 'email in use'
                        }
                        return Response(response_data, status=403)
                else:
                    response_data = {
                        'Status': 'error',
                        'Error': 'Invalid Fields'
                    }
                    return Response(response_data, status=404)
            else:
                response_data = {
                    'Status': 'error',
                    'Error': 'Invalid Token'
                }
                return Response(response_data, status=404)

        except Exception:
            response_data = {
                'Status': 'error',
                'Error': 'Invalid Token'
            }
            return Response(response_data, status=404)


@api_view(['POST'])
def settings_change_password(request):
    if request.method == 'POST':
        data = request.data
        try:
            token = Token.objects.get(key=data['Token'])
            if token is not None:
                if 'old_password' in data and 'new_password' in data:
                    user = User.objects.get(pk=token.user_id)
                    if user is not None:
                        check = check_password(data['old_password'], user.password)
                        if check:
                            user.set_password(data['new_password'])
                            user.save()
                            response_data = {
                                'Status': 'success'
                            }
                            return Response(response_data, status=200)
                        else:
                            response_data = {
                                'Status': 'error',
                                'Error': 'passwords dont match'
                            }
                            return Response(response_data, status=200)
                    else:
                        response_data = {
                            'Status': 'error',
                            'Error': 'Invalid Token'
                        }
                        return Response(response_data, status=404)
                else:
                    response_data = {
                        'Status': 'error',
                        'Error': 'Invalid Fields'
                    }
                    return Response(response_data, status=404)
            else:
                response_data = {
                    'Status': 'error',
                    'Error': 'Invalid Token'
                }
                return Response(response_data, status=404)

        except Exception:
            response_data = {
                'Status': 'error',
                'Error': 'Invalid Token'
            }
            return Response(response_data, status=404)


@api_view(['POST'])
def user_recover_password(request):
    if request.method == 'POST':
        data = request.data
        try:
            if 'email' in data:
                user = User.objects.filter(email=data['email'])
                if user.exists():
                    email_subject = 'Reset your Password'
                    message = render_to_string('authentication/email-forgot-password.html',
                                               {
                                                   'protocol': request.scheme + '://',
                                                   'domain': get_current_site(request).domain,
                                                   'uid': urlsafe_base64_encode(force_bytes(user[0].pk)),
                                                   'token': PasswordResetTokenGenerator().make_token(user[0])
                                               })
                    message_text = strip_tags(message)
                    email = EmailMessage(
                        email_subject,
                        message,
                        settings.EMAIL_HOST_USER,
                        [data['email']],
                    )
                    email.content_subtype = 'html'
                    EmailThread(email).start()

                response_data = {
                    'Status': 'success'
                }
                return Response(response_data, status=200)
            else:
                response_data = {
                    'Status': 'error',
                    'Error': 'Invalid Fields'
                }
                return Response(response_data, status=404)

        except Exception as e:
            response_data = {
                'Status': 'error',
                'Error': 'Exception ' + str(e)
            }
            return Response(response_data, status=404)


@api_view(['POST'])
def submit_anime(request):
    if request.method == 'POST':
        serializer = SubmitAnimeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            response_data = {
                'Status': 'Success'
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        else:
            response_data = {
                'Status': 'error',
                'Error': 'Data is Invalid'
            }
            return Response(response_data)


@api_view(['GET'])
def get_all_anime(request):
    if request.method == 'GET':
        pageNumber = request.GET.get('p', '')
        itemsPerPage = request.GET.get('count', '')

        if not pageNumber.isdigit() or pageNumber is None or pageNumber == "":
            pageNumber = 1

        if not itemsPerPage.isdigit() or itemsPerPage is None or itemsPerPage == "":
            itemsPerPage = 30

        animeObjs = Anime_class.objects.order_by('mNameEN')
        p = Paginator(animeObjs, itemsPerPage)

        try:
            objs = p.page(pageNumber)
            serializer = AnimeSerializer(objs, many=True)
            return Response(serializer.data)
        except EmptyPage:
            response_data = {
                'Status': 'error',
                'Error': 'no more pages'
            }
            return Response(response_data, status=404)


@api_view(['POST'])
def get_search_anime(request):
    if request.method == 'POST':
        data = request.data
        if "Keywords" in data:
            ENobjs = Anime_class.objects.filter(mNameEN__contains=data["Keywords"].lower())
            JPobjs = Anime_class.objects.filter(mNameJP__contains=data["Keywords"].lower())

            animeObjs = JPobjs | ENobjs
            if animeObjs.count() > 0:
                serializer = AnimeSerializer(animeObjs[:20], many=True)
                return Response(serializer.data)
            else:
                response_data = {
                    'Status': 'error',
                    'Error': 'No items to show'
                }
                return Response(response_data, status=404)
        else:
            response_data = {
                'Status': 'error',
                'Error': 'Invalid Post Data'
            }
            return Response(response_data, status=404)


@api_view(['POST'])
def get_mylist_anime(request):
    if request.method == 'POST':
        data = request.data
        try:
            token = Token.objects.get(pk=data['Token'])
            user = User.objects.get(pk=token.user_id)

            if user is not None:
                mylistObjs = MyList_class.objects.filter(mUser=user).order_by('-mAddedDate')
                if mylistObjs.count() > 0:
                    animes = []
                    for mylist in mylistObjs:
                        animes.append(Anime_class.objects.get(pk=mylist.mAnime.mNameEN))

                    pageNumber = request.GET.get('p', '')
                    itemsPerPage = request.GET.get('count', '')

                    if not pageNumber.isdigit() or pageNumber is None or pageNumber == "":
                        pageNumber = 1

                    if not itemsPerPage.isdigit() or itemsPerPage is None or itemsPerPage == "":
                        itemsPerPage = 30

                    p = Paginator(animes, itemsPerPage)
                    try:
                        objs = p.page(pageNumber)
                        serializer = AnimeSerializer(objs, many=True)
                        return Response(serializer.data)
                    except EmptyPage:
                        response_data = {
                            'Status': 'error',
                            'Error': 'no more pages'
                        }
                        return Response(response_data, status=404)
                else:
                    response_data = {
                        'Status': 'error',
                        'Error': 'No items to show'
                    }
                    return Response(response_data, status=404)
            else:
                response_data = {
                    'Status': 'error',
                    'Error': 'Invalid Token'
                }
                return Response(response_data, status=500)
        except Exception as e:
            response_data = {
                'Status': 'error',
                'Error': 'exception - ' + str(e)
            }
            return Response(response_data, status=500)


@api_view(['POST'])
def add_mylist(request):
    if request.method == 'POST':
        data = request.data
        try:
            token = Token.objects.get(pk=data['Token'])
            user = User.objects.get(pk=token.user_id)
            if token is not None and user is not None:
                if 'mNameEN' in data:
                    anime = Anime_class.objects.get(mNameEN=data['mNameEN'])

                    if anime is not None:
                        mylist = MyList_class(mAnime=anime, mUser=user, mAddedDate=datetime.date.today())
                        mylist.save()
                        response_data = {
                            'Status': 'Success'
                        }
                        return Response(response_data)
                    else:
                        response_data = {
                            'Status': 'error',
                            'Error': 'Invalid Anime'
                        }
                        return Response(response_data, status=500)
                else:
                    response_data = {
                        'Status': 'error',
                        'Error': 'Invalid Post Data'
                    }
                    return Response(response_data, status=500)
            else:
                response_data = {
                    'Status': 'error',
                    'Error': 'Invalid Token'
                }
                return Response(response_data, status=500)
        except Exception:
            response_data = {
                'Status': 'error',
                'Error': 'Exception has occurred'
            }
            return Response(response_data, status=500)


@api_view(['POST'])
def remove_mylist(request):
    if request.method == 'POST':
        data = request.data
        try:
            token = Token.objects.get(pk=data['Token'])
            user = User.objects.get(pk=token.user_id)
            if token is not None and user is not None:
                if 'mNameEN' in data:
                    anime = Anime_class.objects.get(mNameEN=data['mNameEN'])

                    if anime is not None:
                        MyList_class.objects.filter(mUser=user).filter(mAnime=anime).delete()
                        response_data = {
                            'Status': 'Success'
                        }
                        return Response(response_data)
                    else:
                        response_data = {
                            'Status': 'error',
                            'Error': 'Invalid Anime'
                        }
                        return Response(response_data, status=500)
                else:
                    response_data = {
                        'Status': 'error',
                        'Error': 'Invalid Post Data'
                    }
                    return Response(response_data, status=500)
            else:
                response_data = {
                    'Status': 'error',
                    'Error': 'Invalid Token'
                }
                return Response(response_data, status=500)
        except Exception:
            response_data = {
                'Status': 'error',
                'Error': 'Exception has occurred'
            }
            return Response(response_data, status=500)


@api_view(['POST'])
def check_mylist(request):
    if request.method == 'POST':
        data = request.data
        try:
            token = Token.objects.get(pk=data['Token'])
            user = User.objects.get(pk=token.user_id)
            if token is not None and user is not None:
                if 'mNameEN' in data:
                    anime = Anime_class.objects.get(mNameEN=data['mNameEN'])

                    if anime is not None:
                        if MyList_class.objects.filter(mUser=user).filter(mAnime=anime).count() > 0:
                            response_data = {
                                'Added': True
                            }
                        else:
                            response_data = {
                                'Added': False
                            }
                        return Response(response_data)
                    else:
                        response_data = {
                            'Status': 'error',
                            'Error': 'Invalid Anime'
                        }
                        return Response(response_data, status=500)
                else:
                    response_data = {
                        'Status': 'error',
                        'Error': 'Invalid Post Data'
                    }
                    return Response(response_data, status=500)
            else:
                response_data = {
                    'Status': 'error',
                    'Error': 'Invalid Token'
                }
                return Response(response_data, status=500)
        except Exception:
            response_data = {
                'Status': 'error',
                'Error': 'Exception has occurred'
            }
            return Response(response_data, status=500)


@api_view(['GET'])
def get_string_cats(request):
    if request.method == 'GET':
        catObjs = Category_class.objects.order_by('mCategoryName')
        serializer = CategoryNameSerializer(catObjs, many=True)
        return Response(serializer.data)


@api_view(['POST'])
def get_category_anime(request):
    if request.method == 'POST':
        data = request.data
        if "mCategoryName" in data:
            animeObjs = Anime_class.objects.filter(
                mCategories__mCategoryName__contains=data["mCategoryName"].lower()).order_by('mNameEN')

            if animeObjs.count() > 0:
                pageNumber = request.GET.get('p', '')
                itemsPerPage = request.GET.get('count', '')

                if not pageNumber.isdigit() or pageNumber is None or pageNumber == "":
                    pageNumber = 1

                if not itemsPerPage.isdigit() or itemsPerPage is None or itemsPerPage == "":
                    itemsPerPage = 30

                p = Paginator(animeObjs, itemsPerPage)

                try:
                    objs = p.page(pageNumber)
                    serializer = AnimeSerializer(objs, many=True)
                    return Response(serializer.data)
                except EmptyPage:
                    response_data = {
                        'Status': 'error',
                        'Error': 'no more pages'
                    }
                    return Response(response_data, status=404)
            else:
                response_data = {
                    'Status': 'error',
                    'Error': 'No items to show'
                }
                return Response(response_data, status=404)
        else:
            response_data = {
                'Status': 'error',
                'Error': 'Invalid Post Data'
            }
            return Response(response_data, status=403)


@api_view(['POST'])
def get_episodes(request):
    if request.method == 'POST':
        data = request.data
        if 'mNameEN' in data:
            anime = Anime_class.objects.get(mNameEN=data["mNameEN"].lower())
            episodeObjs = Episode_class.objects.filter(mAnime=anime).order_by('mEpisodeNumber')

            if episodeObjs.count() > 0:
                serializer = EpisodeSerializer(episodeObjs, many=True)
                return Response(serializer.data)
            else:
                response_data = {
                    'Status': 'error',
                    'Error': 'No items to show'
                }
                return Response(response_data, status=404)
        else:
            response_data = {
                'Status': 'error',
                'Error': 'Invalid Post Data'
            }
            return Response(response_data, status=404)


@api_view(['GET'])
def get_episodes_latest(request):
    if request.method == 'GET':
        episodeObjs = Episode_class.objects.order_by('-mReleaseDate')[:30]

        if episodeObjs.count() > 0:
            serializer = EpisodeSerializer(episodeObjs, many=True)
            return Response(serializer.data)
        else:
            response_data = {
                'Status': 'error',
                'Error': 'No items to show'
            }
            return Response(response_data, status=404)


@api_view(['GET'])
def get_episodes_most_views(request):
    if request.method == 'GET':
        episodeObjs = Episode_class.objects.order_by('-mViews')[:30]

        if episodeObjs.count() > 0:
            serializer = EpisodeSerializer(episodeObjs, many=True)
            return Response(serializer.data)
        else:
            response_data = {
                'Status': 'error',
                'Error': 'No items to show'
            }
            return Response(response_data, status=404)


@api_view(['GET'])
def get_episodes_random(request):
    if request.method == 'GET':
        EpisodeObjs = Episode_class.objects.all()
        RandomEpisodeObjs = list(EpisodeObjs)
        shuffle(RandomEpisodeObjs)

        if EpisodeObjs.count() > 0:
            serializer = EpisodeSerializer(RandomEpisodeObjs[:30], many=True)
            return Response(serializer.data)
        else:
            response_data = {
                'Status': 'error',
                'Error': 'No items to show'
            }
            return Response(response_data, status=404)


@api_view(['POST'])
def get_episode(request):
    if request.method == 'POST':
        data = request.data
        if "mID" in data:
            episodeObj = Episode_class.objects.get(mID=data["mID"])

            if episodeObj is not None:
                serializer = EpisodeSerializer(episodeObj)
                return Response(serializer.data)
            else:
                response_data = {
                    'Status': 'error',
                    'Error': 'No items to show'
                }
                return Response(response_data, status=404)
        else:
            response_data = {
                'Status': 'error',
                'Error': 'Invalid Post Data'
            }
            return Response(response_data, status=404)


@api_view(['POST'])
def get_episode_next(request):
    if request.method == 'POST':
        data = request.data
        if "mID" in data:
            episodeObj = Episode_class.objects.get(mID=data["mID"])

            if episodeObj is not None:
                eps = Episode_class.objects.filter(mAnime__mNameEN=episodeObj.mAnime.mNameEN, mEpisodeNumber=episodeObj.mEpisodeNumber + 1, mIsSpecial=episodeObj.mIsSpecial)

                if eps.count() > 0:
                    serializer = EpisodeSerializer(eps[0])
                    return Response(serializer.data)
                else:
                    response_data = {
                        'Status': 'error',
                        'Error': 'No next EP'
                    }
                    return Response(response_data, status=404)
            else:
                response_data = {
                    'Status': 'error',
                    'Error': 'Post episode does not exist'
                }
                return Response(response_data, status=404)
        else:
            response_data = {
                'Status': 'error',
                'Error': 'Invalid Post Data'
            }
            return Response(response_data, status=404)


@api_view(['POST'])
def get_anime_thumbnail(request):
    if request.method == 'POST':
        data = request.data
        if "mNameEN" in data:
            animeObj = Anime_class.objects.get(mNameEN=data["mNameEN"])

            if animeObj is not None:
                response_data = {
                    'mThumbnail': animeObj.mThumbnail
                }
                return Response(response_data)
            else:
                response_data = {
                    'Status': 'error',
                    'Error': 'No items to show'
                }
                return Response(response_data, status=404)
        else:
            response_data = {
                'Status': 'error',
                'Error': 'Invalid Post Data'
            }
            return Response(response_data, status=404)


@api_view(['POST'])
def episode_add_view(request):
    if request.method == 'POST':
        data = request.data
        if "mID" in data:
            episode = Episode_class.objects.get(pk=data["mID"])

            if episode is not None:
                episode.mViews = episode.mViews + 1
                episode.save()

                response_data = {
                    'Status': 'Success'
                }
                return Response(response_data)
            else:
                response_data = {
                    'Status': 'error',
                    'Error': 'Invalid Post Data'
                }
                return Response(response_data)
        else:
            response_data = {
                'Status': 'error',
                'Error': 'Invalid Post Data'
            }
            return Response(response_data, status=404)


@api_view(['GET'])
def vcdn_url_post(request):
    if request.method == 'GET':
        data = request.query_params.get("vcdn")

        if data is not None:
            if request.META['HTTP_USER_AGENT'] is not None:
                # Get mp4 link
                vcdn_url = "https://vcdn2.space/api/source/" + data
                vcdn_payload = "r=&d=vcdn2.space"
                vcdn_headers = {
                    'authority': 'vcdn2.space',
                    'accept': '*/*',
                    'x-requested-with': 'XMLHttpRequest',
                    'user-agent': request.META['HTTP_USER_AGENT'],
                    'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
                    'origin': 'https://vcdn2.space',
                    'sec-fetch-site': 'same-origin',
                    'sec-fetch-mode': 'cors',
                    'sec-fetch-dest': 'empty',
                    'referer': "https://vcdn2.space/v/" + data,
                    'accept-language': 'en-US,en;q=0.9'
                }

                vcdn_response = requests.request("POST", vcdn_url, headers=vcdn_headers, data=vcdn_payload)
                vcdn_data = vcdn_response.json()

                vcdn_redirect_link = None
                for d in vcdn_data['data']:
                    vcdn_redirect_link = d['file']

                return Response({"videoFile": vcdn_redirect_link}, status=200)
            else:
                response_data = {
                    'Status': 'error',
                    'Error': 'Invalid Header Data'
                }
                return Response(response_data, status=404)
        else:
            response_data = {
                'Status': 'error',
                'Error': 'No data submitted'
            }
            return Response(response_data, status=404)


@api_view(['POST'])
def check_special_only(request):
    if request.method == 'POST':
        data = request.data
        if data is not None:
            episodes = Episode_class.objects.filter(mAnime=data["mNameEN"].lower()).filter(mIsSpecial=False).all()

            if episodes is not None:
                if len(episodes) > 0:
                    response_data = {
                        'Status': False
                    }
                    return Response(response_data, status=200)
                else:
                    response_data = {
                        'Status': True
                    }
                    return Response(response_data, status=200)
            else:
                response_data = {
                    'Status': False
                }
                return Response(response_data, status=200)
        else:
            response_data = {
                'Status': 'error',
                'Error': 'No data submitted'
            }
            return Response(response_data, status=404)
