"""
Telegram Routers - Sync va Async routerlar
"""

from .sync.router import Router
from .sync.global_router import GlobalRouter, message_handler, callback_handler, register_sync_bot, get_sync_global_stats
from .async.router import AsyncRouter
from .async.global_router import AsyncGlobalRouter, async_message_handler, async_callback_handler, register_async_bot, get_async_global_stats
from .filters import Command, Text, TextContains, ContentType, State, IsAdmin, CallbackData, CallbackDataStartswith

__version__ = "1.0.0"

__all__ = [
    # Sync routerlar
    'Router',
    'GlobalRouter',
    'message_handler',
    'callback_handler', 
    'register_sync_bot',
    'get_sync_global_stats',
    
    # Async routerlar
    'AsyncRouter',
    'AsyncGlobalRouter',
    'async_message_handler',
    'async_callback_handler',
    'register_async_bot',
    'get_async_global_stats',
    
    # Filterlar
    'Command',
    'Text',
    'TextContains',
    'ContentType', 
    'State',
    'IsAdmin',
    'CallbackData',
    'CallbackDataStartswith'
]