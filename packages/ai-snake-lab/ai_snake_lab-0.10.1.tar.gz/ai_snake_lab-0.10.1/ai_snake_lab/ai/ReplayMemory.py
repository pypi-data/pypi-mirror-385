"""
ai/ReplayMemory.py

    AI Snake Game Simulator
    Author: Nadim-Daniel Ghaznavi
    Copyright: (c) 2024-2025 Nadim-Daniel Ghaznavi
    GitHub: https://github.com/NadimGhaznavi/ai
    License: GPL 3.0

This file contains the ReplayMemory class.
"""

import os
import random
import sqlite3, pickle
from pathlib import Path

from ai_snake_lab.constants.DReplayMemory import MEM_TYPE, MEM
from ai_snake_lab.constants.DDef import DDef
from ai_snake_lab.constants.DDir import DDir
from ai_snake_lab.constants.DFile import DFile


class ReplayMemory:

    def __init__(self, seed: int):
        random.seed(seed)
        self.batch_size = 250
        # Valid options: shuffle, random_game or none
        self._mem_type = MEM_TYPE.RANDOM_GAME
        self.min_games = MEM.MIN_GAMES

        # All of the states for a game are stored, in order.
        self.cur_memory = []

        # The snake lab stores temporary and persistent files in this directory
        snake_dir = os.path.join(Path.home(), DDir.DOT + DDir.AI_SNAKE_LAB)
        if not os.path.exists(snake_dir):
            os.mkdir(snake_dir)
        self.db_file = os.path.join(snake_dir, DFile.RUNTIME_DB)
        if os.path.exists(self.db_file):
            os.remove(self.db_file)

        # Connect to SQLite
        self.conn = sqlite3.connect(self.db_file, check_same_thread=False)

        # Get a cursor
        self.cursor = self.conn.cursor()

        # Intialize the schema
        self.init_db()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass  # avoid errors on interpreter shutdown

    def append(self, transition, final_score=None):
        """Add a transition to the current game."""
        if self.mem_type() == MEM_TYPE.NONE:
            return

        (old_state, move, reward, new_state, done) = transition

        self.cur_memory.append((old_state, move, reward, new_state, done))

        if done:
            if final_score is None:
                raise ValueError("final_score must be provided when the game ends")

            total_frames = len(self.cur_memory)

            # Record the game
            self.cursor.execute(
                "INSERT INTO games (score, total_frames) VALUES (?, ?)",
                (final_score, total_frames),
            )
            game_id = self.cursor.lastrowid

            # Record the frames
            for i, (state, action, reward, next_state, done) in enumerate(
                self.cur_memory
            ):
                self.cursor.execute(
                    """
                    INSERT INTO frames (game_id, frame_index, state, action, reward, next_state, done)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        game_id,
                        i,
                        pickle.dumps(state),
                        pickle.dumps(action),
                        reward,
                        pickle.dumps(next_state),
                        done,
                    ),
                )

            self.conn.commit()
            self.cur_memory = []

    def clear_runtime_data(self):
        """Clear all data out of the runtime DB"""
        self.cursor.execute("DELETE FROM games")
        self.cursor.execute("DELETE FROM frames")
        self.conn.commit()

    def close(self):
        """Close the database connection."""
        if getattr(self, "conn", None):
            self.conn.close()
            self.conn = None
        if getattr(self, "db_file", None) and os.path.exists(self.db_file):
            os.remove(self.db_file)
            self.db_file = None

    def get_average_game_length(self):
        self.cursor.execute("SELECT AVG(total_frames) FROM games")
        avg = self.cursor.fetchone()[0]
        return int(avg) if avg else 0

    def get_random_frames(self):
        """Return a random set of frames from the database. Do not use the SQLite3
        RANDOM() function, because we can't set the seed."""
        num_frames = self.get_average_game_length() or 32  # fallback if no data

        # Retrieve the id values from the frames table
        self.cursor.execute("SELECT id FROM frames")
        all_ids = [row[0] for row in self.cursor.fetchall()]

        # Get n random ids
        sample_ids = random.sample(all_ids, min(num_frames, len(all_ids)))
        if not sample_ids:
            return []

        # Build placeholders for the SQL IN clause
        placeholders = ",".join("?" for _ in sample_ids)

        # Execute the query with the unpacked tuple
        self.cursor.execute(
            f"SELECT state, action, reward, next_state, done FROM frames WHERE id IN ({placeholders})",
            sample_ids,
        )
        rows = self.cursor.fetchall()
        frames = [
            (
                pickle.loads(state_blob),
                pickle.loads(action),
                float(reward),
                pickle.loads(next_state_blob),
                bool(done),
            )
            for state_blob, action, reward, next_state_blob, done in rows
        ]
        return frames, len(frames)

    def get_random_game(self):
        self.cursor.execute("SELECT id FROM games")
        all_ids = [row[0] for row in self.cursor.fetchall()]
        if not all_ids or len(all_ids) < self.min_games:
            return [], MEM.NO_DATA  # no games available

        rand_id = random.choice(all_ids)
        self.cursor.execute(
            "SELECT state, action, reward, next_state, done "
            "FROM frames WHERE game_id = ? ORDER BY frame_index ASC",
            (rand_id,),
        )
        rows = self.cursor.fetchall()
        if not rows:
            return [], rand_id  # game exists but no frames

        game = [
            (
                pickle.loads(state_blob),
                pickle.loads(action),
                float(reward),
                pickle.loads(next_state_blob),
                bool(done),
            )
            for state_blob, action, reward, next_state_blob, done in rows
        ]
        return game, rand_id

    def get_num_games(self):
        """Return number of games stored in the database."""
        self.cursor.execute("SELECT COUNT(*) FROM games")
        return self.cursor.fetchone()[0]

    def get_num_frames(self):
        """Return number of frames stored in the database."""
        self.cursor.execute("SELECT COUNT(*) FROM frames")
        return self.cursor.fetchone()[0]

    def get_training_data(self):
        mem_type = self.mem_type()

        if mem_type == MEM_TYPE.NONE:
            return None, MEM.NO_DATA  # No data available

        # RANDOM_GAME mode: return full ordered frames from one random game
        elif mem_type == MEM_TYPE.RANDOM_GAME:
            frames, game_id = self.get_random_game()
            if not frames:  # no frames available
                return None, MEM.NO_DATA
            training_data = frames
            metadata = game_id

        # SHUFFLE mode: return a random set of frames
        elif mem_type == MEM_TYPE.SHUFFLE:
            frames, num_frames = self.get_random_frames()
            if not frames:  # no frames available
                return None, MEM.NO_DATA
            training_data = frames
            metadata = num_frames

        else:
            raise ValueError(f"Unknown memory type: {mem_type}")

        # Split into arrays for vectorized training
        states = [d[0] for d in training_data]
        actions = [d[1] for d in training_data]
        rewards = [d[2] for d in training_data]
        next_states = [d[3] for d in training_data]
        dones = [d[4] for d in training_data]

        return (states, actions, rewards, next_states, dones), metadata

    def init_db(self):
        # Create the games table
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS games (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                score INTEGER NOT NULL,
                total_frames INTEGER NOT NULL
            );
            """
        )
        self.conn.commit()

        # Create the frames table
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS frames (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                game_id INTEGER NOT NULL,
                frame_index INTEGER NOT NULL,
                state BLOB NOT NULL,
                action BLOB NOT NULL,      
                reward INTEGER NOT NULL,
                next_state BLOB NOT NULL,
                done INTEGER NOT NULL,        -- 0 or 1
                FOREIGN KEY (game_id) REFERENCES games(id)
            );
            """
        )
        self.conn.commit()

        # Create the unique index
        self.cursor.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS idx_game_frame ON frames (game_id, frame_index);
            """
        )
        self.conn.commit()

        # Create the index on game_id
        self.cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_frames_game_id ON frames (game_id);
            """
        )
        self.conn.commit()

        # If the games or frames tables do exist, clear the data
        self.clear_runtime_data()

    def mem_type(self, mem_type=None):
        if mem_type is not None:
            self._mem_type = mem_type
        return self._mem_type

    def set_memory(self, memory):
        self.memory = memory
