from flask_login import UserMixin
from .db import get_db_conn, release_db_conn

class User(UserMixin):
    def __init__(self, id, email, password_hash):
        self.id = id
        self.email = email
        self.password = password_hash

    @classmethod
    def get(cls, user_id):
        conn = get_db_conn()
        cur = conn.cursor()
        cur.execute("SELECT id, email, password_hash FROM users WHERE id = %s", (user_id,))
        row = cur.fetchone()
        cur.close()
        release_db_conn(conn)

        if row:
            return cls(id=row[0], email=row[1], password_hash=row[2])
        return None

    @classmethod
    def get_by_email(cls, email):
        """Check if user already exists (has both email and password)"""
        conn = get_db_conn()
        cur = conn.cursor()
        cur.execute("SELECT id, email, password_hash FROM users WHERE email = %s AND password_hash IS NOT NULL", (email,))
        row = cur.fetchone()
        cur.close()
        release_db_conn(conn)

        if row:
            return cls(id=row[0], email=row[1], password_hash=row[2])
        return None

    @classmethod
    def create(cls, email, password_hash):
        """Create a new user OR update anonymous user with password"""
        conn = get_db_conn()
        cur = conn.cursor()

        # Check if user already exists
        cur.execute("SELECT id, password_hash FROM users WHERE email = %s", (email,))
        user = cur.fetchone()

        if user and user[1] is None:
            user_id = user[0]
            cur.execute(
                "UPDATE users SET password_hash = %s WHERE id = %s",
                (password_hash, user_id)
            )
        else:
            # Create new user
            cur.execute(
                "INSERT INTO users (email, password_hash) VALUES (%s, %s) RETURNING id",
                (email, password_hash)
            )
            user_id = cur.fetchone()[0]

        conn.commit()
        cur.close()
        release_db_conn(conn)
        return cls(id=user_id, email=email, password_hash=password_hash)