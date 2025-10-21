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

from typing import List, Any


# -- Classes
class CallbackCall:
    """Call with arguments passed to a callback function."""

    def __init__(self, method_and_arguments: List[Any]):
        """Initialize the arguments."""
        if len(method_and_arguments) == 0:
            raise RuntimeError('Callback call needs at least a name.')

        if not isinstance(method_and_arguments[0], str):
            raise RuntimeError('Invalid type for method (should be str).')

        self._name: str = method_and_arguments[0]
        self._arguments = method_and_arguments[1:]

    @property
    def name(self) -> str:
        return self._name

    @property
    def number_of_arguments(self) -> int:
        return len(self._arguments)

    def argument_at_index(self, at_index: int = 0) -> Any:
        if at_index < 0 or at_index >= self.number_of_arguments:
            raise RuntimeError('Invalid argument index.')

        return self._arguments[at_index]

    def argument_as_integer(self, at_index: int = 0) -> int:
        if at_index < 0 or at_index >= self.number_of_arguments:
            raise RuntimeError('Invalid argument index.')

        argument = self._arguments[at_index]
        if not isinstance(argument, int):
            raise RuntimeError('Invalid argument type.')

        return argument

    def argument_as_boolean(self, at_index: int = 0) -> bool:
        if at_index < 0 or at_index >= self.number_of_arguments:
            raise RuntimeError('Invalid argument index.')

        argument = self._arguments[at_index]
        if not isinstance(argument, bool):
            raise RuntimeError('Invalid argument type.')

        return argument

    def argument_as_string(self, at_index: int = 0) -> str:
        if at_index < 0 or at_index >= self.number_of_arguments:
            raise RuntimeError('Invalid argument index.')

        argument = self._arguments[at_index]
        if not isinstance(argument, str):
            raise RuntimeError('Invalid argument type.')

        return argument

    def subcall(self) -> "CallbackCall":
        if self.number_of_arguments < 2:
            raise RuntimeError('Not enough arguments to convert call to a subcall.')

        return CallbackCall(self._arguments)
