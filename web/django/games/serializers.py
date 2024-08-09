from rest_framework import serializers
from .models import Game, GameRound, GameInvite, GameMessage


class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = '__all__'


class GameRoundSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameRound
        fields = '__all__'


class GameInviteSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameInvite
        fields = '__all__'


class GameMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameMessage
        fields = '__all__'