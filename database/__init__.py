# TOSS-Intro-Bot - Discord Bot
# Copyright (C) 2020 - 2021 Dylan Prins
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.
# If not, see <https://www.gnu.org/licenses/gpl-3.0.txt>.

# You may contact me at toss@sinelservers.xyz

import sqlite3


class Database:
    """ Class for mid-level management of a database"""
    def __init__(self, database_name: str):
        self._db = self._make_connection(database_name)

    def _make_connection(self, name: str) -> sqlite3.Connection:
        """ Returns connection object to database

        :param name: The name of the database
        :return: sqlite3.Connection
        """
        return sqlite3.connect(name + ".db")

    def _close_connection(self) -> None:
        """ Closes connection object """
        self._db.close()

    def _make_cursor(self) -> sqlite3.Cursor:
        """ Returns cursor object to connection object

        :return: sqlite3.Cursor
        """
        return self._db.cursor()

    def _exec_sql_code(self, sqlcode: str) -> list:
        """ Executes SQL code, and commits it.

        :param sqlcode: The SQL code.
        """
        cursor = self._make_cursor()
        cursor.execute(sqlcode)
        self._db.commit()
        return cursor.fetchall()

    def _make_table(self, tablename: str, data: list) -> None:
        """ Makes table in a database

        :param tablename: Name of the table
        :param data: A list of tuples, with the first value being the name of
                     the column and the second being a valid sqllite3 type
        :return: Result from the sql code
        """
        sqlcode = f"CREATE TABLE {tablename} ("
        for column in data:
            sqlcode += f"{column[0]} {column[1]}, "
        sqlcode = sqlcode[:-2] + ");"
        self._exec_sql_code(sqlcode)

    def _delete_table(self, tablename: str):
        """ Deletes a table from a database

        :param tablename: Name of the table
        :return: Result from the sql code
        """
        return self._exec_sql_code(f"DROP TABLE {tablename};")

    def _table_exists(self, tablename: str) -> bool:
        """ Checks if a table exists

        :param tablename: Name of the table
        :return: Whether the table exists
        """
        sqlcode = f"SELECT name FROM sqlite_master WHERE type='table' AND name='{tablename}';"
        return len(self._exec_sql_code(sqlcode)) > 0

    def _lookup_record(self, tablename: str, expression: str = "") -> list:
        """ Looks up a record

        :param tablename: Name of the table
        :param expression: The expression to match records
        :return: A list of matching records
        """
        sqlcode = f"SELECT * FROM {tablename}"
        if expression:
            sqlcode += f" WHERE {expression}"
        sqlcode += ";"
        return self._exec_sql_code(sqlcode)

    def _add_record(self, tablename: str, record_data: list) -> None:
        """ Adds a record to a table on a database

        :param tablename: Name of the table
        :param record_data: List of tuples with the format ("Column name", "data")
        """
        sqlcode = f"INSERT INTO {tablename}("
        values = ""
        for column in record_data:
            sqlcode += f"{column[0]}, "
            values += f"{column[1]}, "
        sqlcode = sqlcode[:-2] + f") VALUES({values[:-2]});"
        self._exec_sql_code(sqlcode)

    def _update_record(self, tablename: str, record_data: list, expression: str = "") -> None:
        """ Updates a record from a database

        :param tablename: Name of the table
        :param record_data: List of tuples with the format ("Column name", "data")
        :param expression: The expression to use when updating certain things
        :return: Result from the sql code
        """
        sqlcode = f"UPDATE {tablename} SET "
        for item in record_data:
            sqlcode += f"{item[0]} = {item[1]}, "
        sqlcode = sqlcode[:-2]

        if expression:
            sqlcode += f" WHERE {expression}"

        sqlcode += ";"
        self._exec_sql_code(sqlcode)

    def _delete_record(self, tablename: str, expression: str = "") -> None:
        """ Deletes a record from a database

        :param tablename: Name of the table
        :param expression: The expression to use when deleting certain things
        :return: Result from the sql code
        """
        sqlcode = f"DELETE FROM {tablename}"
        if expression:
            sqlcode += f" WHERE {expression}"
        sqlcode += ";"
        self._exec_sql_code(sqlcode)
