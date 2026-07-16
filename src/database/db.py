"""
=========================================================
db.py

Database Connection

Author : Hareesh
=========================================================
"""

import sqlite3
import os

DATABASE_FOLDER = "database"
DATABASE_NAME = "financial_intelligence.db"


def get_connection():
    """
    Create SQLite Connection
    """

    os.makedirs(DATABASE_FOLDER, exist_ok=True)

    db_path = os.path.join(
        DATABASE_FOLDER,
        DATABASE_NAME
    )

    conn = sqlite3.connect(db_path)

    return conn


def close_connection(conn):
    """
    Close SQLite Connection
    """

    if conn:
        conn.close()


def execute_query(query):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(query)

    conn.commit()

    conn.close()


def execute_many(query, values):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.executemany(query, values)

    conn.commit()

    conn.close()


def fetch_all(query):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(query)

    rows = cursor.fetchall()

    conn.close()

    return rows