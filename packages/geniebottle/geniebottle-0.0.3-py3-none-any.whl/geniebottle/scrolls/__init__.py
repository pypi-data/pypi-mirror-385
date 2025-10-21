"""
Magic Scrolls - Beautiful interfaces for interacting with magic

Scrolls are themed UI components that provide consistent, magical experiences
for different interaction modes (terminal, web, etc.)
"""

from .scroll import Scroll
from .agent_scroll import AgentScroll
from .chat_scroll import ChatScroll

__all__ = ['Scroll', 'AgentScroll', 'ChatScroll']
