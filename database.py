import os
import sqlite3
import uuid
import datetime
from typing import Optional, Dict, Any, Tuple

if os.environ.get("VERCEL"):
    DB_PATH = "/tmp/users.db"
else:
    DB_PATH = os.path.join(os.path.dirname(__file__), "data", "users.db")

class Database:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        try:
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        except Exception:
            pass
        self.init_db()

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                telegram_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                language TEXT DEFAULT 'uz',
                free_checks_left INTEGER DEFAULT 1,
                paid_checks_left INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_check_at TIMESTAMP
            )
            """)

            # Add language column if migrating existing database
            try:
                cursor.execute("ALTER TABLE users ADD COLUMN language TEXT DEFAULT 'uz'")
            except Exception:
                pass

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                order_id TEXT PRIMARY KEY,
                telegram_id INTEGER,
                amount_uzs INTEGER,
                checks_count INTEGER,
                provider TEXT,
                status TEXT DEFAULT 'PENDING',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                paid_at TIMESTAMP,
                FOREIGN KEY (telegram_id) REFERENCES users(telegram_id)
            )
            """)
            conn.commit()

    def set_user_language(self, telegram_id: int, lang: str):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET language = ? WHERE telegram_id = ?", (lang, telegram_id))
            conn.commit()

    def get_or_create_user(self, telegram_id: int, username: str = "", first_name: str = "") -> Dict[str, Any]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
            row = cursor.fetchone()
            if row:
                # Update username or first_name if changed
                cursor.execute("""
                    UPDATE users SET username = ?, first_name = ? WHERE telegram_id = ?
                """, (username, first_name, telegram_id))
                conn.commit()
                return dict(row)

            # Create new user with 1 FREE trial check
            cursor.execute("""
                INSERT INTO users (telegram_id, username, first_name, free_checks_left, paid_checks_left)
                VALUES (?, ?, ?, 1, 0)
            """, (telegram_id, username, first_name))
            conn.commit()
            
            cursor.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
            return dict(cursor.fetchone())

    def get_user_status(self, telegram_id: int) -> Optional[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
            row = cursor.fetchone()
            if not row:
                return None
            data = dict(row)
            data["total_checks_left"] = data["free_checks_left"] + data["paid_checks_left"]
            data["can_check"] = data["total_checks_left"] > 0
            return data

    def can_perform_check(self, telegram_id: int) -> Tuple[bool, int, str]:
        """
        Returns (can_check, total_left, check_type_to_use)
        check_type_to_use: 'free', 'paid', or 'none'
        """
        user = self.get_or_create_user(telegram_id)
        free_left = user.get("free_checks_left", 0)
        paid_left = user.get("paid_checks_left", 0)
        total = free_left + paid_left

        if free_left > 0:
            return True, total, "free"
        elif paid_left > 0:
            return True, total, "paid"
        else:
            return False, 0, "none"

    def deduct_check(self, telegram_id: int) -> bool:
        """
        Deducts 1 check (free first, then paid).
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT free_checks_left, paid_checks_left FROM users WHERE telegram_id = ?", (telegram_id,))
            row = cursor.fetchone()
            if not row:
                return False

            free_left, paid_left = row["free_checks_left"], row["paid_checks_left"]
            now = datetime.datetime.utcnow().isoformat()

            if free_left > 0:
                cursor.execute("""
                    UPDATE users 
                    SET free_checks_left = free_checks_left - 1, last_check_at = ?
                    WHERE telegram_id = ?
                """, (now, telegram_id))
                conn.commit()
                return True
            elif paid_left > 0:
                cursor.execute("""
                    UPDATE users 
                    SET paid_checks_left = paid_checks_left - 1, last_check_at = ?
                    WHERE telegram_id = ?
                """, (now, telegram_id))
                conn.commit()
                return True

            return False

    def create_order(self, telegram_id: int, amount_uzs: int, checks_count: int, provider: str = "click") -> str:
        order_id = str(uuid.uuid4())[:12]
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO orders (order_id, telegram_id, amount_uzs, checks_count, provider, status)
                VALUES (?, ?, ?, ?, ?, 'PENDING')
            """, (order_id, telegram_id, amount_uzs, checks_count, provider))
            conn.commit()
        return order_id

    def complete_order(self, order_id: str) -> bool:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM orders WHERE order_id = ? AND status = 'PENDING'", (order_id,))
            order = cursor.fetchone()
            if not order:
                return False

            now = datetime.datetime.utcnow().isoformat()
            cursor.execute("""
                UPDATE orders SET status = 'PAID', paid_at = ? WHERE order_id = ?
            """, (now, order_id))

            # Add paid checks to user balance
            cursor.execute("""
                UPDATE users SET paid_checks_left = paid_checks_left + ? WHERE telegram_id = ?
            """, (order["checks_count"], order["telegram_id"]))

            conn.commit()
            return True

    def get_stats(self) -> Dict[str, Any]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM users")
            total_users = cursor.fetchone()["count"]

            cursor.execute("SELECT COUNT(*) as count FROM orders WHERE status = 'PAID'")
            paid_orders = cursor.fetchone()["count"]

            cursor.execute("SELECT SUM(amount_uzs) as total FROM orders WHERE status = 'PAID'")
            sum_row = cursor.fetchone()
            total_revenue = sum_row["total"] if sum_row["total"] else 0

            return {
                "total_users": total_users,
                "paid_orders": paid_orders,
                "total_revenue_uzs": total_revenue
            }
