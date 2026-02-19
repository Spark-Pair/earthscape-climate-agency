import sqlite3
from contextlib import contextmanager
from datetime import datetime
from typing import Iterable, Optional

DB_NAME = "earthscape.db"


@contextmanager
def get_connection(db_path: str = DB_NAME):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def now_utc() -> str:
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")


def init_db(db_path: str = DB_NAME) -> None:
    with get_connection(db_path) as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('admin', 'analyst')),
                fullname TEXT NOT NULL DEFAULT '',
                is_active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS datasets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dataset_name TEXT NOT NULL,
                uploaded_by INTEGER NOT NULL,
                upload_time TEXT NOT NULL,
                raw_csv_text TEXT NOT NULL,
                FOREIGN KEY (uploaded_by) REFERENCES users(id)
            );

            CREATE TABLE IF NOT EXISTS dataset_access (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dataset_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                granted_by INTEGER NOT NULL,
                granted_at TEXT NOT NULL,
                UNIQUE(dataset_id, user_id),
                FOREIGN KEY (dataset_id) REFERENCES datasets(id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (granted_by) REFERENCES users(id)
            );

            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                subject TEXT NOT NULL,
                message TEXT NOT NULL,
                created_at TEXT NOT NULL,
                status TEXT NOT NULL CHECK(status IN ('open', 'closed')) DEFAULT 'open',
                FOREIGN KEY (user_id) REFERENCES users(id)
            );

            CREATE TABLE IF NOT EXISTS performance_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                action_name TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                execution_time_ms REAL NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );
            """
        )
        _migrate_users_table(conn)


def _migrate_users_table(conn: sqlite3.Connection) -> None:
    cols = {row["name"] for row in conn.execute("PRAGMA table_info(users)").fetchall()}
    if "fullname" not in cols:
        conn.execute("ALTER TABLE users ADD COLUMN fullname TEXT NOT NULL DEFAULT ''")
    if "is_active" not in cols:
        conn.execute("ALTER TABLE users ADD COLUMN is_active INTEGER NOT NULL DEFAULT 1")


def create_user(
    username: str,
    password_hash: str,
    role: str,
    fullname: str = "",
    is_active: int = 1,
) -> int:
    with get_connection() as conn:
        cur = conn.execute(
            """
            INSERT INTO users (username, password_hash, role, fullname, is_active, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (username, password_hash, role, fullname, is_active, now_utc()),
        )
        return cur.lastrowid


def get_user_by_username(username: str) -> Optional[sqlite3.Row]:
    with get_connection() as conn:
        return conn.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()


def get_user_by_id(user_id: int) -> Optional[sqlite3.Row]:
    with get_connection() as conn:
        return conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()


def list_users(role: Optional[str] = None) -> list[sqlite3.Row]:
    with get_connection() as conn:
        if role:
            return conn.execute(
                "SELECT * FROM users WHERE role = ? ORDER BY username", (role,)
            ).fetchall()
        return conn.execute("SELECT * FROM users ORDER BY role, username").fetchall()


def list_analysts() -> list[sqlite3.Row]:
    return list_users(role="analyst")


def user_count(role: Optional[str] = None) -> int:
    with get_connection() as conn:
        if role:
            row = conn.execute(
                "SELECT COUNT(*) AS c FROM users WHERE role = ?", (role,)
            ).fetchone()
        else:
            row = conn.execute("SELECT COUNT(*) AS c FROM users").fetchone()
        return int(row["c"])


def set_user_active(user_id: int, is_active: int) -> None:
    with get_connection() as conn:
        conn.execute("UPDATE users SET is_active = ? WHERE id = ?", (is_active, user_id))


def insert_dataset(dataset_name: str, uploaded_by: int, raw_csv_text: str) -> int:
    with get_connection() as conn:
        cur = conn.execute(
            """
            INSERT INTO datasets (dataset_name, uploaded_by, upload_time, raw_csv_text)
            VALUES (?, ?, ?, ?)
            """,
            (dataset_name, uploaded_by, now_utc(), raw_csv_text),
        )
        return cur.lastrowid


def list_datasets_for_admin() -> list[sqlite3.Row]:
    with get_connection() as conn:
        return conn.execute(
            """
            SELECT d.id, d.dataset_name, d.upload_time, d.uploaded_by,
                   u.username AS uploaded_by_username,
                   COUNT(da.id) AS assigned_users
            FROM datasets d
            JOIN users u ON d.uploaded_by = u.id
            LEFT JOIN dataset_access da ON da.dataset_id = d.id
            GROUP BY d.id
            ORDER BY d.upload_time DESC
            """
        ).fetchall()


