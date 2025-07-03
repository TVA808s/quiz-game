from django.contrib.auth.hashers import make_password
from .models import *

users_data = [
    {
        'username': 'quiz_master',
        'email': 'master@quiz.com',
        'password': 'quiz12345',
        'total_games': 15,
        'possible_points': 1500,
        'earned_points': 1200,
        'avatar': 'master.png',
        'friends': [2, 3]
    },
    {
        'username': 'john_doe',
        'email': 'john@example.com',
        'password': 'john12345',
        'total_games': 8,
        'possible_points': 800,
        'earned_points': 650,
        'avatar': 'john.png',
        'friends': [1, 3]
    },
    {
        'username': 'jane_smith',
        'email': 'jane@example.com',
        'password': 'jane12345',
        'total_games': 12,
        'possible_points': 1200,
        'earned_points': 950,
        'avatar': 'jane.png',
        'friends': [1, 2, 4]
    },
    {
        'username': 'new_player',
        'email': 'new@example.com',
        'password': 'new12345',
        'total_games': 2,
        'possible_points': 200,
        'earned_points': 150,
        'avatar': 'default.png',
        'friends': [3]
    }
]

quizes_data = [
    {
        'title': 'General Knowledge',
        'category': 'General',
        'questions': [101, 102, 103, 104, 105, 106, 107, 108, 109, 110],
        'difficulty': 'easy'
    },
    {
        'title': 'Science Challenge',
        'category': 'Science',
        'questions': [201, 202, 203, 204, 205, 206, 207, 208, 209, 210],
        'difficulty': 'medium'
    },
    {
        'title': 'History Expert',
        'category': 'History',
        'questions': [301, 302, 303, 304, 305, 306, 307, 308, 309, 310],
        'difficulty': 'hard'
    },
    {
        'title': 'Mixed Bag',
        'category': 'Mixed',
        'questions': [101, 205, 302, 107, 209, 303, 110, 208, 306, 104],
        'difficulty': 'mixed'
    }
]

users_on_quizes_data = [
    {
        'user_id': 1,
        'quiz_id': 1,
        'possible_points': 100,
        'earned_points': 95,
        'date': '2023-05-10'
    },
    {
        'user_id': 1,
        'quiz_id': 2,
        'possible_points': 100,
        'earned_points': 85,
        'date': '2023-05-12'
    },
    {
        'user_id': 2,
        'quiz_id': 1,
        'possible_points': 100,
        'earned_points': 70,
        'date': '2023-05-11'
    },
    {
        'user_id': 3,
        'quiz_id': 3,
        'possible_points': 100,
        'earned_points': 90,
        'date': '2023-05-15'
    },
    {
        'user_id': 4,
        'quiz_id': 4,
        'possible_points': 100,
        'earned_points': 60,
        'date': '2023-05-18'
    }
]

lobbies_data = [
    {
        'quiz_id': 1,
        'creator_id': 1,
        'key': 'ABCD1234',
        'password': '',
        'visability': 'public',
        'status': 'waiting',
        'max_players': 4,
        'created_at': '2023-05-20T10:00:00Z',
        'players': [1, 2]  # Игроки, которые уже присоединились
    },
    {
        'quiz_id': 2,
        'creator_id': 3,
        'key': 'EFGH5678',
        'password': 'science123',
        'visability': 'private',
        'status': 'waiting',
        'max_players': 4,
        'created_at': '2023-05-20T11:30:00Z',
        'players': [3]  # Только создатель пока
    },
    {
        'quiz_id': 4,
        'creator_id': 2,
        'key': 'IJKL9012',
        'password': '',
        'visability': 'friends',
        'status': 'starting',
        'max_players': 4,
        'created_at': '2023-05-20T09:15:00Z',
        'players': [2, 1, 3]  # Почти полное лобби
    }
]

def gentestdata():
    for user_data in users_data:
        user_data['password'] = make_password(user_data['password'])
        Users.objects.create(**user_data)

    for quiz_data in quizes_data:
        Quizes.objects.create(**quiz_data)

    for result_data in users_on_quizes_data:
        UsersOnQuizes.objects.create(**result_data)

    for lobby_data in lobbies_data:
        players = lobby_data.pop('players')
        lobby = Lobby.objects.create(**lobby_data)
        lobby.players.set(players)
