from __future__ import annotations

import typing

__all__: list[str] = ["Waterloggable"]

class Waterloggable:
    """
    Members:

      No : Cannot be waterlogged.

      Yes : Can be waterlogged.

      Always : Is always waterlogged. (attribute is not stored)
    """

    Always: typing.ClassVar[
        Waterloggable
    ]  # value = amulet.game.java._block.Waterloggable.Always
    No: typing.ClassVar[
        Waterloggable
    ]  # value = amulet.game.java._block.Waterloggable.No
    Yes: typing.ClassVar[
        Waterloggable
    ]  # value = amulet.game.java._block.Waterloggable.Yes
    __members__: typing.ClassVar[
        dict[str, Waterloggable]
    ]  # value = {'No': amulet.game.java._block.Waterloggable.No, 'Yes': amulet.game.java._block.Waterloggable.Yes, 'Always': amulet.game.java._block.Waterloggable.Always}
    def __eq__(self, other: typing.Any) -> bool: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: typing.SupportsInt) -> None: ...
    def __int__(self) -> int: ...
    def __ne__(self, other: typing.Any) -> bool: ...
    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...
    @property
    def name(self) -> str: ...
    @property
    def value(self) -> int: ...
