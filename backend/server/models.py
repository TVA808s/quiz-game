from django.db import models
from django.db.models import JSONField
from django.contrib.auth.models import AbstractUser

class Users(AbstractUser):
    first_name = None
    last_name = None
    total_games = models.PositiveBigIntegerField(default=0)
    possible_points = models.PositiveIntegerField(default=0)
    earned_points = models.PositiveIntegerField(default=0)
    avatar = models.CharField(max_length=64, default='1.png')
    friends = JSONField(default=list, blank=True) # массив содержащий id других пользователей
    
    # переопределение из-за ошибки именований
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='server_users_set',
        related_query_name='server_user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='server_users_set',
        related_query_name='server_user',
    )
    
class Quizes(models.Model):
    DIFFICULTY = [
        ('eazy', 'легкая'),
        ('medium', 'средняя'), 
        ('hard', 'высокая'),
        ('mixed', 'смешанная')
    ]
       
    title = models.CharField(max_length=32)
    category = models.CharField(max_length=16)
    questions = JSONField(default=list) # массив содержащий id вопросов из api
    difficulty = models.CharField(choices=DIFFICULTY)

class UsersOnQuizes(models.Model):
    user_id = models.ForeignKey(Users, on_delete=models.CASCADE)
    quiz_id = models.ForeignKey(Quizes, on_delete=models.CASCADE)
    possible_points = models.PositiveIntegerField(default=0)
    earned_points = models.PositiveIntegerField(default=0)
    date = models.DateField(auto_now_add=True)
    class Meta:
        ordering = ['-date']
        unique_together = ['user_id', 'quiz_id']

class Lobby(models.Model):
    VISABILITY = [
        ('public', 'публичная'),
        ('private', 'скрытая'),
        ('friends', 'видна друзьям')
    ]
        
    STATUS = [
        ('waiting', 'ожидание'),
        ('starting', 'запуск')
    ]        
    
    quiz_id = models.ForeignKey(Quizes, on_delete=models.CASCADE)
    creator = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='created_lobbies')
    players = models.ManyToManyField(Users, related_name='joined_lobbies')
    key = models.CharField(max_length=8, unique=True)
    visability = models.CharField(choices=VISABILITY)
    status = models.CharField(choices=STATUS)
    max_players = models.PositiveBigIntegerField(default=4)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['key']),
            models.Index(fields=['status', 'visability'])
        ]    
    @property
    def player_count(self):
        return self.players.count()
    
    def is_joinable(self):
        return (
            self.status == 'waiting'
            and self.player_count < self.max_players
        )





