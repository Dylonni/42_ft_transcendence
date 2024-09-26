import logging
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.response import Response
from pong.views import PrivateView
from .models import Game, GameRound, GameInvite, GameMessage
from .serializers import GameSerializer, GameRoundSerializer, GameInviteSerializer, GameMessageSerializer

logger = logging.getLogger('django')


class GameListView(PrivateView):
    def get(self, request):
        games = Game.objects.all()
        serializer = GameSerializer(games, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        serializer = GameSerializer(data=request.data)
        if not serializer.is_valid():
            response_data = {'error': serializer.errors}
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        try:
            game = Game.objects.set_game_infos(serializer.save(), request.profile)
            response_data = {'message': _('Game created.'), 'redirect': f'/games/{game.id}/'}
            return Response(response_data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            response_data = {'error': str(e)}
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

game_list = GameListView.as_view()


class GameSearchView(PrivateView):
    def get(self, request):
        name = request.query_params.get('name', '')
        games = Game.objects.search_by_name(name)
        if not games.exists():
            response_data = {'message': _('Game not found.')}
            return Response(response_data, status=status.HTTP_200_OK)
        response_data = {'data': GameSerializer(games, many=True).data}
        return Response(response_data, status=status.HTTP_200_OK)

game_search = GameSearchView.as_view()


class GameDetailView(PrivateView):
    def get(self, request, game_id):
        game = get_object_or_404(Game, id=game_id)
        response_data = {'data': GameSerializer(game).data}
        return Response(response_data, status=status.HTTP_200_OK)

game_detail = GameDetailView.as_view()


class GameJoinView(PrivateView):
    def post(self, request, game_id):
        try:
            game = get_object_or_404(Game, id=game_id)
            Game.objects.add_player(game, request.profile)
            response_data = {'message': _('Game joined.'), 'redirect': f'/games/{game_id}/'}
            return Response(response_data, status=status.HTTP_200_OK)
        except ValueError as e:
            response_data = {'error': str(e)}
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

game_join = GameJoinView.as_view()


class GameLeaveView(PrivateView):
    def post(self, request, game_id):
        try:
            game = get_object_or_404(Game, id=game_id)
            Game.objects.remove_player(game, request.profile)
            response_data = {'message': _('Game left.'), 'redirect': f'/home/'}
            return Response(response_data, status=status.HTTP_200_OK)
        except ValueError as e:
            response_data = {'error': str(e)}
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

game_leave = GameLeaveView.as_view()


class GameStartView(PrivateView):
    def post(self, request, game_id):
        try:
            game = get_object_or_404(Game, id=game_id)
            player = request.profile
            if not game.can_start(player):
                response_data = {'error': _('Need more players.')}
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
            rounds = GameRound.objects.prepare_rounds(game)
            Game.objects.start(game)
            round = Game.objects.get_next_round(game)
            rounds_data = GameRoundSerializer(rounds, many=True).data
            response_data = {'message': _('Game started.'), 'data': rounds_data}
            return Response(response_data, status=status.HTTP_200_OK)
        except ValueError as e:
            response_data = {'error': str(e)}
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

game_start = GameStartView.as_view()


class GameMessageListView(PrivateView):
    def get(self, request, game_id):
        game = get_object_or_404(Game, id=game_id)
        serializer = GameMessageSerializer(game.messages, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request, game_id):
        try:
            game = get_object_or_404(Game, id=game_id)
            GameMessage.objects.send_message(game, request.profile, request.data['message'])
            response_data = {'message': _('Message sent.')}
            return Response(response_data, status=status.HTTP_200_OK)
        except ValueError as e:
            response_data = {'error': str(e)}
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

game_message_list = GameMessageListView.as_view()