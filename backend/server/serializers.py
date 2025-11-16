from rest_framework import serializers 
from .models import Users, UsersOnQuizes, Lobbies
from rest_framework.validators import UniqueValidator
import django.contrib.auth.password_validation as validators

class PublicUserSerializer(serializers.ModelSerializer):
    class Meta:
        model: Users
        fields = '__all__'
        exclude = ['email']

class PublicUserShortSerializer(serializers.ModelSerializer):
    class Meta:
        model: Users
        fields = ['id', 'username', 'avatar', 'total_games', 'average']
        
class PrivateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = '__all__'

class GameDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = UsersOnQuizes
        fields = '__all__'
        

class LeaderBoardPlayerDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ['id', 'username', 'avatar', 'earned_points', 'possible_points', 'average']

class LeaderBoardDataSerializer(serializers.Serializer):
    period = serializers.CharField()
    players = LeaderBoardPlayerDataSerializer(many=True, read_only=True)

class PublicLobbySerializer(serializers.ModelSerializer):
    class Meta:
        model = Lobbies
        fields = '__all__'
        exclude = ['key']

class PrivateLobbySerializer(serializers.ModelSerializer):
    class Meta:
        model = Lobbies
        fields = '__all__'

class PublicLobbiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lobbies
        fields = ['title', 'category', 'max_players', 'current_players', 'created_at']
    
class FriendSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ['id', 'username', 'avatar']

class FriendsListSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    friends = FriendSerializer(many=True)

class ResultsSerializer(serializers.Serializer):
    lobbies = PublicLobbiesSerializer(many=True)
    users = PublicUserShortSerializer(many=True, read_only=True)

class UserRegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=Users.objects.all())]
    )
    username = serializers.CharField(
        validators=[UniqueValidator(queryset=Users.objects.all())]
    )
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={'input_type': 'password'}
    )
    class Meta:
        model = Users
        fields = ['username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True, 'style': {'input_type': 'password'}}} 
    
    def validate_password(self, value):
        try:
            validators.validate_password(password=value)
        except validators.ValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value

    def create(self, validated_data):
        user = Users.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user

class UserAuthenticationSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=32)
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
