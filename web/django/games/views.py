import logging
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.response import Response
from pong.views import PrivateView
from .models import Game
from .serializers import GameSerializer

logger = logging.getLogger('django')


class GameListView(PrivateView):
    def get(self, request):
        games = Game.objects.all()
        serializer = GameSerializer(games, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        try:
            game = Game.objects.create_game()
            logger.info(f'Game {game.id} created by {request.profile.alias}.')
            # TODO: Add logic to make player and join game
            serializer = GameSerializer(game)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            logger.warn(str(e))
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

game_list = GameListView.as_view()


class GameSearchView(PrivateView):
    def get(self, request):
        name = request.query_params.get('name', '')
        games = Game.objects.search_by_name(name)
        if games.exists():
            games_data = GameSerializer(games, many=True).data
            logger.info(f'Games found for name "{name}".')
            return Response(games_data, status=status.HTTP_200_OK)
        else:
            logger.info(f'No games found for name "{name}".')
            return Response(status=status.HTTP_204_NO_CONTENT)

game_search = GameSearchView.as_view()