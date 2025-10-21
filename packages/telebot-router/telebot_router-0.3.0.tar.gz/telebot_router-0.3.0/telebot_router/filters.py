from typing import List, Union

class Command:
    def __init__(self, commands: Union[str, List[str]]):
        if isinstance(commands, str):
            commands = [commands]
        self.commands = [cmd.lower() for cmd in commands]
    
    def __call__(self, message):
        if not hasattr(message, 'text') or not message.text or not message.text.startswith('/'):
            return False
        command = message.text.split()[0][1:].split('@')[0].lower()
        return command in self.commands

class Text:
    def __init__(self, texts: Union[str, List[str]]):
        if isinstance(texts, str):
            texts = [texts]
        self.texts = texts
    
    def __call__(self, message):
        return hasattr(message, 'text') and message.text in self.texts

class TextContains:
    def __init__(self, substrings: Union[str, List[str]]):
        if isinstance(substrings, str):
            substrings = [substrings]
        self.substrings = substrings
    
    def __call__(self, message):
        if not hasattr(message, 'text') or not message.text:
            return False
        return any(sub in message.text for sub in self.substrings)

class ContentType:
    def __init__(self, content_types: List[str]):
        self.content_types = content_types
    
    def __call__(self, message):
        return hasattr(message, 'content_type') and message.content_type in self.content_types

class State:
    def __init__(self, state):
        self.state = state
    
    def __call__(self, message):
        return True

class IsAdmin:
    def __init__(self, admin_ids: List[int]):
        self.admin_ids = admin_ids
    
    def __call__(self, message):
        return hasattr(message, 'from_user') and message.from_user.id in self.admin_ids

class CallbackData:
    def __init__(self, data: Union[str, List[str]]):
        if isinstance(data, str):
            data = [data]
        self.data = data
    
    def __call__(self, call):
        return hasattr(call, 'data') and call.data in self.data

class CallbackDataStartswith:
    def __init__(self, prefix: str):
        self.prefix = prefix
    
    def __call__(self, call):
        return hasattr(call, 'data') and call.data.startswith(self.prefix)