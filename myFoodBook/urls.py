"""myFoodBook URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.contrib import admin
from django import urls
from django.urls import path, include, re_path
from foodBookApp import views as food_book_views
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.conf import settings





#URL Patterns for Web App
urlpatterns = [
    path('admin/', admin.site.urls),  

    path('',food_book_views.home, name="home"),
    path('splash',food_book_views.splash, name="splash-page"),
    path('register/',food_book_views.register,name='register'),
    path('login/',auth_views.LoginView.as_view(template_name='foodBookApp/login.html'), name='login'),
    path('logout/',auth_views.LogoutView.as_view(template_name='foodBookApp/logout.html'), name='logout'),
    path('change-password/', auth_views.PasswordChangeView.as_view(),name='change-password'),
    path('reset-password', auth_views.PasswordResetView.as_view(),name='reset-password'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    path('main/', food_book_views.get_main_feed,name='main-feed'),
    path('explore/users', food_book_views.ProfileListView.as_view(),name='explore-users'),
    path('profile-edit',food_book_views.ProfileUpdateView.as_view(),name='edit-profile'),
    path('profile/<str:username>', food_book_views.ProfilePagePostListView.as_view(),name='user-profile'),
    path('profile/<str:username>/photos', food_book_views.photos,name='user-photos'),
    path('profile/<str:username>/friends', food_book_views.user_friends,name='user-friends'),
    path('settings/', food_book_views.user_settings, name='user-settings'),

    path('photos/', food_book_views.my_photos,name='my-photos'),
    path('friends/', food_book_views.friends,name='my-friends'),
    path('invite/accept', food_book_views.accept_invatation,name='accept-invite'),
    path('invite/reject', food_book_views.reject_invatation,name='reject-invite'),
    path('send-invite/',food_book_views.send_invatation, name='send-invite'),
    path('remove-friend/',food_book_views.remove_from_friends, name='remove-friend'),
    
    path('like/<int:pk>',food_book_views.like, name='like-post'),


    path('my-invites/', food_book_views.invites_view, name='my-invites'),

    path('post/',food_book_views.PostCreateView.as_view(),name='new-post'),
    path('post/<int:pk>/', food_book_views.post,name='view-post'),    
    path('post/<int:pk>/update', food_book_views.PostUpdateView.as_view(),name='edit-post'),
    path('post/<int:pk>/delete', food_book_views.PostDeleteView.as_view(),name='delete-post'),

    path('convos/', include('conversations.urls')),

    path('search/', food_book_views.search_results, name='search'),

    re_path(
        r'^tags-autocomplete/$',
        food_book_views.TagAutocomplete.as_view(),
        name='tags-autocomplete',
    ),
]

#FOR HOSTING MEDIA FILES WHILE IN DVELOPMENT WILL NEED TO CHANGE ON DEPLOYMENT
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

