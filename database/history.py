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
    def __init__(self, guild_id: int):
        super().__init__("toss")
        self._guild_id = guild_id
        self._data_dict = {}

        if self._table_exists(f"g_{self._guild_id}"):
            lookup = self._lookup_record(f"g_{self._guild_id}")
            for data in lookup:
                self._data_dict[data[0]] = literal_eval(Storage(data[1]).un_base64())

        if self._table_exists("guild_settings"):
            lookup = self._lookup_record(f"guild_settings", f"guild_id = {self._guild_id}")
            if lookup:
                self._settings = {"intro_channel": lookup[0][1], "log_channel": lookup[0][2]}
            else:
                self._settings = {"intro_channel": 0, "log_channel": 0}

        else:
            self._make_table(f"guild_settings", [
                ("guild_id", "INTEGER PRIMARY KEY"),
                ("intro_channel", "INTEGER"),
                ("log_channel", "INTEGER")
            ])

            self.__init__(guild_id)

    def _check_tables(self) -> None:
        if not self._table_exists(f"g_{self._guild_id}"):
            self._make_table(f"g_{self._guild_id}", [("user_id", "INTEGER"), ("message_base64", "TEXT")])
            self._data_dict = {}

            self._settings = {"intro_channel": 0, "log_channel": 0}

    def _commit_user(self, user_id: int = None) -> None:
        current_users = [data[0] for data in self._lookup_record(f"g_{self._guild_id}")]

        if user_id is None:
            for user_id in self._data_dict:
                base64 = Storage(str(self._data_dict[user_id])).do_base64()

                if user_id in current_users:
                    self._update_record(f"g_{self._guild_id}", [("message_base64", f"'{base64}'")], f"user_id = {user_id}")

                else:
                    self._add_record(f"g_{self._guild_id}", [("user_id", user_id), ("message_base64", f"'{base64}'")])

        else:
            base64 = Storage(str(self._data_dict[user_id])).do_base64()

            if user_id in current_users:
                self._update_record(f"g_{self._guild_id}", [("message_base64", f"'{base64}'")], f"user_id = {user_id}")

            else:
                self._add_record(f"g_{self._guild_id}", [("user_id", user_id), ("message_base64", f"'{base64}'")])

    def _commit_settings(self):
        current_setting_guilds = [data[0] for data in self._lookup_record(f"guild_settings")]
        if self._guild_id in current_setting_guilds:
            self._update_record("guild_settings", [
                ("intro_channel", self._settings["intro_channel"]),
                ("log_channel", self._settings["log_channel"])
            ])
        else:
            self._add_record("guild_settings", [
                ("guild_id", self._guild_id),
                ("intro_channel", self._settings["intro_channel"]),
                ("log_channel", self._settings["log_channel"])
            ])

    def manual_commit(self) -> None:
        self._commit_user()
        self._commit_settings()

    def add(self, user_id: int, message_id: int, commit: bool = True) -> None:
        self._check_tables()

        if user_id in self._data_dict:
            if message_id not in self._data_dict[user_id]:
                self._data_dict[user_id].append(message_id)
        else:
            self._data_dict[user_id] = [message_id]

        if commit:
            self._commit_user(user_id)

    def get(self, user_id: int, ids: bool = False) -> int:
        self._check_tables()

        if user_id not in self._data_dict:
            return 0

        if ids:
            return self._data_dict[user_id]
        return len(self._data_dict[user_id])

    def get_from_message_id(self, message_id: int) -> int:
        self._check_tables()

        for user_id in self._data_dict:
            if message_id in self._data_dict[user_id]:
                return user_id

        return 0

    def remove(self, user_id: int, message_id: int, commit: bool = True) -> None:
        self._check_tables()

        if user_id not in self._data_dict:
            return

        if message_id not in self._data_dict[user_id]:
            return

        self._data_dict[user_id].remove(message_id)

        if commit:
            self._commit_user()

    def set_channel_intro(self, channel_id: int, commit: bool = True) -> None:
        self._settings["intro_channel"] = channel_id

        if commit:
            self._commit_settings()

    def set_channel_log(self, channel_id: int, commit: bool = True) -> None:
        self._settings["log_channel"] = channel_id

        if commit:
            self._commit_settings()

    def get_intro_channel(self) -> int:
        return self._settings["intro_channel"] or 0

    def get_log_channel(self) -> int:
        return self._settings["log_channel"] or 0

    def show_over_threshhold(self, threshold: int) -> dict:
        self._check_tables()
        above_threshold_list = {}

        for user_id in self._data_dict:
            if len(self._data_dict[user_id]) >= threshold:
                above_threshold_list[user_id] = len(self._data_dict[user_id])

        return above_threshold_list