def list_datasets_for_user(user_id: int, role: str) -> list[sqlite3.Row]:
    with get_connection() as conn:
        if role == "admin":
            return conn.execute(
                """
                SELECT d.id, d.dataset_name, d.upload_time, u.username AS uploaded_by_username
                FROM datasets d
                JOIN users u ON d.uploaded_by = u.id
                ORDER BY d.upload_time DESC
                """
            ).fetchall()

        return conn.execute(
            """
            SELECT d.id, d.dataset_name, d.upload_time, u.username AS uploaded_by_username
            FROM datasets d
            JOIN dataset_access da ON da.dataset_id = d.id
            JOIN users u ON d.uploaded_by = u.id
            WHERE da.user_id = ?
            ORDER BY d.upload_time DESC
            """,
            (user_id,),
        ).fetchall()


def get_dataset_by_id(dataset_id: int) -> Optional[sqlite3.Row]:
    with get_connection() as conn:
        return conn.execute(
            """
            SELECT d.*, u.username AS uploaded_by_username
            FROM datasets d
            JOIN users u ON d.uploaded_by = u.id
            WHERE d.id = ?
            """,
            (dataset_id,),
        ).fetchone()


def grant_dataset_access(dataset_id: int, user_id: int, granted_by: int) -> None:
    with get_connection() as conn:
        conn.execute(
            """
            INSERT OR IGNORE INTO dataset_access (dataset_id, user_id, granted_by, granted_at)
            VALUES (?, ?, ?, ?)
            """,
            (dataset_id, user_id, granted_by, now_utc()),
        )


def grant_dataset_access_bulk(dataset_id: int, user_ids: Iterable[int], granted_by: int) -> None:
    user_ids = list(user_ids)
    if not user_ids:
        return
    with get_connection() as conn:
        conn.executemany(
            """
            INSERT OR IGNORE INTO dataset_access (dataset_id, user_id, granted_by, granted_at)
            VALUES (?, ?, ?, ?)
            """,
            [(dataset_id, uid, granted_by, now_utc()) for uid in user_ids],
        )


def list_dataset_access(dataset_id: int) -> list[sqlite3.Row]:
    with get_connection() as conn:
        return conn.execute(
            """
            SELECT da.id, da.dataset_id, da.user_id, da.granted_by, da.granted_at,
                   u.username AS analyst_username,
                   g.username AS granted_by_username
            FROM dataset_access da
            JOIN users u ON da.user_id = u.id
            JOIN users g ON da.granted_by = g.id
            WHERE da.dataset_id = ?
            ORDER BY u.username
            """,
            (dataset_id,),
        ).fetchall()


def revoke_dataset_access(dataset_id: int, user_id: int) -> None:
    with get_connection() as conn:
        conn.execute(
            "DELETE FROM dataset_access WHERE dataset_id = ? AND user_id = ?",
            (dataset_id, user_id),
        )


def delete_dataset(dataset_id: int) -> None:
    with get_connection() as conn:
        conn.execute("DELETE FROM datasets WHERE id = ?", (dataset_id,))


def insert_feedback(user_id: int, subject: str, message: str) -> int:
    with get_connection() as conn:
        cur = conn.execute(
            """
            INSERT INTO feedback (user_id, subject, message, created_at, status)
            VALUES (?, ?, ?, ?, 'open')
            """,
            (user_id, subject, message, now_utc()),
        )
        return cur.lastrowid


def list_feedback_for_user(user_id: int) -> list[sqlite3.Row]:
    with get_connection() as conn:
        return conn.execute(
            """
            SELECT f.*, u.username
            FROM feedback f
            JOIN users u ON f.user_id = u.id
            WHERE f.user_id = ?
            ORDER BY f.created_at DESC
            """,
            (user_id,),
        ).fetchall()


def list_all_feedback() -> list[sqlite3.Row]:
    with get_connection() as conn:
        return conn.execute(
            """
            SELECT f.*, u.username
            FROM feedback f
            JOIN users u ON f.user_id = u.id
            ORDER BY f.created_at DESC
            """
        ).fetchall()


def update_feedback_status(feedback_id: int, status: str) -> None:
    with get_connection() as conn:
        conn.execute(
            "UPDATE feedback SET status = ? WHERE id = ?", (status, feedback_id)
        )


def delete_feedback(feedback_id: int) -> None:
    with get_connection() as conn:
        conn.execute("DELETE FROM feedback WHERE id = ?", (feedback_id,))


def log_performance(user_id: Optional[int], action_name: str, execution_time_ms: float) -> int:
    with get_connection() as conn:
        cur = conn.execute(
            """
            INSERT INTO performance_logs (user_id, action_name, timestamp, execution_time_ms)
            VALUES (?, ?, ?, ?)
            """,
            (user_id, action_name, now_utc(), execution_time_ms),
        )
        return cur.lastrowid


def list_performance_logs(limit: int = 1000) -> list[sqlite3.Row]:
    with get_connection() as conn:
        return conn.execute(
            """
            SELECT p.*, u.username
            FROM performance_logs p
            LEFT JOIN users u ON p.user_id = u.id
            ORDER BY p.timestamp DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
