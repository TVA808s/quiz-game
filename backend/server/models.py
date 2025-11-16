from django.db import models
from django.contrib.auth.models import AbstractUser

class Users(AbstractUser):
    # для авторизации по логину
    USERNAME_FIELD = 'email' 
    email = models.EmailField(unique=True, blank=False, null=False)
    REQUIRED_FIELDS = ['username']
    username = models.CharField(max_length=16, unique=True)

    first_name = None
    last_name = None
    is_active = None
    is_superuser = None
    last_login = None

    total_games = models.PositiveBigIntegerField(default=0)
    possible_points = models.PositiveIntegerField(default=0)
    earned_points = models.PositiveIntegerField(default=0)
    avatar = models.CharField(max_length=64, default='1.png')

    friend_requests = models.ManyToManyField('self', symmetrical=False, blank=True, related_name='received_requests')
    friends = models.ManyToManyField('self', symmetrical=True, blank=True) 
    def accept_friend_request(self, sender):
        self.friend_requests.remove(sender)
        self.friends.add(sender)

    @property
    def average(self):
        if self.possible_points > 0:
            return f"{round(self.earned_points / self.possible_points * 100)}%"
        return '0%'
    
        

class UsersOnQuizes(models.Model):
    # история игр пользователя с результатом игры

    DIFFICULTY = [
        ('easy', 'легкая'),
        ('medium', 'средняя'), 
        ('hard', 'высокая'),
        ('mixed', 'смешанная')
    ]
    user_id = models.ForeignKey(Users, on_delete=models.CASCADE)
    category = models.CharField(max_length=16, default='random')
    difficulty = models.CharField(choices=DIFFICULTY, default='mixed')
    possible_points = models.PositiveIntegerField(default=0)
    earned_points = models.PositiveIntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True)
    class Meta:
        ordering = ['-date']


class Lobbies(models.Model):
    # запись о лобби очищаемая после завершения игры

    DIFFICULTY = [
        ('easy', 'легкая'),
        ('medium', 'средняя'), 
        ('hard', 'высокая'),
        ('mixed', 'смешанная')
    ]
    VISIBILITY = [
        ('public', 'публичная'),
        ('private', 'скрытая'),
        ('friends', 'видна друзьям')
    ]   
    STATUS = [
        ('waiting', 'ожидание'),
        ('starting', 'запуск')
    ]        
    title = models.CharField(max_length=32, default='Quizl')
    category = models.CharField(max_length=16, default='random')
    difficulty = models.CharField(choices=DIFFICULTY, default='mixed')

    creator = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='created_lobbies')
    players = models.ManyToManyField(Users, related_name='joined_lobbies')
    key = models.CharField(max_length=8, unique=True)
    visibility = models.CharField(choices=VISIBILITY)
    status = models.CharField(choices=STATUS)
    max_players = models.PositiveBigIntegerField(default=4)
    created_at = models.DateTimeField(auto_now_add=True)
    @property
    def current_players(self):
        return self.players.count()
    
    class Meta:
        indexes = [
            models.Index(fields=['key']),
            models.Index(fields=['status', 'visibility'])
        ]    
    def is_joinable(self):
        return (
            self.status == 'waiting'
            and self.current_players < self.max_players
        )





