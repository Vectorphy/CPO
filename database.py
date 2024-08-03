# database.py

import sqlite3
import asyncio

class Database:
    def __init__(self, db_name='bot_database.sqlite'):
        self.db_name = db_name
        self.conn = None
        self.lock = asyncio.Lock()

    async def connect(self):
        self.conn = sqlite3.connect(self.db_name)
        await self.create_tables()

    async def create_tables(self):
        async with self.lock:
            cursor = self.conn.cursor()
            
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS study_groups (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                creator_id INTEGER NOT NULL,
                max_size INTEGER NOT NULL,
                end_time REAL NOT NULL,
                guild_id INTEGER NOT NULL,
                admin_role_id INTEGER,
                session_role_id INTEGER,
                voice_channel_id INTEGER
            )
            ''')

            cursor.execute('''
            CREATE TABLE IF NOT EXISTS group_members (
                group_id INTEGER,
                user_id INTEGER,
                FOREIGN KEY (group_id) REFERENCES study_groups (id),
                PRIMARY KEY (group_id, user_id)
            )
            ''')

            cursor.execute('''
            CREATE TABLE IF NOT EXISTS pomodoro_sessions (
                id INTEGER PRIMARY KEY,
                group_id INTEGER,
                start_time REAL,
                end_time REAL,
                focus_duration INTEGER,
                short_break_duration INTEGER,
                long_break_duration INTEGER,
                FOREIGN KEY (group_id) REFERENCES study_groups (id)
            )
            ''')

            cursor.execute('''
            CREATE TABLE IF NOT EXISTS managers (
                id INTEGER PRIMARY KEY,
                user_id INTEGER NOT NULL,
                guild_id INTEGER,
                permission_level INTEGER NOT NULL
            )
            ''')

            self.conn.commit()

    async def close(self):
        if self.conn:
            self.conn.close()

    async def create_study_group(self, name, creator_id, max_size, end_time, guild_id):
        async with self.lock:
            cursor = self.conn.cursor()
            cursor.execute('''
            INSERT INTO study_groups (name, creator_id, max_size, end_time, guild_id, admin_role_id, session_role_id, voice_channel_id)
            VALUES (?, ?, ?, ?, ?, NULL, NULL, NULL)
            ''', (name, creator_id, max_size, end_time, guild_id))
            group_id = cursor.lastrowid
            self.conn.commit()
            return group_id

    async def get_study_group(self, guild_id):
        async with self.lock:
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM study_groups WHERE guild_id = ?', (guild_id,))
            return cursor.fetchone()

    async def delete_study_group(self, group_id):
        async with self.lock:
            cursor = self.conn.cursor()
            cursor.execute('DELETE FROM study_groups WHERE id = ?', (group_id,))
            cursor.execute('DELETE FROM group_members WHERE group_id = ?', (group_id,))
            self.conn.commit()

    async def add_group_member(self, group_id, user_id):
        async with self.lock:
            cursor = self.conn.cursor()
            cursor.execute('''
            INSERT OR IGNORE INTO group_members (group_id, user_id)
            VALUES (?, ?)
            ''', (group_id, user_id))
            self.conn.commit()

    async def remove_group_member(self, group_id, user_id):
        async with self.lock:
            cursor = self.conn.cursor()
            cursor.execute('''
            DELETE FROM group_members
            WHERE group_id = ? AND user_id = ?
            ''', (group_id, user_id))
            self.conn.commit()

    async def get_group_members(self, group_id):
        async with self.lock:
            cursor = self.conn.cursor()
            cursor.execute('SELECT user_id FROM group_members WHERE group_id = ?', (group_id,))
            return [row[0] for row in cursor.fetchall()]

    async def update_group_roles(self, group_id, admin_role_id, session_role_id):
        async with self.lock:
            cursor = self.conn.cursor()
            cursor.execute('''
            UPDATE study_groups
            SET admin_role_id = ?, session_role_id = ?
            WHERE id = ?
            ''', (admin_role_id, session_role_id, group_id))
            self.conn.commit()

    async def get_group_roles(self, group_id):
        async with self.lock:
            cursor = self.conn.cursor()
            cursor.execute('SELECT admin_role_id, session_role_id FROM study_groups WHERE id = ?', (group_id,))
            return cursor.fetchone()

    async def update_voice_channel(self, group_id, voice_channel_id):
        async with self.lock:
            cursor = self.conn.cursor()
            cursor.execute('''
            UPDATE study_groups
            SET voice_channel_id = ?
            WHERE id = ?
            ''', (voice_channel_id, group_id))
            self.conn.commit()

    async def get_user_group(self, user_id):
        async with self.lock:
            cursor = self.conn.cursor()
            cursor.execute('''
            SELECT study_groups.* FROM study_groups
            JOIN group_members ON study_groups.id = group_members.group_id
            WHERE group_members.user_id = ?
            ''', (user_id,))
            return cursor.fetchone()

    # Manager methods (unchanged)
    # ... (keep the existing manager methods)

    # Pomodoro methods (unchanged)
    # ... (keep the existing pomodoro methods)