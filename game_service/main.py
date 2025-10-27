from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import Dict, List, Optional, Set
import logging
import json
import httpx
import asyncio
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

DJANGO_API_URL = "http://backend:8000/api"
MIN_PLAYERS = 2
MAX_PLAYERS = 8
QUESTION_COUNT = 5
ANSWER_DISPLAY_TIME = 3

class Player:
    def __init__(self, client_id: str, websocket: WebSocket):
        self.client_id = client_id
        self.websocket = websocket
        self.score = 0
        self.ready = False
        self.current_answer: Optional[str] = None
        self.has_answered = False

class Game:
    def __init__(self, game_id: str):
        self.game_id = game_id
        self.players: Dict[str, Player] = {}
        self.questions: List[dict] = []
        self.current_question_index = 0
        self.state = "waiting"  # waiting, playing, finished
        self.created_at = datetime.now()
        self.answered_players: Set[str] = set()
        self.question_lock = asyncio.Lock()

    def add_player(self, client_id: str, websocket: WebSocket) -> bool:
        if len(self.players) >= MAX_PLAYERS:
            return False
        if client_id in self.players:
            return False
        self.players[client_id] = Player(client_id, websocket)
        logger.info(f"Player {client_id} added to game {self.game_id}. Total: {len(self.players)}")
        return True

    def remove_player(self, client_id: str):
        if client_id in self.players:
            del self.players[client_id]
            logger.info(f"Player {client_id} removed from game {self.game_id}. Total: {len(self.players)}")

    def can_start(self) -> bool:
        return len(self.players) >= MIN_PLAYERS and self.state == "waiting"

    async def fetch_questions(self) -> bool:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{DJANGO_API_URL}/game/random-questions/",
                    params={"count": QUESTION_COUNT}
                )
                if response.status_code == 200:
                    self.questions = response.json()
                    logger.info(f"Fetched {len(self.questions)} questions for game {self.game_id}")
                    return True
                else:
                    logger.error(f"Failed to fetch questions: {response.status_code}")
                    return False
        except Exception as e:
            logger.error(f"Error fetching questions: {e}")
            return False

    def get_current_question(self) -> Optional[dict]:
        if 0 <= self.current_question_index < len(self.questions):
            q = self.questions[self.current_question_index]
            return {
                "question_number": self.current_question_index + 1,
                "total_questions": len(self.questions),
                "question_text": q["question_text"],
                "question_id": q["id"]
            }
        return None

    def check_answer(self, client_id: str, answer: str) -> bool:
        if self.current_question_index >= len(self.questions):
            return False

        correct_answer = self.questions[self.current_question_index]["correct_answer"]
        is_correct = answer.strip().lower() == correct_answer.strip().lower()

        if is_correct and client_id in self.players:
            self.players[client_id].score += 1

        return is_correct

    def reset_answers(self):
        self.answered_players.clear()
        for player in self.players.values():
            player.has_answered = False
            player.current_answer = None

    def all_players_answered(self) -> bool:
        return len(self.answered_players) >= len(self.players)

    def get_leaderboard(self) -> List[dict]:
        return [
            {"client_id": p.client_id, "score": p.score}
            for p in sorted(self.players.values(), key=lambda x: x.score, reverse=True)
        ]

    async def broadcast(self, message: dict, exclude: Optional[str] = None):
        disconnected = []
        for client_id, player in self.players.items():
            if exclude and client_id == exclude:
                continue
            try:
                await player.websocket.send_json(message)
            except Exception as e:
                logger.error(f"Error sending to {client_id}: {e}")
                disconnected.append(client_id)

        for client_id in disconnected:
            self.remove_player(client_id)

class GameManager:
    def __init__(self):
        self.games: Dict[str, Game] = {}

    def create_game(self, game_id: str) -> Game:
        if game_id not in self.games:
            self.games[game_id] = Game(game_id)
            logger.info(f"Game {game_id} created")
        return self.games[game_id]

    def get_game(self, game_id: str) -> Optional[Game]:
        return self.games.get(game_id)

    def delete_game(self, game_id: str):
        if game_id in self.games:
            del self.games[game_id]
            logger.info(f"Game {game_id} deleted")

