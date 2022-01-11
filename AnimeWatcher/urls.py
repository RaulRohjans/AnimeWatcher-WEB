"""AnimeWatcher URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from Authentication.views import *
from Content.views import *
from Admin.views import *
from Api.views import *

urlpatterns = [

    # Authentication
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),
    path('account-settings/', account_settings_view, name='account-settings'),
    path('account-settings/<token>/', account_settings_token_view, name='account-settings-token'),
    path('change-password/', change_password_view, name='change-password'),
    path('change-password/<token>/', change_password_token_view, name='change-password-token'),
    path('forgot-password/', forgot_password_view, name='forgot-password'),
    path('recover-password/<uidb64>/<token>/', recover_password_view, name='recover-password'),
    path('account-activation/<uidb64>/<token>/', verification_view, name='account-activation'),


    # Content
    path('', home_view, name='home'),
    path('about-us/', about_us_view, name='about-us'),
    path('donate/', donate_view, name='donate'),
    path('disclaimer/', disclaimer_view, name='disclaimer'),
    path('privacy-policy/', privacy_policy_view, name='privacy-policy'),
    path('my-list/', my_list_view, name='my-list'),
    path('anime/', anime_list_view, name='anime-list'),
    path('anime/<str:AnimeID>/', anime_view, name='animes'),
    path('anime/<str:AnimeID>/<int:EpisodeID>/', play_anime_view, name='anime-player'),
    path('report-comment/<int:id>', report_comment_view, name='report-comment'),
    path('delete-comment/<int:id>', delete_comment_view, name='delete-comment'),
    path('submit-anime/', submit_anime_view, name='submit-anime'),
    path('category/<str:id>/', category_view, name='category_id'),
    path('category/', category_list_view, name='categories'),


    # Admin
    path('admin/', admin_home_view, name='admin'),

    path('admin/user', redirect_view, name='admin-user'),
    path('admin/user/create', admin_user_create_view, name='admin-user-create'),
    path('admin/user/all', admin_user_edit_view, name='admin-user-all'),
    path('admin/user/edit/<str:username>', admin_user_edit_username_view, name='admin-user-edit-username'),

    path('admin/anime', redirect_view, name='admin-anime'),
    path('admin/anime/create', admin_anime_create_view, name='admin-anime-create'),
    path('admin/anime/all', admin_anime_edit_view, name='admin-anime-all'),
    path('admin/anime/edit/<str:id>', admin_anime_edit_id_view, name='admin-anime-edit-id'),
    path('admin/anime/mylist', redirect_view, name='admin-anime-mylist'),
    path('admin/anime/mylist/create', admin_anime_list_create_view, name='admin-anime-mylist-create'),
    path('admin/anime/mylist/all', admin_anime_list_edit_view, name='admin-anime-mylist-all'),
    path('admin/anime/mylist/edit/<int:id>', admin_anime_list_edit_id_view, name='admin-anime-mylist-edit-id'),
    path('admin/anime/submitted', admin_anime_submitted_view, name='admin-anime-submitted'),

    path('admin/category', redirect_view, name='admin-category'),
    path('admin/category/create', admin_category_create_view, name='admin-category-create'),
    path('admin/category/all', admin_category_edit_view, name='admin-category-all'),
    path('admin/category/edit/<str:id>', admin_category_edit_id_view, name='admin-category-edit-id'),

    path('admin/episode', redirect_view, name='admin-episode'),
    path('admin/episode/create', admin_episode_create_view, name='admin-episode-create'),
    path('admin/episode/all', admin_episode_edit_view, name='admin-episode-all'),
    path('admin/episode/edit/<int:id>', admin_episode_edit_id_view, name='admin-episode-edit-id'),

    path('admin/reported-comments', admin_rep_comments_view, name='admin-repcomments'),


    # Api
    path('api/ping', ping_api, name='api-ping'),
    path('api/check-app-updates', check_app_updates, name='api-check-app-updates'),
    path('api/authenticate-user', authenticate_user, name='api-authenticate-user'),
    path('api/register-new-user', register_new_user, name='api-register-new-user'),
    path('api/logout', logout_user, name='api-logout'),
    path('api/get-user-data', get_user_data, name='api-get-user-data'),
    path('api/settings-change-user', settings_change_user, name='api-settings-change-user'),
    path('api/settings-change-email', settings_change_email, name='api-settings-change-email'),
    path('api/settings-change-password', settings_change_password, name='api-settings-change-password'),
    path('api/user-recover-password', user_recover_password, name='api-user-recover-password'),
    path('api/submit-anime', submit_anime, name='api-submit-anime'),
    path('api/get-all-anime', get_all_anime, name='api-get-all-anime'),
    path('api/get-mylist-anime', get_mylist_anime, name='api-get-mylist-anime'),
    path('api/get-search-anime', get_search_anime, name='api-get-search-anime'),
    path('api/get-string-categories', get_string_cats, name='api-get-string-categories'),
    path('api/get-category-anime', get_category_anime, name='api-get-category-anime'),
    path('api/get-episodes', get_episodes, name='api-get-episodes'),
    path('api/get-episodes-latest', get_episodes_latest, name='api-get-episodes-latest'),
    path('api/get-episodes-most-views', get_episodes_most_views, name='api-get-episodes-most-views'),
    path('api/get-episodes-random', get_episodes_random, name='api-get-episodes-random'),
    path('api/get-episode', get_episode, name='api-get-episode'),
    path('api/get-episode-next', get_episode_next, name='api-get-episode-next'),
    path('api/get-anime-thumbnail', get_anime_thumbnail, name='api-get-anime-thumbnail'),
    path('api/episode-add-view', episode_add_view, name='api-episode-add-view'),
    path('api/check-token', check_token, name='api-check-token'),
    path('api/my-list-add', add_mylist, name='api-my-list-add'),
    path('api/my-list-remove', remove_mylist, name='api-my-list-remove'),
    path('api/my-list-check', check_mylist, name='api-my-list-check'),
    path('api/check-special-only', check_special_only, name='api-check-special-only'),


    path('api/vcdn/', vcdn_url_post, name='api-vcdn'),
]
