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

import sys

try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib  # type: ignore
    except ImportError:
        # -- This is just to quiet a warning about tomllib not defined in this case
        import enum as tomllib  # type: ignore
        sys.exit('Error: This program requires either tomllib or tomli but neither is available')

from StreamDeck.Devices import StreamDeck
from StreamDeck.DeviceManager import DeviceManager
from StreamDeck.ImageHelpers import PILHelper

from PIL import Image, ImageFont, ImageDraw
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Any, Callable
from PyUtilities.Exceptions import ArgumentError

from StreamDeckLayoutManager.CallbackCall import CallbackCall
from StreamDeckLayoutManager.KeyConfig import KeyConfig


# -- Classes
class Manager:
    """Manage all our Stream Deck interactions."""

    @classmethod
    def _key_name(cls, key_index: int) -> str:
        return f'Key{key_index}'

    @classmethod
    def _page_and_key_name(cls, page_name: str, key_index: int) -> str:
        return f'{page_name}_{Manager._key_name(key_index)}'

    def __init__(self, config_file_path: Path, deck_index: int = 0):
        """Initialize the manager based on user configuration."""

        self._key_configs: Dict[str, KeyConfig] = {}
        self._assets_folder: Optional[Path] = None
        self._font: Optional[ImageFont.FreeTypeFont] = None
        self._callbacks: Dict[str, Callable[[CallbackCall], None]] = {'display_page': self._display_page_callback,
                                                                      'push_page': self._push_page_callback,
                                                                      'pop_page': self._pop_page_callback}
        self._page_stack: List[str] = []
        self._pressed_keys: Dict[str, bool] = {}

        self._stream_decks = DeviceManager().enumerate()
        self._nb_of_stream_decks: int = len(self._stream_decks)

        if self._nb_of_stream_decks == 0:
            raise RuntimeError('StreamDeckLayoutManager: Could not find any StreamDecks.')

        if deck_index >= self._nb_of_stream_decks:
            raise RuntimeError('StreamDeckLayoutManager: Ouf of bounds deck_index.')

        self._deck = self._stream_decks[deck_index]
        if not self._deck.is_visual():
            raise RuntimeError('StreamDeckLayoutManager: StreamDeck does not have any screens.')

        self._deck.open()
        self._deck.reset()

        self._number_of_keys = self._deck.key_count()

        self.clear_page()

        self._init_config(config_file_path)

        # -- Register callback function for when a key state changes.
        self._deck.set_key_callback(self._key_change_callback)

    def _set_key_config(self, page_name: str, key_index: int, config: KeyConfig) -> None:
        self._key_configs[Manager._page_and_key_name(page_name=page_name, key_index=key_index)] = config

    def _get_key_config(self, page_name: str, key_index: int) -> Optional[KeyConfig]:
        return self._key_configs.get(Manager._page_and_key_name(page_name=page_name, key_index=key_index))

    def _init_config(self, config_file_path: Path) -> None:
        if not config_file_path.exists():
            raise RuntimeError(f'StreamDeckLayoutManager: Cannot read config file at "{config_file_path}".')

        data: Optional[Dict[str, Any]] = None

        try:
            with open(config_file_path, mode="rb") as fp:
                data = tomllib.load(fp)

            if data is None:
                raise RuntimeError

        except Exception as e:
            raise RuntimeError(f'StreamDeckLayoutManager: Cannot read config file at "{config_file_path}" ({e}).')

        starting_page: Optional[str] = None

        for config_section, value in data.items():
            if config_section == 'config':
                folder_path = value.get('AssetFolder')
                if folder_path is None:
                    raise RuntimeError(f'StreamDeckLayoutManager: Missing "AssetFolder" in "{config_file_path}".')

                self._assets_folder = folder_path if folder_path.startswith('/') else (
                    Path(config_file_path).parent / folder_path)

                font_file = value.get('Font')
                if font_file is None:
                    raise RuntimeError(f'StreamDeckLayoutManager: Missing "Font" in "{config_file_path}".')

                font_size = value.get('FontSize')
                if font_size is None:
                    raise RuntimeError(f'StreamDeckLayoutManager: Missing "FontSize" in "{config_file_path}".')

                self._font = ImageFont.truetype(self._assets_folder / font_file, font_size)

                brightness = value.get('Brightness')
                if brightness is not None:
                    self.set_brightness(brightness)

                starting_page = value.get('StartPage')
            else:
                if starting_page is None:
                    starting_page = config_section

                for i in range(self._number_of_keys):
                    key_name = Manager._key_name(i)

                    image_name = value.get(key_name + 'Image')
                    label = value.get(key_name + 'Label')

                    if image_name is None:
                        continue

                    if self._get_key_config(page_name=config_section, key_index=i) is not None:
                        raise ArgumentError(f'StreamDeckLayoutManager: Found multiple configurations for '
                                            f'page "{config_section}" and key "{i}".')

                    key_config = KeyConfig()
                    key_config.image = Path(image_name)
                    key_config.label = label

                    margins = value.get(key_name + 'ImageMargins')
                    if margins is not None:
                        if not isinstance(margins, List):
                            raise ArgumentError(f'StreamDeckLayoutManager: Invalid margins for '
                                                f'page "{config_section}" and key "{i}".')

                        for margin in margins:
                            if not isinstance(margin, int):
                                raise ArgumentError(f'StreamDeckLayoutManager: Invalid margins for '
                                                    f'page "{config_section}" and key "{i}".')

                        key_config.margins = margins

                    pressed_actions = value.get(key_name + 'PressedActions')
                    if pressed_actions is not None:
                        for action in pressed_actions:
                            key_config.pressed_callbacks.append(CallbackCall(action))
                    else:
                        pressed_action = value.get(key_name + 'PressedAction')
                        if pressed_action is not None:
                            key_config.pressed_callbacks.append(CallbackCall(pressed_action))

                    released_actions = value.get(key_name + 'ReleasedActions')
                    if released_actions is not None:
                        for action in released_actions:
                            key_config.released_callbacks.append(CallbackCall(action))
                    else:
                        released_action = value.get(key_name + 'ReleasedAction')
                        if released_action is not None:
                            key_config.released_callbacks.append(CallbackCall(released_action))

                    self._set_key_config(page_name=config_section, key_index=i, config=key_config)

        if self._assets_folder is None:
            raise RuntimeError(f'StreamDeckLayoutManager: Missing "config" section in "{config_file_path}".')

        if starting_page is None:
            raise RuntimeError(f'StreamDeckLayoutManager: Could not find a starting page in "{config_file_path}".')

        self.display_page(starting_page)

    # -- Generates a custom tile with run-time generated text and custom image via the PIL module.
    def _render_key_image(self, image_filename: Path, label: Optional[str] = None) -> bytes:
        # Resize the source image asset to best-fit the dimensions of a single key,
        # leaving a margin at the bottom so that we can draw the key title
        # afterward.
        icon = Image.open(image_filename)
        image: Image.Image = PILHelper.create_scaled_image(self._deck, icon, margins=(0, 0, 20, 0))

        # Load a custom TrueType font and use it to overlay the key index, draw key
        # label onto the image a few pixels from the bottom of the key.
        draw = ImageDraw.Draw(image)
        if label is not None:
            draw.text((image.width / 2, image.height - 5), text=label, font=self._font, anchor='ms', fill='white')

        return PILHelper.to_native_key_format(self._deck, image)

    def _set_key_image(self, key_index: int, image_file: Optional[Path], label: Optional[str]) -> None:
        if image_file is None or self._assets_folder is None:
            return

        image_filename = image_file if image_file.is_relative_to(Path('/')) else self._assets_folder / image_file

        # Generate the custom key with the requested image and label.
        image = self._render_key_image(image_filename, label)

        # -- Use a scoped-with on the deck to ensure we're the only thread using it right now.
        with self._deck:
            # -- Update requested key with the generated image.
            self._deck.set_key_image(key_index, image)

    # -- Associated actions when a key is pressed.
    def _key_change_callback(self, deck: StreamDeck, key_index: int, state: bool) -> None:  # type: ignore
        if self._deck is None or len(self._page_stack) == 0 or deck != self._deck:
            return

        current_page_name = self._page_stack[-1]
        key_config = self._get_key_config(page_name=current_page_name, key_index=key_index)
        if key_config is None:
            return

        if state:
            actions = key_config.pressed_callbacks
            self._pressed_keys[Manager._page_and_key_name(page_name=current_page_name, key_index=key_index)] = True
        else:
            page_and_key_name = Manager._page_and_key_name(page_name=current_page_name, key_index=key_index)
            if self._pressed_keys.get(page_and_key_name) is None:
                # -- The key was not pressed before, or maybe we switched page since the key was pressed.
                return

            actions = key_config.released_callbacks

            self._pressed_keys.pop(page_and_key_name, None)

        for action in actions:
            callback = self._callbacks.get(action.name)
            if callback is None:
                raise RuntimeError(f'StreamDeckLayoutManager: Unknown callback "{action.name}".')

            callback(action)

    def _update_page(self, page_name: str) -> None:
        self.clear_page()

        for key_index in range(self._number_of_keys):
            key_config = self._get_key_config(page_name=page_name, key_index=key_index)
            if key_config is None:
                continue

            image_file = key_config.image
            label = key_config.label

            self._set_key_image(key_index=key_index, image_file=image_file, label=label)

    def _display_page_callback(self, call: CallbackCall) -> None:
        if call.number_of_arguments != 1:
            raise RuntimeError('StreamDeckLayoutManager: Invalid arguments to display_page action.')

        self.display_page(call.argument_as_string(at_index=0))

    def _push_page_callback(self, call: CallbackCall) -> None:
        if call.number_of_arguments != 1:
            raise RuntimeError('StreamDeckLayoutManager: Invalid arguments to push_page action.')

        current_page_index = len(self._page_stack) - 1
        if current_page_index < 0:
            raise RuntimeError('StreamDeckLayoutManager: No current page set before calling pushPage().')

        self.push_page(call.argument_as_string(at_index=0))

    def _pop_page_callback(self, call: CallbackCall) -> None:
        if call.number_of_arguments != 0:
            raise RuntimeError('StreamDeckLayoutManager: Invalid arguments to pop_page action.')

        current_page_index = len(self._page_stack) - 1
        if current_page_index < 1:
            raise RuntimeError('StreamDeckLayoutManager: No page to pop when calling popPage().')

        self.pop_page()

    def set_brightness(self, percentage: int) -> None:
        self._deck.set_brightness(percentage)

    def clear_page(self) -> None:
        self._pressed_keys = {}

        for key_index in range(self._number_of_keys):
            self._deck.set_key_image(key=key_index, image=bytes())

    def display_page(self, name: str) -> None:
        current_page_index = len(self._page_stack) - 1
        if current_page_index < 0:
            self._page_stack.append(name)
        else:
            self._page_stack[current_page_index] = name

        self._update_page(name)

    def push_page(self, name: str) -> None:
        if self._page_stack[-1] == name:
            # -- We are trying to switch to the same page we are already on.
            return

        self._page_stack.append(name)
        self._update_page(name)

    def pop_page(self) -> None:
        if len(self._page_stack) == 1:
            return

        self._page_stack = self._page_stack[:-1]
        self._update_page(self._page_stack[-1])

    def set_key(self, page_name: str, key_index: int, image_file: Optional[Path] = None, label: Optional[str] = None,
                pressed_callbacks: Optional[Tuple[CallbackCall]] = None,
                released_callbacks: Optional[Tuple[CallbackCall]] = None) -> None:
        key_config = self._get_key_config(page_name, key_index)
        if key_config is None:
            key_config = KeyConfig(image=image_file, label=label)
        else:
            key_config.image = image_file
            key_config.label = label

        key_config.pressed_callbacks = list(pressed_callbacks) if pressed_callbacks is not None else []
        key_config.released_callbacks = list(released_callbacks) if released_callbacks is not None else []

        self._set_key_config(page_name=page_name, key_index=key_index, config=key_config)

        # -- If we are currently displaying this page then we update the button too
        if len(self._page_stack) > 0 and page_name == self._page_stack[-1]:
            self._set_key_image(key_index, image_file, label)

    def set_callback(self, callback_name: str, callback: Optional[Callable[[CallbackCall], None]]) -> None:
        if callback_name in ['display_page', 'push_page', 'pop_page']:
            raise ArgumentError(f'StreamDeckLayoutManager: Callback name "{callback_name}" is reserved.')

        if callback is None:
            self._callbacks.pop(callback_name)
        else:
            self._callbacks[callback_name] = callback

    def has_callback_for(self, callback_name: str) -> bool:
        return self._callbacks.get(callback_name) is not None

    def shutdown(self) -> None:
        # -- Use a scoped-with on the deck to ensure we're the only thread using it right now.
        with self._deck:
            # -- Reset deck, clearing all button images.
            self._deck.reset()

            # -- Close deck handle, terminating internal worker threads.
            self._deck.close()

    # -- Return the number of stream decks found.
    @property
    def number_of_stream_decks(self) -> int:
        return self._nb_of_stream_decks

    # -- Prints diagnostic information about a given StreamDeck.
    def print_deck_info(self, index: int) -> None:
        if index >= self._nb_of_stream_decks:
            raise RuntimeError('Out of bounds index for printDeckInfo().')

        deck = self._stream_decks[index]
        image_format = deck.key_image_format()    # type: ignore

        flip_description: Dict[Tuple[bool, bool], str] = {
            (False, False): 'not mirrored',
            (True, False): 'mirrored horizontally',
            (False, True): 'mirrored vertically',
            (True, True): 'mirrored horizontally/vertically',
        }

        print(f'Deck {index} - {deck.deck_type()}.')
        print(f'\t - ID: {deck.id()}')
        print(f'\t - Serial: "{deck.get_serial_number()}"')
        print(f'\t - Firmware Version: "{deck.get_firmware_version()}"')
        print(f'\t - Key Count: {deck.key_count()} (in a {deck.key_layout()[0]}x{deck.key_layout()[1]} grid)')
        if deck.is_visual():
            print(f'\t - Key Images: {image_format["size"][0]}x{image_format["size"][1]} pixels, '
                  f'{image_format["format"]} format, rotated {image_format["rotation"]} degrees, '
                  f'{flip_description[image_format["flip"]]}')
        else:
            print('\t - No Visual Output')
