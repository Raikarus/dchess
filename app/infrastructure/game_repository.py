import threading
from typing import Optional, Dict

from app.domain.aggregates.game import Game


class GameRepository:
    def __init__(self):
        self._games: Dict[str, Game] = {}
        self._lock = threading.Lock()

    def add(self, game: Game) -> None:
        with self._lock:
            self._games[str(game.uuid)] = game

    def get(self, game_uuid: str) -> Optional[Game]:
        with self._lock:
            return self._games.get(game_uuid)

    def remove(self, game_uuid: str) -> None:
        with self._lock:
            if game_uuid in self._games:
                del self._games[game_uuid]

    def list_all(self):
        with self._lock:
            return list(self._games.values())
