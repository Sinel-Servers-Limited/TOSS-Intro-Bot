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

from ast import literal_eval
from database import Database
from database.storage import Storage


class History(Database):
    """ Class for high-level management of history database """
    def __init__(self, channel_id: int):
        super().__init__("toss")
        self.channel_id = channel_id

        if not self._table_exists(f"c_{channel_id}"):
            self._make_table(f"c_{channel_id}", [("user_id", "INTEGER PRIMARY KEY"), ("message_base64", "TEXT")])
            self.data_dict = {}

        else:
            lookup = self._lookup_record(f"c_{channel_id}")
            for data in lookup:
                self.data_dict[data[0]] = literal_eval(Storage(data[1]).un_base64())

    def _commit(self, user_id: int = None) -> None:
        """ Commit changes

        :param user_id: The user id to update the info of
        """
        current_users = [data[0] for data in self._lookup_record(f"c_{self.channel_id}")]

        if user_id is None:
            for user_id in self.data_dict:
                base64 = Storage(str(self.data_dict[user_id])).do_base64()

                if user_id in current_users:
                    self._update_record(f"c_{self.channel_id}", [("message_base64", f"'{base64}'")], f"user_id = {user_id}")

                else:
                    self._add_record(f"c_{self.channel_id}", [("user_id", user_id), ("message_base64", f"'{base64}'")])

        else:
            base64 = Storage(str(self.data_dict[user_id])).do_base64()

            if user_id in current_users:
                self._update_record(f"c_{self.channel_id}", [("message_base64", f"'{base64}'")], f"user_id = {user_id}")

            else:
                self._add_record(f"c_{self.channel_id}", [("user_id", user_id), ("message_base64", f"'{base64}'")])

    def add(self, user_id: int, message_id: int, commit: bool = True) -> None:
        if user_id in self.data_dict:
            self.data_dict[user_id].append(message_id)
        else:
            self.data_dict[user_id] = [message_id]

        if commit:
            self._commit(user_id)

    def remove(self, user_id: int, message_id: int, commit: bool = True) -> None:
        if user_id not in self.data_dict:
            return

        self.data_dict[user_id].remove(message_id)

        if commit:
            self._commit()