manager = GameManager()

@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "active_games": len(manager.games),
        "games": [
            {
                "game_id": g.game_id,
                "players": len(g.players),
                "state": g.state
            }
            for g in manager.games.values()
        ]
    }


@app.websocket("/ws/{game_id}/{client_id}")
async def websocket_endpoint(websocket: WebSocket, game_id: str, client_id: str):
    game = manager.create_game(game_id)

    await websocket.accept()

    if not game.add_player(client_id, websocket):
        await websocket.send_json({
            "type": "error",
            "message": "Game is full or you're already connected"
        })
        await websocket.close()
        return

    await game.broadcast({
        "type": "player_joined",
        "client_id": client_id,
        "total_players": len(game.players),
        "players": list(game.players.keys()),
        "can_start": game.can_start()
    })

    await websocket.send_json({
        "type": "game_state",
        "state": game.state,
        "players": list(game.players.keys()),
        "can_start": game.can_start()
    })

    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            message_type = message.get("type")

            if message_type == "start_game":
                if not game.can_start():
                    await websocket.send_json({
                        "type": "error",
                        "message": f"Need at least {MIN_PLAYERS} players to start"
                    })
                    continue

                if not await game.fetch_questions():
                    await websocket.send_json({
                        "type": "error",
                        "message": "Failed to load questions"
                    })
                    continue

                game.state = "playing"
                game.current_question_index = 0
                game.reset_answers()

                await game.broadcast({
                    "type": "game_started",
                    "total_questions": len(game.questions)
                })

                question = game.get_current_question()
                if question:
                    await game.broadcast({
                        "type": "question",
                        **question
                    })

            elif message_type == "answer":
                if game.state != "playing":
                    continue

                if client_id in game.answered_players:
                    await websocket.send_json({
                        "type": "error",
                        "message": "You already answered this question"
                    })
                    continue

                answer = message.get("answer", "")
                is_correct = game.check_answer(client_id, answer)

                game.answered_players.add(client_id)
                game.players[client_id].has_answered = True

                correct_answer = game.questions[game.current_question_index]["correct_answer"]

                await websocket.send_json({
                    "type": "answer_result",
                    "correct": is_correct,
                    "your_score": game.players[client_id].score,
                    "correct_answer": correct_answer,
                    "your_answer": answer
                })

                await game.broadcast({
                    "type": "player_answered",
                    "client_id": client_id,
                    "correct": is_correct,
                    "answered_count": len(game.answered_players),
                    "total_players": len(game.players)
                }, exclude=client_id)

                if game.all_players_answered():
                    async with game.question_lock:
                        await asyncio.sleep(ANSWER_DISPLAY_TIME)

                        game.current_question_index += 1
                        game.reset_answers()

                        if game.current_question_index < len(game.questions):
                            question = game.get_current_question()
                            if question:
                                await game.broadcast({
                                    "type": "question",
                                    **question
                                })
                        else:
                            game.state = "finished"
                            leaderboard = game.get_leaderboard()
                            await game.broadcast({
                                "type": "game_finished",
                                "leaderboard": leaderboard
                            })

            elif message_type == "chat":
                await game.broadcast({
                    "type": "chat",
                    "client_id": client_id,
                    "message": message.get("message", "")
                }, exclude=client_id)

    except WebSocketDisconnect:
        game.remove_player(client_id)
        await game.broadcast({
            "type": "player_left",
            "client_id": client_id,
            "total_players": len(game.players),
            "can_start": game.can_start()
        })

        if len(game.players) == 0:
            manager.delete_game(game_id)
    except Exception as e:
        logger.error(f"Error in websocket for {client_id}: {e}")
        game.remove_player(client_id)
