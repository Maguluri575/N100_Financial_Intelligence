"""
=========================================================
sqlite_manager.py

SQLite Manager

Author : Hareesh
=========================================================
"""

import pandas as pd

from .db import get_connection


class SQLiteManager:

    def __init__(self):

        self.conn = get_connection()

    # ---------------------------------------------------

    def save_dataframe(self,
                       dataframe,
                       table_name):

        dataframe.to_sql(

            table_name,

            self.conn,

            if_exists="replace",

            index=False

        )

        print(f"{table_name} Saved Successfully")

    # ---------------------------------------------------

    def append_dataframe(self,
                         dataframe,
                         table_name):

        dataframe.to_sql(

            table_name,

            self.conn,

            if_exists="append",

            index=False

        )

        print(f"{table_name} Appended Successfully")

    # ---------------------------------------------------

    def read_table(self,
                   table_name):

        query = f"""

        SELECT *

        FROM {table_name}

        """

        return pd.read_sql(

            query,

            self.conn

        )

    # ---------------------------------------------------

    def execute(self,
                query):

        cursor = self.conn.cursor()

        cursor.execute(query)

        self.conn.commit()

    # ---------------------------------------------------

    def count_rows(self,
                   table_name):

        cursor = self.conn.cursor()

        cursor.execute(

            f"""

            SELECT COUNT(*)

            FROM {table_name}

            """

        )

        return cursor.fetchone()[0]

    # ---------------------------------------------------

    def table_exists(self,
                     table_name):

        cursor = self.conn.cursor()

        cursor.execute("""

        SELECT name

        FROM sqlite_master

        WHERE type='table'

        AND name=?

        """,

        (table_name,))

        return cursor.fetchone() is not None

    # ---------------------------------------------------

    def delete_table(self,
                     table_name):

        cursor = self.conn.cursor()

        cursor.execute(

            f"""

            DROP TABLE IF EXISTS {table_name}

            """

        )

        self.conn.commit()

    # ---------------------------------------------------

    def close(self):

        self.conn.close()