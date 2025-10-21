#
# Copyright (c) 2022-present Didier Malenfant <didier@malenfant.net>
#
# This file is part of StreamDeckLayoutManager.
#
# StreamDeckLayoutManager is free software: you can redistribute it and/or modify it under the terms of the GNU General
# Public License as published by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# StreamDeckLayoutManager is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the
# implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public
# License for more details.
#
# You should have received a copy of the GNU General Public License along with StreamDeckLayoutManager. If not,
# see <https://www.gnu.org/licenses/>.
#

from typing import List, Optional
from pathlib import Path

from StreamDeckLayoutManager.CallbackCall import CallbackCall


# -- Classes
class KeyConfig:
    """Configuration for a given key."""

    def __init__(self, image: Optional[Path] = None, label: Optional[str] = None):
        self.image = image
        self.label = label
        self.margins: List[int] = []
        self.pressed_callbacks: List[CallbackCall] = []
        self.released_callbacks: List[CallbackCall] = []
