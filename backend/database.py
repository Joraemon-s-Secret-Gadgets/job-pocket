import json
from pymysql.cursors import DictCursor

from common.db import rdb_engine

def get_user(email: str):
    raw_conn = rdb_engine.raw_connection()
    try:
        with raw_conn.cursor(DictCursor) as c:
            sql = "SELECT username, password, email, resume_data FROM users WHERE email = %s"
            c.execute(sql, (email,))
            user = c.fetchone()
            if user:
                return (
                    user["username"],
                    user["password"],
                    user["email"],
                    user["resume_data"],
                )
            return None
    finally:
        raw_conn.close()


def add_user_via_web(name, password_hash, email, resume_data=None):
    raw_conn = rdb_engine.raw_connection()
    try:
        with raw_conn.cursor(DictCursor) as c:
            c.execute("SELECT email FROM users WHERE email = %s", (email,))
            if c.fetchone():
                return False, "이미 가입된 이메일입니다."

            resume_json_str = (
                json.dumps(resume_data, ensure_ascii=False) if resume_data else "{}"
            )
            sql = "INSERT INTO users (username, password, email, resume_data) VALUES (%s, %s, %s, %s)"
            c.execute(sql, (name, password_hash, email, resume_json_str))
            raw_conn.commit()
            return True, "회원가입 성공"
    except Exception as e:
        return False, f"오류 발생: {e}"
    finally:
        raw_conn.close()


def update_password(email, new_password_hash):
    raw_conn = rdb_engine.raw_connection()
    try:
        with raw_conn.cursor(DictCursor) as c:
            sql = "UPDATE users SET password = %s WHERE email = %s"
            c.execute(sql, (new_password_hash, email))
            success = c.rowcount > 0
            raw_conn.commit()
            return success
    finally:
        raw_conn.close()


def update_resume_data(email, resume_data):
    raw_conn = rdb_engine.raw_connection()
    try:
        with raw_conn.cursor(DictCursor) as c:
            resume_json_str = json.dumps(resume_data, ensure_ascii=False)
            sql = "UPDATE users SET resume_data = %s WHERE email = %s"
            c.execute(sql, (resume_json_str, email))
            success = c.rowcount > 0
            raw_conn.commit()
            return success
    finally:
        raw_conn.close()


def save_chat_message(email, role, content):
    raw_conn = rdb_engine.raw_connection()
    try:
        with raw_conn.cursor(DictCursor) as c:
            sql = "INSERT INTO chat_history (user_email, role, content) VALUES (%s, %s, %s)"
            c.execute(sql, (email, role, content))
            raw_conn.commit()
    finally:
        raw_conn.close()


def load_chat_history(email):
    raw_conn = rdb_engine.raw_connection()
    try:
        with raw_conn.cursor(DictCursor) as c:
            sql = "SELECT role, content FROM chat_history WHERE user_email = %s ORDER BY created_at ASC"
            c.execute(sql, (email,))
            rows = (
                c.fetchall()
            )  # DictCursor이므로 [{"role": "...", "content": "..."}, ...] 형태로 바로 나옵니다.
            return rows
    finally:
        raw_conn.close()


def delete_chat_history(email):
    raw_conn = rdb_engine.raw_connection()
    try:
        with raw_conn.cursor(DictCursor) as c:
            sql = "DELETE FROM chat_history WHERE user_email = %s"
            c.execute(sql, (email,))
            raw_conn.commit()
    finally:
        raw_conn.close()
