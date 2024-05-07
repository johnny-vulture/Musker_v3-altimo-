from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name="home"),
    path('profile_list/', views.profile_list, name='profile_list'),
    path('profile/<int:pk>', views.profile, name='profile'),
    path('profile/followers/<int:pk>', views.followers, name='followers'),
    path('profile/follows/<int:pk>', views.follows, name='follows'),
    path('login/', views.login_user, name='login'),
    path('logout', views.logout_user, name='logout'),
    path('register/', views.register_user, name='register'),
    path('update_user/', views.update_user, name='update_user'),

    path('unfollow/<int:pk>', views.unfollow, name="unfollow"),
    path('follow/<int:pk>', views.follow, name="follow"),



    path('fight/', views.challenge_page, name='fight'),
    path('fight1/', views.create_challenge, name='fight1'),
    path('user_challenges/', views.user_challenges, name='user_challenges'),
    path('accept/<int:challenge_id>/',
         views.accept_challenge, name='accept_challenge'),
    path('reject/<int:challenge_id>/',
         views.reject_challenge, name='reject_challenge'),

    # wallet page
    path("portfolio/", views.portfolio_view, name="portfolio"),

    # dash page
    path("dash/", views.dash_view, name="dash"),

    # CRUD operations on cryptos
    # path("search_crypto/", views.search_view, name="search_crypto"),
    path('crypto/', views.search_crypto, name='crypto'),
    path("add_to_portfolio/", views.add_to_portfolio_view, name="add_to_portfolio"),
    path('delete_from_portfolio/<int:pk>/',
         views.delete_from_portfolio_view, name='delete_from_portfolio'),





]
