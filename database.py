# database.py

import sqlite3
import os

# Database file path
DB_FILE = 'cpo_bot.db'

def get_db_connection():
    """Create a database connection and return it"""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # This allows accessing columns by name
    return conn

def init_db():
    """Initialize the database with necessary tables"""
    conn = get_db_connection()
    cur = conn.cursor()

    # Create user_stats table if it doesn't exist
    cur.execute('''
    CREATE TABLE IF NOT EXISTS user_stats (
        user_id INTEGER PRIMARY KEY,
        pomodoro_sessions INTEGER DEFAULT 0,
        checkins INTEGER DEFAULT 0
    )
    ''')

    # Create pomodoro_groups table if it doesn't exist
    cur.execute('''
    CREATE TABLE IF NOT EXISTS pomodoro_groups (
        group_id INTEGER PRIMARY KEY AUTOINCREMENT,
        group_name TEXT NOT NULL UNIQUE,
        creator_id INTEGER NOT NULL
    )
    ''')

    # Create group_members table if it doesn't exist
    cur.execute('''
    CREATE TABLE IF NOT EXISTS group_members (
        group_id INTEGER,
        user_id INTEGER,
        PRIMARY KEY (group_id, user_id),
        FOREIGN KEY (group_id) REFERENCES pomodoro_groups (group_id)
    )
    ''')

    # Create tasks table if it doesn't exist
    cur.execute('''
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        task TEXT NOT NULL,
        completed BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    conn.commit()
    conn.close()

def update_pomodoro_stats(user_id):
    """Increment the Pomodoro session count for a user"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
    INSERT INTO user_stats (user_id, pomodoro_sessions)
    VALUES (?, 1)
    ON CONFLICT(user_id) DO UPDATE SET pomodoro_sessions = pomodoro_sessions + 1
    ''', (user_id,))
    conn.commit()
    conn.close()

def update_checkin_stats(user_id):
    """Increment the check-in count for a user"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
    INSERT INTO user_stats (user_id, checkins)
    VALUES (?, 1)
    ON CONFLICT(user_id) DO UPDATE SET checkins = checkins + 1
    ''', (user_id,))
    conn.commit()
    conn.close()

def get_user_stats(user_id):
    """Retrieve user statistics"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM user_stats WHERE user_id = ?', (user_id,))
    stats = cur.fetchone()
    conn.close()
    return stats

def create_pomodoro_group(group_name, creator_id):
    """Create a new Pomodoro group"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('INSERT INTO pomodoro_groups (group_name, creator_id) VALUES (?, ?)', (group_name, creator_id))
    group_id = cur.lastrowid
    cur.execute('INSERT INTO group_members (group_id, user_id) VALUES (?, ?)', (group_id, creator_id))
    conn.commit()
    conn.close()
    return group_id

def add_group_member(group_id, user_id):
    """Add a member to a Pomodoro group"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('INSERT OR IGNORE INTO group_members (group_id, user_id) VALUES (?, ?)', (group_id, user_id))
    conn.commit()
    conn.close()

def remove_group_member(group_id, user_id):
    """Remove a member from a Pomodoro group"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM group_members WHERE group_id = ? AND user_id = ?', (group_id, user_id))
    conn.commit()
    conn.close()

def get_group_members(group_id):
    """Get all members of a Pomodoro group"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT user_id FROM group_members WHERE group_id = ?', (group_id,))
    members = cur.fetchall()
    conn.close()
    return [member['user_id'] for member in members]

def get_group_by_name(group_name):
    """Get a Pomodoro group by its name"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM pomodoro_groups WHERE group_name = ?', (group_name,))
    group = cur.fetchone()
    conn.close()
    return group

def add_task(user_id, task_description):
    """Add a new task for a user"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('INSERT INTO tasks (user_id, task) VALUES (?, ?)', (user_id, task_description))
    task_id = cur.lastrowid
    conn.commit()
    conn.close()
    return task_id

def complete_task(user_id, task_id):
    """Mark a task as complete"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('UPDATE tasks SET completed = TRUE WHERE id = ? AND user_id = ?', (task_id, user_id))
    success = cur.rowcount > 0
    conn.commit()
    conn.close()
    return success

def get_user_tasks(user_id):
    """Get all tasks for a user"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM tasks WHERE user_id = ? ORDER BY created_at DESC', (user_id,))
    tasks = cur.fetchall()
    conn.close()
    return tasks

# Initialize the database when this module is imported
init_db()