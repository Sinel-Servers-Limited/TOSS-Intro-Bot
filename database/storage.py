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

import base64


class Storage:
    def __init__(self, text: str):
        self.text = text

    def do_base64(self):
        self.text = base64.b64encode(bytes(self.text, "utf-8")).decode("utf-8")
        return self.text

    def un_base64(self):
        self.text = base64.b64decode(self.text).decode("utf-8")
        return self.text
