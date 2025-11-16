from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)



urlpatterns = [
    path('main', views.main),
    path('search', views.search),

    path('registration', views.registration),
    path('authorization', views.authorization),

    path('users/<int:userId>', views.user),
    path('profile', views.profile),

    path('lobby/<int:lobbyId>', views.lobby),
    path('game/<int:gameId>/ws', views.game),

    path('friends', views.friends),
    path('leaderboard', views.leaderboard),

]
