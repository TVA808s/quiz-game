from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle
from rest_framework import status
from django.db.models.functions import Lower
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.cache import cache_page
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from .serializers import *
from .models import *

class PostOnlyThrottle(UserRateThrottle):
    def allow_request(self, request, view):
        if request.method != 'POST':
            return True
        return super().allow_request(request, view)
    
class OncePerMinute(PostOnlyThrottle):
    rate = '1/minute'
class FiftyPerDay(PostOnlyThrottle):
    rate = '50/day'

ErrorResponses = {
    500: {'error': '500 Internal server error', 'message': 'Непредвиденная ошибка, попробуйте позже'},
    405: {'error': '405 Method not allowed', 'message': 'Данный метод недоступен'},
    404: {'error': '404 Not found', 'method': 'Страница не найдена, проверьте URL запроса'},
    403: {'error': '403 Forbidden', 'method': 'Нет разрешения на вход'},
    401: {'error': '401 Unauthorized', 'message': 'Войдите в аккаунт для выполнения этого действия'},
    400: {'error': '400 Bad request', 'message': 'При выполнении запроса произошла ошибка, попробуйте ещё раз'}
}

@api_view(['GET'])
def main(request):
    lobbies = Lobbies.objects.filter(visibility='public', status='waiting').select_related('creator')[:10] 
    lobbies_serializer = PublicLobbySerializer(lobbies, many=True)
    response_data = {
        "count": lobbies.count(),
        "lobbies": lobbies_serializer.data
    }
    if request.user.is_authenticated:
        user_serializer = PublicUserSerializer(request.user)
        response_data["user"] = user_serializer.data
    else:
        response_data["user"] = None
    
    return Response(response_data)

@api_view(['GET', 'POST'])
def search(request):
    if request.method == 'POST':
        search_query = request.data.get('search', '').strip()
        if not search_query:
            return Response({
                'lobbies': [],
                'users': []
            })
        
        lobbies = Lobbies.objects.filter(
            Q(key=search_query, visibility='private') |
            # Q(title__icontains=search_query, visibility='public') |  Названия у лобби нет, у квиза есть
            Q(creator__username__icontains=search_query, visibility='friends'), 
            status='waiting').select_related('creator').distinct()
        lobbies_serializer = PublicLobbySerializer(lobbies, many=True)

        users = Users.objects.filter(
            Q(username__icontains=search_query)
        ).exclude(id=request.user.id)
        users_serializer = PublicUserSerializer(users, many=True)

        response_data = {
            'lobbies': lobbies_serializer.data,
            'users': users_serializer.data
        }

        return Response(response_data)
    
    return Response({
        'lobbies': [],
        'users': []
    })


@throttle_classes([OncePerMinute, FiftyPerDay])
@api_view(['GET', 'POST'])
def registration(request):
    if request.method == 'POST':
        registrationSerializer = UserRegistrationSerializer(data=request.data)
        if registrationSerializer.is_valid():
            try:
                user = registrationSerializer.save()
                return Response(
                    {
                        'redirect': '/main',
                        'user_id': user.id
                    },
                    status=status.HTTP_201_CREATED
                )
            except Exception as e:
                return Response(
                    ErrorResponses[500], status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        return Response(
            ErrorResponses[400], status=status.HTTP_400_BAD_REQUEST
        )
    
    return Response('authorization get')

@throttle_classes([OncePerMinute, FiftyPerDay])
@api_view(['GET', 'POST'])
def authorization(request):
    if request.method == 'POST':
        authorizationSerializer = UserAuthorizationSerializer(data=request.data)
        if not authorizationSerializer.is_valid():
            return Response(
                ErrorResponses[400], status=status.HTTP_400_BAD_REQUEST
            )
        try:
            user = authenticate(
                email=authorizationSerializer.validated_data['email'],
                password=authorizationSerializer.validated_data['password']
            )
            if not user:
                return Response(
                    ErrorResponses[401], status=status.HTTP_401_UNAUTHORIZED
                )
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    'redirect': '/main',
                    'user_id': user.id,
                    'tokens': {
                        'refresh': str(refresh),
                        'access': str(refresh.access_token)
                    }
                }, status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                ErrorResponses[500], status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
    return Response('authorization get')


@api_view(['GET'])
def user(request, userId):
    print(request.path)
    try:
        user = Users.objects.get(id=userId)
        userSerializer = PublicUserSerializer(user)
        return Response(
            userSerializer.data, status=status.HTTP_200_OK
        )
    except Users.DoesNotExist:
        return Response(ErrorResponses[404],status=status.HTTP_404_NOT_FOUND)
    
    except Exception as e:
        return Response(
            ErrorResponses[500], status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    

@api_view()
@permission_classes([IsAuthenticated])
@cache_page(60 * 10)
def profile(request):
    try: 
        user = request.user
        userSerializer = PrivateUserSerializer(user)
        return Response(userSerializer.data)
    except Exception as e:
        return Response(
            ErrorResponses[500], status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view()
@permission_classes([IsAuthenticated])
def friends(request):
    try:
        user = request.user
        friends = user.friends.all().only(
            'id', 'username', 'avatar'
        )
        friendsSerializer = FriendSerializer(friends, many=True)
        friendsListSerializer = FriendsListSerializer({
            'count': friends.count(),
            'friends': friendsSerializer.data
        })
        return Response(friendsListSerializer.data)
    
    except Exception as e:
        return Response(
            ErrorResponses[500], status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET', 'POST'])
@cache_page(60 * 10)
def leaderboard(request):
    users = Users.objects.all()
    usersSerializer = LeaderBoardPlayerSerializer(users, many=True)
    leaderboardSerializer = LeaderBoardDataSerializer({
        'period': 'all',
        'players': usersSerializer
    })
    if request.method == 'POST':
        return Response('leaderboard post')
    return Response(leaderboardSerializer.data)


@api_view(['GET', 'POST'])
def lobby(request, lobbyId): 
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return Response(
                ErrorResponses[401],
                status=status.HTTP_401_UNAUTHORIZED
            )
        return Response('lobby post')
    return Response(f'lobby get {lobbyId}')

@api_view()
@permission_classes([IsAuthenticated])
def game(request, gameId):
    return Response(f'game {gameId}')
