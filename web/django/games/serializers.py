from rest_framework import serializers
from .models import Game, GameRound, GameInvite, GameMessage


class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = '__all__'

    # def validate(self, attrs):
    #     map_choice = int(attrs.get('mapChoice'))
    #     if map_choice < 0 or map_choice > 4:
    #         map_choice = 0
    #     attrs['mapChoice'] = map_choice
    #     return attrs        


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