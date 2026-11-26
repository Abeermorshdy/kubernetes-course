import os
import pymysql
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

APP_TITLE = os.getenv("APP_TITLE", "Guestbook")

MYSQL_WRITE_HOST = os.getenv("MYSQL_WRITE_HOST", "mysql-write")
MYSQL_READ_HOST = os.getenv("MYSQL_READ_HOST", "mysql-read")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))

MYSQL_USER = os.getenv("MYSQL_USER", "appuser")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "guestbook")

app = FastAPI(title=APP_TITLE)


class Message(BaseModel):
    name: str
    message: str


def write_connection():
    return pymysql.connect(
        host=MYSQL_WRITE_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DATABASE,
        autocommit=True,
    )


def read_connection():
    return pymysql.connect(
        host=MYSQL_READ_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DATABASE,
        autocommit=True,
    )


@app.on_event("startup")
def prepare_database():
    connection = write_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS messages (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    message TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
    finally:
        connection.close()


@app.get("/api/info")
def info():
    return {
        "app": APP_TITLE,
        "write_database": MYSQL_WRITE_HOST,
        "read_database": MYSQL_READ_HOST,
        "status": "running",
    }


@app.get("/api/messages")
def list_messages():
    connection = read_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT id, name, message, created_at FROM messages ORDER BY id DESC"
            )
            rows = cursor.fetchall()
            return [
                {
                    "id": row[0],
                    "name": row[1],
                    "message": row[2],
                    "created_at": str(row[3]),
                }
                for row in rows
            ]
    finally:
        connection.close()


@app.post("/api/messages")
def create_message(item: Message):
    connection = write_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO messages (name, message) VALUES (%s, %s)",
                (item.name, item.message),
            )
            return {"status": "created", "name": item.name}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    finally:
        connection.close()
