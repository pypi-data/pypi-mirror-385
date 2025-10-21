# StreamDeckLayoutManager

[![GPL-v3.0](https://img.shields.io/badge/license-GPL--3.0-orange)](https://spdx.org/licenses/GPL-3.0-or-later.html) [![PyPI - Python Version](https://img.shields.io/pypi/pyversions/StreamDeckLayoutManager.svg)](https://python.org) [![PyPI - Version](https://img.shields.io/pypi/v/StreamDeckLayoutManager.svg)](https://pypi.org/project/StreamDeckLayoutManager)

A higher-level **Python** API for ElGato's [Stream Deck](https://www.elgato.com/en/stream-deck-mk2).

This module is based off and uses [streamdeck-elgato-python](https://github.com/abcminiuser/python-elgato-streamdeck) from [Dean Camera](https://github.com/abcminiuser).

### Installation

**StreamDeckLayoutManager** is a pure Python project. It requires at least [Python](https://python.org) 3.8.

You can install **StreamDeckLayoutManager** by typing the following in a terminal window:

```console
pip install StreamDeckLayoutManager
```

### Usage

You can use **StreamDeckLayoutManager** in your own **Python** scripts like this:

```
import StreamDeckLayoutManager

streamdeck_manager = StreamDeckLayoutManager.Manager('StreamDeckConfig.toml')
streamdeck_manager.display_page('MyPageName')
```

In order to receive key press/release information, you need to hook up at least one callback:

```
streamdeck_manager.set_callback('MyCallbackName', callback_method)
```

Callback method will receive a `List` of arguments, as provided by the key configuration, minus the callback name:

```
def streamdeck_callback(arguments):
    # -- If the key's action is [ 'MyCallbackName', 'test', 42 ]
    # -- then arguments in this case will be [ 'test', 42 ]
    ...
```

### Config file format

Config files are regular [`toml`](https://toml.io/en/) files. They have a general section named `config`:

```
[config]
Brightness = 90
AssetFolder = 'assets'
Font = 'Roboto-Regular.ttf'
FontSize = 11
StartPage = 'MyPageName'
```

`AssetFolder` is relative to the folder where the config file is found.

They also have entries for each page:

```
[MyPageName]
Key13Image = 'MyIcon.png'
Key13Label = 'My Label'
Key13PressedActions = [[ 'MyCallbackName', 'test', 42 ]]
Key13ReleasedActions = [[ 'MyCallbackName', 'other_test' ]]
...
```

The page contains numbered entries for each key from `Key0` to `Key14` (if you are using an original stream deck). Each entry lists the image to use, the text to display underneath the image and the callback to call when the key is pressed or when it is released.

Image path is relative to the asset folder provided in the `config` section.

Callback names such as `push_page`, `pop_page` and `display_page` are reserved and can be used to moved between pages, including creating folders

```
Key14Image = 'folder.png'
Key14Label = 'MyFolder'
Key14PressedActions = [[ 'push_page', 'SamplePage1' ]]
```

This callback will push the current page onto a stack and display the page `SamplePage1`.

```
Key14Image = 'back.png'
Key14Label = 'Go Back'
Key14PressedActions = [[ 'pop_page' ]]
```

This callback will pop the previous page from a stack and display it again.

```
Key9Image = 'other.png'
Key9Label = 'NextPage'
Key9PressedActions = [[ 'display_page', 'SamplePage2' ]]
```

This callback will simply display it the page `SamplePage2`. The page stack is unaffected and only the current page is modified.

As seen in the action settings, multiple callbacks can be set for each 'pressed' and 'released' actions.

### StreamDeckLayoutManager.Manager class

##### `Manager(config_file_path: str, deck_index: int = 0) -> None`

Initialize a new manager for stream deck at index `deck_index` using the config file at `config_file_path`.

##### `Manager.shutdown() -> None`

Shuts down the manager.

##### `Manager.display_page(page_name: str) -> None`

Display page named `page_name`.

##### `Manager.push_page(page_name: str) -> None`

Push current page onto the stack and display page named `page_name`.

##### `Manager.pop_page() -> None`

Pop the previous page off the stack and display it.

##### `Manager.set_key(page_name: str, key_index: int, image_file: Optional[str], label: Optional[str], 
                       pressed_callbacks: Optional[Tuple[CallbackCall]] = None,
                       released_callbacks: Optional[Tuple[CallbackCall]] = None) -> None`

Set the key in page named `page_name` at index `key_index` to display image at `image_file` with label `label`. When key is pressed then `pressed_callbacks` are called, when the key is released then `released_callbacks` are called.

Image path is relative to the asset folder provided in the `config` section.

This can be used to set keys dynamically, as opposed to statically in the config file.

For example:

```
streamdeck_manager.set_key('MainPage', 12, 'MyImage.png', 'My Label',
                           StreamDeckLayoutManager.CallbackCall(['MyCallbackName', 'test_argument', 2]))
```

##### `Manager.set_callback(self, callback_name: str,
                            callback: Callable[[StreamDeckLayoutManager.CallbackCall], None]) -> None`

Set the callback method for callback `callback_name` to the method `callback`.

##### `Manager.number_of_stream_decks -> int`

Return the number of stream decks found.

##### `Manager.print_deck_info(self, index: int)`

Prints diagnostic information about the stream deck at index `index`.

### License

**StreamDeckLayoutManager** is distributed under the terms of the [GPLv3.0](https://spdx.org/licenses/GPL-3.0-or-later.html) or later license.
