import logging
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.response import Response
from pong.views import PrivateView
from .models import Game, Player, Round
from .serializers import GameSerializer, RoundSerializer

logger = logging.getLogger('django')


class GameListView(PrivateView):
    def get(self, request):
        games = Game.objects.all()
        serializer = GameSerializer(games, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        try:
            serializer = GameSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            game = serializer.save()
            logger.info(f'Game {game.id}: {request.profile.alias} created the room.')
            player = Player.objects.join_game(request.profile, game)
            logger.info(f'Game {game.id}: {request.profile.alias} joined.')
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
            return Response(data=games_data, status=status.HTTP_200_OK)
        else:
            logger.info(f'No games found for name "{name}".')
            return Response(status=status.HTTP_204_NO_CONTENT)

game_search = GameSearchView.as_view()


class GameDetailView(PrivateView):
    def get(self, request, game_id):
        game = get_object_or_404(Game, id=game_id)
        serializer = GameSerializer(game)
        return Response(serializer.data)

game_detail = GameDetailView.as_view()


class GameJoinView(PrivateView):
    def post(self, request, game_id):
        game = get_object_or_404(Game, id=game_id)
        can_join = Player.objects.can_join_game(game)
        if can_join:
            player = Player.objects.join_game(request.profile, game)
            logger.info(f'Game {game.id}: {request.profile.alias} joined.')
            response = Response(
                {
                    'status': _('Player joined!'),
                    'redirect': f'/games/{game_id}',
                },
                status=status.HTTP_200_OK,
            )
            return response
        else:
            logger.info(f'Game {game.id}: {request.profile.alias} failed to join.')
            return Response(status=status.HTTP_204_NO_CONTENT)

game_join = GameJoinView.as_view()


class GameLeaveView(PrivateView):
    def post(self, request, game_id):
        game = get_object_or_404(Game, id=game_id)
        has_left = Player.objects.leave_game(request.profile, game)
        if has_left:
            logger.info(f'Game {game.id}: {request.profile.alias} left.')
            response = Response(
                {
                    'status': _('Player left!'),
                    'redirect': '/home/',
                },
                status=status.HTTP_200_OK,
            )
            return response
        else:
            logger.info(f'Game {game.id}: {request.profile.alias} failed to leave.')
            return Response(status=status.HTTP_204_NO_CONTENT)

game_leave = GameLeaveView.as_view()


class GameStartView(PrivateView):
    def post(self, request, game_id):
        if Player.objects.can_start_game(game_id):
            game = get_object_or_404(Game, id=game_id)
            players = Player.objects.shuffle_players_for_game(game_id)
            rounds = Round.objects.prepare_rounds(players, game)
            rounds = Round.objects.start_game(players)
            rounds_data = RoundSerializer(rounds, many=True).data
            logger.info(f'Game {game.id}: Matches are about to begin.')
            return Response(data=rounds_data, status=status.HTTP_204_NO_CONTENT)
        logger.info(f'Game {game_id}: Cannot start.')
        return Response(status=status.HTTP_204_NO_CONTENT)

game_start = GameStartView.as_view()


class GameReadyView(PrivateView):
    def post(self, request, game_id):
        game = get_object_or_404(Game, id=game_id)
        player = get_object_or_404(Player, profile=request.profile)
        player = Player.objects.mark_ready(player, player.ready)
        logger.info(f'Game {game_id}: {request.profile.alias} is ready.')
        return Response(status=status.HTTP_204_NO_CONTENT)

game_ready = GameReadyView.as_view()