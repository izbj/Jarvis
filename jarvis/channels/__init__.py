"""Chat channels module with plugin architecture."""

from jarvis.channels.base import BaseChannel
from jarvis.channels.manager import ChannelManager

__all__ = ["BaseChannel", "ChannelManager"]
