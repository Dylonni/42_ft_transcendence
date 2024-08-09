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
        serializer.is_valid(raise_exception=True)
        player = request.profile
        
        if player.game:
            message = 'Player already in a game.'
            extra = {'player': player}
            logger.info(message, extra=extra)
            response_data = {'message': _(message)}
            return Response(response_data, status=status.HTTP_201_CREATED)
        
        game = serializer.save(name=Game.objects.generate_name(), host=player)
        player.join_game(game)
        
        message = 'Player created a game.'
        extra = {'game': game, 'player': player}
        logger.info(message, extra=extra)
        response_data = {'message': _(message), 'redirect': f'/games/{game.id}/', 'game_id': game.id}
        return Response(response_data, status=status.HTTP_201_CREATED)

game_list = GameListView.as_view()


class GameSearchView(PrivateView):
    def get(self, request):
        name = request.query_params.get('name', '')
        games = Game.objects.search_by_name(name)
        extra = {'name': name}
        
        if games.exists():
            games_data = GameSerializer(games, many=True).data
            return Response(games_data, status=status.HTTP_200_OK)
        
        message = 'No game rooms found.'
        logger.info(message, extra=extra)
        response_data = {'message': _(message)}
        return Response(response_data, status=status.HTTP_200_OK)

game_search = GameSearchView.as_view()


class GameDetailView(PrivateView):
    def get(self, request, game_id):
        game = get_object_or_404(Game, id=game_id)
        serializer = GameSerializer(game)
        return Response(serializer.data, status=status.HTTP_200_OK)

game_detail = GameDetailView.as_view()


class GameJoinView(PrivateView):
    def post(self, request, game_id):
        game = get_object_or_404(Game, id=game_id)
        player = request.profile
        extra = {'game': game, 'player': player}
        
        if player in game.players.all():
            message = 'Player is already in the game.'
            logger.info(message, extra=extra)
            response_data = {'message': _(message)}
            return Response(response_data, status=status.HTTP_200_OK)
        if game.is_full():
            message = 'Game is full. Unable to join.'
            logger.info(message, extra=extra)
            response_data = {'message': _(message)}
            return Response(response_data, status=status.HTTP_200_OK)
        
        player.join_game(game)
        message = 'Player joined the game.'
        logger.info(message, extra=extra)
        response_data = {'message': _(message), 'redirect':  f'/games/{game_id}/'}
        return Response(response_data, status=status.HTTP_200_OK)

game_join = GameJoinView.as_view()


class GameLeaveView(PrivateView):
    def post(self, request, game_id):
        game = get_object_or_404(Game, id=game_id)
        player = request.profile
        player.leave_game()
        response_data = {'redirect': '/home/'}
        extra = {'game': game, 'player': player}
        
        if game.host == player:
            new_host = game.players.exclude(id=player.id).first()
            if new_host:
                game.set_host(new_host)
                message = 'Player left the game. A new host has been chosen.'
                extra['new_host'] = new_host
                logger.info(message, extra=extra)
                response_data['message'] = _(message)
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                game.delete()
                message = 'Player left the game. The game has been deleted.'
                logger.info(message, extra=extra)
                response_data['message'] = _(message)
                return Response(response_data, status=status.HTTP_200_OK)
        
        message = 'Player left the game.'
        logger.info(message, extra=extra)
        response_data['message'] = _(message)
        return Response(response_data, status=status.HTTP_200_OK)

game_leave = GameLeaveView.as_view()


class GameStartView(PrivateView):
    def post(self, request, game_id):
        game = get_object_or_404(Game, id=game_id)
        player = request.profile
        extra = {'game': game, 'player': player}
        
        if game.can_start(player):
            # TODO: need to test
            players = game.shuffle_players()
            rounds = GameRound.objects.prepare_rounds(players, game)
            rounds = GameRound.objects.start_game(players)
            rounds_data = GameRoundSerializer(rounds, many=True).data
            message = 'Player started the game.'
            logger.info(message, extra=extra)
            response_data = {'message': _(message)}
            return Response(response_data, status=status.HTTP_200_OK)
        
        message = 'All players must be ready.'
        logger.info(message, extra=extra)
        response_data = {'message': _(message)}
        return Response(response_data, status=status.HTTP_200_OK)

game_start = GameStartView.as_view()


class GameReadyView(PrivateView):
    def post(self, request, game_id):
        game = get_object_or_404(Game, id=game_id)
        player = request.profile
        extra = {'game': game, 'player': player}
        
        if player.toggle_ready():
            message = 'Player set ready.'
        else:
            message = 'Player canceled ready state.'
        logger.info(message, extra=extra)
        response_data = {'message': _(message)}
        return Response(response_data, status=status.HTTP_200_OK)

game_ready = GameReadyView.as_view()