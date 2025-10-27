'use client';

import { useState, useEffect, useRef } from 'react';

type GameState = 'menu' | 'lobby' | 'playing' | 'finished';

interface Player {
  client_id: string;
  score?: number;
}

interface Question {
  question_number: number;
  total_questions: number;
  question_text: string;
  question_id: number;
}

export default function GamePage() {
  // State management for game lifecycle
  const [gameState, setGameState] = useState<GameState>('menu');
  const [gameId, setGameId] = useState('');
  const [clientId, setClientId] = useState('');
  const [ws, setWs] = useState<WebSocket | null>(null);
  const [players, setPlayers] = useState<string[]>([]);
  const [currentQuestion, setCurrentQuestion] = useState<Question | null>(null);
  const [answer, setAnswer] = useState('');
  const [score, setScore] = useState(0);
  const [leaderboard, setLeaderboard] = useState<Player[]>([]);
  const [message, setMessage] = useState('');
  const [canStart, setCanStart] = useState(false);
  const [feedback, setFeedback] = useState<{text: string, type: 'success' | 'error', correctAnswer?: string, yourAnswer?: string} | null>(null);
  const [answeredCount, setAnsweredCount] = useState(0);
  const [totalPlayers, setTotalPlayers] = useState(0);

  // useRef to maintain WebSocket instance across
  const wsRef = useRef<WebSocket | null>(null);

 // cleanup WS connection on component unmount
  useEffect(() => {
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);
  // generate ids for games/players
  const generateGameId = () => {
    return 'game_' + Math.random().toString(36).substr(2, 9);
  };

  const generateClientId = () => {
    return 'player_' + Math.random().toString(36).substr(2, 9);
  };
  // WS connection
  const connectToGame = (gId: string, cId: string) => {
    const wsUrl = `ws://localhost/ws/${gId}/${cId}`;
    const websocket = new WebSocket(wsUrl);

    websocket.onopen = () => {
      console.log('Connected to game');
      setGameState('lobby');
      setMessage('Connected to game!');
    };

    websocket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log('Received:', data);

      switch (data.type) {
        case 'player_joined':
          setPlayers(data.players);
          setMessage(`Player ${data.client_id} joined! (${data.total_players} players)`);
          break;

        case 'player_left':
          setPlayers(data.players || []);
          setMessage(`Player ${data.client_id} left`);
          break;

        case 'game_state':
          setPlayers(data.players);
          setCanStart(data.can_start);
          break;

        case 'game_started':
          setGameState('playing');
          setMessage(`Game started! ${data.total_questions} questions`);
          setScore(0);
          break;

        case 'question':
          setCurrentQuestion({
            question_number: data.question_number,
            total_questions: data.total_questions,
            question_text: data.question_text,
            question_id: data.question_id,
          });
          setAnswer('');
          setFeedback(null);
          break;

        case 'answer_result':
          setScore(data.your_score);
          setFeedback({
            text: data.correct ? 'Correct!' : 'Wrong!',
            type: data.correct ? 'success' : 'error',
            correctAnswer: data.correct_answer,
            yourAnswer: data.your_answer
          });
          break;

        case 'player_answered':
          const status = data.correct ? 'W' : 'L';
          setMessage(`${status} ${data.client_id} answered!`);
          break;

        case 'game_finished':
          setGameState('finished');
          setLeaderboard(data.leaderboard);
          setCurrentQuestion(null);
          break;

        case 'error':
          setMessage(`Error: ${data.message}`);
          break;
      }
    };

    websocket.onerror = (error) => {
      console.error('WebSocket error:', error);
      setMessage('Connection error!');
    };

    websocket.onclose = () => {
      console.log('Disconnected');
      setMessage('Disconnected from game');
      setGameState('menu');
    };
    //store WS reference
    wsRef.current = websocket;
    setWs(websocket);
  };
  // game control funcs
  const startNewGame = () => {
    const gId = generateGameId();
    const cId = generateClientId();
    setGameId(gId);
    setClientId(cId);
    connectToGame(gId, cId);
  };

  const joinExistingGame = () => {
    if (!gameId.trim()) {
      alert('Please enter Game ID');
      return;
    }
    const cId = generateClientId();
    setClientId(cId);
    connectToGame(gameId.trim(), cId);
  };

  const startGame = () => {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type: 'start_game' }));
    }
  };

  const submitAnswer = () => {
    if (!answer.trim()) return;
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ type: 'answer', answer: answer.trim() }));
    }
  };
  // cleanup and reset game state
  const leaveGame = () => {
    if (wsRef.current) {
      wsRef.current.close();
    }
    setGameState('menu');
    setGameId('');
    setClientId('');
    setPlayers([]);
    setCurrentQuestion(null);
    setScore(0);
    setLeaderboard([]);
    setMessage('');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-500 via-pink-500 to-red-500 p-8">
      <div className="max-w-4xl mx-auto">
        {/* Main Menu */}
        {gameState === 'menu' && (
          <div className="bg-white rounded-2xl shadow-2xl p-10">
            <h1 className="text-5xl font-bold text-center mb-8 text-gray-800">
                Quiz Game
            </h1>

            <div className="space-y-6">
              <button
                onClick={startNewGame}
                className="w-full bg-green-500 hover:bg-green-600 text-white text-xl font-bold py-6 rounded-xl transition-all transform hover:scale-105 shadow-lg"
              >
                START NEW GAME
              </button>

              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-gray-300"></div>
                </div>
                <div className="relative flex justify-center text-sm">
                  <span className="px-4 bg-white text-gray-500 font-medium">OR</span>
                </div>
              </div>

              <div className="space-y-3">
                <input
                  type="text"
                  value={gameId}
                  onChange={(e) => setGameId(e.target.value)}
                  placeholder="Enter Game ID"
                  className="w-full border-2 border-gray-300 rounded-xl p-4 text-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none"
                />
                <button
                  onClick={joinExistingGame}
                  className="w-full bg-blue-500 hover:bg-blue-600 text-white text-xl font-bold py-6 rounded-xl transition-all transform hover:scale-105 shadow-lg"
                >
                    CONNECT TO GAME
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Lobby */}
        {gameState === 'lobby' && (
          <div className="bg-white rounded-2xl shadow-2xl p-10">
            <h1 className="text-4xl font-bold text-center mb-6 text-gray-800">
              Game Lobby
            </h1>

            <div className="mb-6 p-4 bg-blue-50 rounded-xl border-2 border-blue-200">
              <p className="text-sm text-gray-600 mb-1">Game ID:</p>
              <p className="text-2xl font-mono font-bold text-blue-600">{gameId}</p>
              <p className="text-xs text-gray-500 mt-2">Share this ID with friends</p>
            </div>

            <div className="mb-8">
              <h3 className="text-xl font-semibold mb-4 text-gray-700">
                Players ({players.length}/8):
              </h3>
              <div className="space-y-2">
                {players.map((player) => (
                  <div
                    key={player}
                    className={`p-3 rounded-lg ${
                      player === clientId
                        ? 'bg-green-100 border-2 border-green-400'
                        : 'bg-gray-100'
                    }`}
                  >
                    <span className="font-medium">
                      {player === clientId ? '-> YOU' : player}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {message && (
              <div className="mb-6 p-4 bg-yellow-50 border-l-4 border-yellow-400 rounded">
                <p className="text-yellow-800">{message}</p>
              </div>
            )}

            <div className="space-y-3">
              <button
                onClick={startGame}
                disabled={!canStart}
                className={`w-full text-xl font-bold py-6 rounded-xl transition-all ${
                  canStart
                    ? 'bg-green-500 hover:bg-green-600 text-white transform hover:scale-105 shadow-lg'
                    : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                }`}
              >
                {canStart ? 'START GAME' : 'Waiting for players (minimum 2 players!)'}
              </button>

              <button
                onClick={leaveGame}
                className="w-full bg-red-500 hover:bg-red-600 text-white font-bold py-4 rounded-xl transition-all"
              >
                Leave Game
              </button>
            </div>
          </div>
        )}

        {/* Playing */}
        {gameState === 'playing' && currentQuestion && (
          <div className="bg-white rounded-2xl shadow-2xl p-10">
            <div className="mb-6 flex justify-between items-center">
              <div className="text-lg font-semibold text-gray-600">
                Question {currentQuestion.question_number}/{currentQuestion.total_questions}
              </div>
              <div className="text-2xl font-bold text-green-600">
                Score: {score}
              </div>
            </div>

            <div className="mb-8 p-6 bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl border-2 border-blue-200">
              <h2 className="text-2xl font-bold text-gray-800 mb-4">
                {currentQuestion.question_text}
              </h2>
            </div>

            {message && (
              <div className="mb-6 p-3 bg-blue-50 border-l-4 border-blue-400 rounded text-blue-800 text-center font-medium">
                {message}
              </div>
            )}

            {feedback && (
              <div className={`mb-6 p-6 rounded-xl ${
                feedback.type === 'success'
                  ? 'bg-green-100 border-2 border-green-300'
                  : 'bg-red-100 border-2 border-red-300'
              }`}>
                <div className="text-center text-2xl font-bold mb-3">
                  {feedback.text}
                </div>
                {!feedback.type.includes('success') && (
                  <div className="space-y-2 text-center">
                    <div className="text-red-700">
                      <span className="font-semibold">Your answer:</span>{' '}
                      <span className="line-through">{feedback.yourAnswer}</span>
                    </div>
                    <div className="text-green-700 text-lg">
                      <span className="font-semibold">Correct answer:</span>{' '}
                      <span className="font-bold">{feedback.correctAnswer}</span>
                    </div>
                  </div>
                )}
              </div>
            )}

            <div className="space-y-4">
              <input
                type="text"
                value={answer}
                onChange={(e) => setAnswer(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && submitAnswer()}
                placeholder="Type your answer..."
                className="w-full border-2 border-gray-300 rounded-xl p-4 text-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none"
                disabled={feedback !== null}
              />

              <button
                onClick={submitAnswer}
                disabled={!answer.trim() || feedback !== null}
                className={`w-full text-xl font-bold py-6 rounded-xl transition-all ${
                  answer.trim() && !feedback
                    ? 'bg-blue-500 hover:bg-blue-600 text-white transform hover:scale-105 shadow-lg'
                    : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                }`}
              >
                Submit Answer
              </button>
            </div>
          </div>
        )}

        {/* Finished */}
        {gameState === 'finished' && (
          <div className="bg-white rounded-2xl shadow-2xl p-10">
            <h1 className="text-4xl font-bold text-center mb-8 text-gray-800">
                STATISTICS
            </h1>

            <div className="mb-8">
              <h2 className="text-2xl font-semibold mb-4 text-gray-700">Leaderboard:</h2>
              <div className="space-y-3">
                {leaderboard.map((player, index) => (
                  <div
                    key={player.client_id}
                    className={`p-4 rounded-xl flex justify-between items-center ${
                      index === 0
                        ? 'bg-yellow-100 border-2 border-yellow-400'
                        : index === 1
                        ? 'bg-gray-100 border-2 border-gray-300'
                        : index === 2
                        ? 'bg-orange-100 border-2 border-orange-300'
                        : 'bg-gray-50'
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <span className="text-2xl font-bold text-gray-600">
                        #{index + 1}
                      </span>
                      <span className="font-medium">
                        {player.client_id === clientId ? '👤 You' : player.client_id}
                      </span>
                    </div>
                    <span className="text-2xl font-bold text-green-600">
                      {player.score} pts
                    </span>
                  </div>
                ))}
              </div>
            </div>

            <button
              onClick={leaveGame}
              className="w-full bg-blue-500 hover:bg-blue-600 text-white text-xl font-bold py-6 rounded-xl transition-all transform hover:scale-105 shadow-lg"
            >
                Back to Menu
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
