
Telebot routers 🤖

Powerful Router System for Sync and Async Telegram Bots


🚀 Features

- ✅ Sync & Async Support - TeleBot and AsyncTeleBot
- ✅ Global Routers - Same handlers for multiple bots
- ✅ Simple Routers - Dedicated handlers for single bot
- ✅ Advanced Filters - Command, Text, IsAdmin and more
- ✅ Modular Design - Clean file structure
- ✅ Full Documentation - Examples for every method

📦 Installation

```bash
pip install telebot-router
```

Or from source:

```bash
git clone https://github.com/Ergashev2006/telebot-router.git
cd telebot-router
pip install - e .
```

🎯 Quick Start

Sync Bot (TeleBot)

```python
from telebot import TeleBot
from telebot_router import Router, Command

bot = TeleBot("YOUR_BOT_TOKEN")
router = Router("my_bot")

@router.message_handler(commands=['start'])
def start_handler(message, bot):
    bot.reply_to(message, "👋 Hello! Sync bot started!")

@router.message_handler(commands=['help'])
def help_handler(message, bot):
    bot.reply_to(message, "📖 Need help?")

router.register(bot)
bot.polling()
```

Async Bot (AsyncTeleBot)

```python
from telebot.async_telebot import AsyncTeleBot
from telebot_router import AsyncRouter, Command
import asyncio

bot = AsyncTeleBot("YOUR_BOT_TOKEN")
router = AsyncRouter("async_bot")

@router.message_handler(commands=['start'])
async def start_handler(message, bot):
    await bot.reply_to(message, "⚡ Hello! Async bot started!")

router.register(bot)

async def main():
    await bot.polling()

asyncio.run(main())
```

🌍 Global Handlers

Multiple Sync Bots

```python
from telebot import TeleBot
from telebot_router import message_handler, register_sync_bot

# Global handler - works for all sync bots
@message_handler(commands=['start'])
def global_start(message, bot):
    bot.reply_to(message, "🌍 This is global handler! Works in all bots!")

# Bot 1
bot1 = TeleBot("TOKEN1")
register_sync_bot(bot1)

# Bot 2
bot2 = TeleBot("TOKEN2")
register_sync_bot(bot2)

# Start only one bot
bot1.polling()
```

Multiple Async Bots

```python
from telebot.async_telebot import AsyncTeleBot
from telebot_router import async_message_handler, register_async_bot
import asyncio

# Global async handler
@async_message_handler(commands=['start'])
async def global_async_start(message, bot):
    await bot.reply_to(message, "🌍⚡ This is global async handler!")

# Async bots
bot1 = AsyncTeleBot("TOKEN1")
bot2 = AsyncTeleBot("TOKEN2")

register_async_bot(bot1)
register_async_bot(bot2)

async def main():
    await bot1.polling()

asyncio.run(main())
```

🔍 Filters

Command Filter

```python
from telebot_router import Command

@router.message_handler(commands=['start', 'help'])
def command_handler(message, bot):
    bot.reply_to(message, "Command received!")
```

Text Filter

```python
from telebot_router import Text

@router.message_handler(func=Text('hello'))
def text_handler(message, bot):
    bot.reply_to(message, "Hello! How are you?")
```

TextContains Filter

```python
from telebot_router import TextContains

@router.message_handler(func=TextContains(['help', 'support']))
def contains_handler(message, bot):
    bot.reply_to(message, "Need help?")
```

IsAdmin Filter

```python
from telebot_router import IsAdmin

ADMIN_IDS = [123456789, 987654321]

@router.message_handler(func=IsAdmin(ADMIN_IDS), commands=['admin'])
def admin_handler(message, bot):
    bot.reply_to(message, "👑 Welcome to admin panel!")
```

CallbackData Filter

```python
from telebot_router import CallbackData
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

@router.callback_query_handler(func=CallbackData('button1'))
def callback_handler(call, bot):
    bot.answer_callback_query(call.id, "Button clicked!")
```

🏗️ Modular Project Structure

handlers/start.py

```python
from telebot_router import Router, Command

router = Router("start_handlers")

@router.message_handler(commands=['start'])
def start_handler(message, bot):
    bot.reply_to(message, "Start handler activated!")
```

handlers/admin.py

```python
from telebot_router import Router, Command, IsAdmin

router = Router("admin_handlers")
ADMIN_IDS = [123456789]

@router.message_handler(func=IsAdmin(ADMIN_IDS), commands=['secret'])
def secret_handler(message, bot):
    bot.reply_to(message, "Secret admin command!")
```

main.py

```python
from telebot import TeleBot
from telebot_router import Router
from handlers.start import router as start_router
from handlers.admin import router as admin_router

bot = TeleBot("YOUR_BOT_TOKEN")
main_router = Router("main")

# Combine all routers
main_router.include_router(start_router)
main_router.include_router(admin_router)

main_router.register(bot)
bot.polling()
```

📊 Statistics

Handler Count

```python
from telebot_router import get_sync_global_stats, get_async_global_stats

# Sync global statistics
sync_stats = get_sync_global_stats()
print(f"Sync bots: {sync_stats['total_bots']}")
print(f"Sync handlers: {sync_stats['handlers']}")

# Async global statistics  
async_stats = get_async_global_stats()
print(f"Async bots: {async_stats['total_bots']}")
print(f"Async handlers: {async_stats['handlers']}")
```

Simple Router Statistics

```python
router = Router("test")
stats = router.get_handler_count()
print(f"Message handlers: {stats['message_handlers']}")
print(f"Callback handlers: {stats['callback_handlers']}")
```

🎯 Additional Features

Include Routers

```python
from telebot_router import include_sync_router, include_async_router

# Include sync router
include_sync_router(my_router)

# Include async router
include_async_router(my_async_router)
```

Clear Handlers

```python
router.clear_handlers()  # Clear all handlers
```



🤝 Contributing

Want to contribute?

1. Fork the repository
2. Create a new branch (git checkout - b feature/awesome- feature)
3. Commit your changes (git commit - am 'Add awesome feature')
4. Push to the branch (git push origin feature/awesome- feature)
5. Create a Pull Request

📝 License

This project is licensed under the MIT License. See LICENSE file for details.

📞 Contact

If you have questions or need help:

- Email: o6.javohir.ergashev@gmail.com
- Telegram: +998947271207
- Issues: GitHub Issues

🙏 Acknowledgments

- TeleBot - Main Telegram Bot library
- All contributors and testers

- - - 

⭐ If you like this project, give it a star!

- - - 

🚀 Quick Reference

Imports

```python
# Sync
from telebot_router import Router, GlobalRouter, message_handler, callback_handler

# Async  
from telebot_router import AsyncRouter, AsyncGlobalRouter, async_message_handler, async_callback_handler

# Filters
from telebot_router import Command, Text, TextContains, IsAdmin, CallbackData

# Functions
from telebot_router import register_sync_bot, register_async_bot, get_sync_global_stats, get_async_global_stats
```

Main Methods

- router.message_handler() - Add message handler
- router.callback_query_handler() - Add callback handler
- router.include_router() - Include another router
- router.register() - Register to bot
- router.get_handler_count() - Get statistics
- router.clear_handlers() - Clear handlers

Happy Coding! 🎉

- - - 

Telegram Bot Test Code#

🧪 Complete Test Bot with All Features

1. test_bot.py - Main Test Bot

```python
from telebot import TeleBot
from telebot_router import Router, Command, Text, TextContains, IsAdmin, CallbackData
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import logging
import time

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_test_bot():
    """Create and configure test bot"""
    
    # Bot configuration
    BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"  # ⚠️ Replace with your token
    ADMIN_IDS = [123456789]  # ⚠️ Replace with your user ID
    
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("❌ ERROR: Please set your bot token!")
        print("💡 Get token from @BotFather in Telegram")
        return None
    
    # Create bot and router
    bot = TeleBot(BOT_TOKEN)
    router = Router("test_bot")
    
    # ==================== TEST HANDLERS ====================
    
    # 1. Basic command test
    @router.message_handler(commands=['start'])
    def start_test(message, bot):
        """Test basic command handling"""
        user = message.from_user
        welcome_text = f"""
🤖 **TEST BOT ACTIVATED**

👤 User: {user.first_name}
🆔 ID: `{user.id}`
🔧 Status: **WORKING**

📋 Available Tests:
/start - Show this message
/ping - Test response time  
/echo [text] - Echo test
/stats - Handler statistics
/menu - Show test buttons
/admin - Admin test (if admin)
        """
        bot.reply_to(message, welcome_text, parse_mode='Markdown')
        logger.info(f"Start test: {user.username}")
    
    # 2. Ping test
    @router.message_handler(commands=['ping'])
    def ping_test(message, bot):
        """Test server response time"""
        start_time = time.time()
        msg = bot.reply_to(message, "🏓 Pinging...")
        end_time = time.time()
        
        response_time = round((end_time - start_time) * 1000, 2)
        
        bot.edit_message_text(
            f"🏓 **Pong!**\n⏱ Response: {response_time}ms\n✅ Router working!",
            message.chat.id,
            msg.message_id,
            parse_mode='Markdown'
        )
        logger.info(f"Ping test: {response_time}ms")
    
    # 3. Echo test
    @router.message_handler(commands=['echo'])
    def echo_test(message, bot):
        """Test echo functionality"""
        text = message.text[6:]  # Remove '/echo '
        if not text:
            bot.reply_to(message, "❌ Usage: `/echo your text`", parse_mode='Markdown')
            return
        
        bot.reply_to(message, f"🔁 Echo: {text}")
        logger.info(f"Echo test: {text}")
    
    # 4. Statistics test
    @router.message_handler(commands=['stats'])
    def stats_test(message, bot):
        """Test router statistics"""
        stats = router.get_handler_count()
        
        stats_text = f"""
📊 **ROUTER STATISTICS**

📨 Message Handlers: {stats['message_handlers']}
🔄 Callback Handlers: {stats['callback_handlers']}
🔧 Total Handlers: {stats['message_handlers'] + stats['callback_handlers']}

✅ Router is working correctly!
        """
        bot.reply_to(message, stats_text, parse_mode='Markdown')
        logger.info(f"Stats test: {stats}")
    
    # 5. Menu with buttons test
    @router.message_handler(commands=['menu'])
    def menu_test(message, bot):
        """Test inline keyboard buttons"""
        keyboard = InlineKeyboardMarkup(row_width=2)
        keyboard.add(
            InlineKeyboardButton("✅ Test Button 1", callback_data="test_btn1"),
            InlineKeyboardButton("🔄 Test Button 2", callback_data="test_btn2"),
            InlineKeyboardButton("📊 Get Stats", callback_data="get_stats"),
            InlineKeyboardButton("❌ Delete Menu", callback_data="delete_menu")
        )
        
        bot.reply_to(
            message,
            "🎮 **TEST MENU**\n\nSelect a button to test callback handlers:",
            parse_mode='Markdown',
            reply_markup=keyboard
        )
    
    # 6. Text filter test
    @router.message_handler(func=Text('hello'))
    def hello_test(message, bot):
        """Test exact text matching"""
        bot.reply_to(message, "✅ **Text Filter Test!** - 'hello' detected!", parse_mode='Markdown')
    
    # 7. Text contains filter test
    @router.message_handler(func=TextContains(['help', 'yordam']))
    def help_test(message, bot):
        """Test text contains matching"""
        bot.reply_to(message, "✅ **TextContains Filter!** - Help word found!")
    
    # 8. Admin filter test
    @router.message_handler(func=IsAdmin(ADMIN_IDS), commands=['admin'])
    def admin_test(message, bot):
        """Test admin- only commands"""
        bot.reply_to(message, "👑 **Admin Test Passed!** - You have admin access!", parse_mode='Markdown')
    
    # 9. Lambda filter test
    @router.message_handler(func=lambda m: m.text and len(m.text) > 20)
    def long_text_test(message, bot):
        """Test custom lambda filter"""
        bot.reply_to(message, f"📝 **Long Text Test!** - {len(message.text)} characters")
    
    # ==================== CALLBACK HANDLERS ====================
    
    @router.callback_query_handler(func=CallbackData('test_btn1'))
    def button1_test(call, bot):
        """Test callback button 1"""
        bot.answer_callback_query(call.id, "✅ Button 1 clicked!")
        bot.send_message(call.message.chat.id, "🎉 **Button 1 Test Passed!**")
    
    @router.callback_query_handler(func=CallbackData('test_btn2'))
    def button2_test(call, bot):
        """Test callback button 2"""
        bot.answer_callback_query(call.id, "🔄 Button 2 clicked!")
        bot.edit_message_text(
            "🔄 **Button 2 Test Passed!**\nMessage edited successfully!",
            call.message.chat.id,
            call.message.message_id,
            parse_mode='Markdown'
        )
    
    @router.callback_query_handler(func=CallbackData('get_stats'))
    def stats_callback_test(call, bot):
        """Test stats in callback"""
        stats = router.get_handler_count()
        stats_text = f"""
📊 **CALLBACK STATS**

Message Handlers: {stats['message_handlers']}
Callback Handlers: {stats['callback_handlers']}
✅ All systems working!
        """
        
        bot.answer_callback_query(call.id, "📊 Stats updated!")
        bot.edit_message_text(
            stats_text,
            call.message.chat.id,
            call.message.message_id,
            parse_mode='Markdown'
        )
    
    @router.callback_query_handler(func=CallbackData('delete_menu'))
    def delete_menu_test(call, bot):
        """Test message deletion"""
        bot.answer_callback_query(call.id, "🗑️ Menu deleted!")
        bot.delete_message(call.message.chat.id, call.message.message_id)
    
    # ==================== ERROR HANDLER ====================
    
    @router.message_handler(func=lambda message: True)
    def unknown_message(message, bot):
        """Handle unknown commands"""
        bot.reply_to(
            message,
            "❓ **Unknown Command**\n\n"
            "Try these test commands:\n"
            "• /start - Show help\n"
            "• /ping - Test speed\n"  
            "• /echo [text] - Echo test\n"
            "• /stats - Show statistics\n"
            "• /menu - Test buttons\n"
            "• 'hello' - Text filter test\n"
            "• 'help me' - Contains filter test",
            parse_mode='Markdown'
        )
    
    return bot, router

def main():
    """Main function to run the test bot"""
    
    print("🚀 TELEGRAM BOT TEST SUITE")
    print("=" * 50)
    
    # Create test bot
    result = create_test_bot()
    if not result:
        return
    
    bot, router = result
    
    # Register router
    router.register(bot)
    
    # Display test information
    stats = router.get_handler_count()
    print("✅ Test Bot Configured!")
    print(f"📊 Handlers: {stats['message_handlers']} message, {stats['callback_handlers']} callback")
    print("\n🎯 **Available Tests:**")
    print("   /start    - Basic functionality")
    print("   /ping     - Response time") 
    print("   /echo     - Echo test")
    print("   /stats    - Router statistics")
    print("   /menu     - Button tests")
    print("   /admin    - Admin test (if admin)")
    print("   'hello'   - Text filter")
    print("   'help'    - Contains filter")
    print("   Long text - Lambda filter")
    print("\n📱 Send /start to your bot to begin testing!")
    print("=" * 50)
    
    try:
        print("🤖 Starting bot polling...")
        bot.polling(non_stop=True, interval=0)
    except KeyboardInterrupt:
        print("\n⏹️ Bot stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
```

2. test_async_bot.py - Async Test Bot

```python
from telebot.async_telebot import AsyncTeleBot
from telebot_router import AsyncRouter, Command, CallbackData
import asyncio
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def create_async_test_bot():
    """Create async test bot"""
    
    BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"  # ⚠️ Replace with your token
    
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("❌ ERROR: Please set your bot token!")
        return None
    
    bot = AsyncTeleBot(BOT_TOKEN)
    router = AsyncRouter("async_test_bot")
    
    # Async test handlers
    @router.message_handler(commands=['start'])
    async def async_start_test(message, bot):
        """Async start test"""
        await bot.reply_to(
            message,
            "⚡ **ASYNC BOT TEST**\n\n"
            "✅ Async router working!\n"
            "🔧 All features available\n"
            "🚀 Fast and efficient!",
            parse_mode='Markdown'
        )
    
    @router.message_handler(commands=['async_ping'])
    async def async_ping_test(message, bot):
        """Async ping test"""
        start_time = time.time()
        msg = await bot.reply_to(message, "⚡ Async pinging...")
        end_time = time.time()
        
        response_time = round((end_time - start_time) * 1000, 2)
        
        await bot.edit_message_text(
            f"⚡ **Async Pong!**\n⏱ {response_time}ms\n🎯 Async router working!",
            message.chat.id,
            msg.message_id,
            parse_mode='Markdown'
        )
    
    @router.callback_query_handler(func=CallbackData('async_btn'))
    async def async_button_test(call, bot):
        """Async callback test"""
        await bot.answer_callback_query(call.id, "⚡ Async button clicked!")
        await bot.send_message(call.message.chat.id, "✅ **Async callback working!**")
    
    return bot, router

async def main():
    """Main async function"""
    print("⚡ ASYNC BOT TEST SUITE")
    print("=" * 40)
    
    result = await create_async_test_bot()
    if not result:
        return
    
    bot, router = result
    router.register(bot)
    
    stats = router.get_handler_count()
    print(f"✅ Async Bot Ready!")
    print(f"📊 Async handlers: {stats}")
    print("\n🎯 Test commands:")
    print("   /start      - Async test")
    print("   /async_ping - Async speed test")
    print("=" * 40)
    
    try:
        print("🤖 Starting async polling...")
        await bot.polling(non_stop=True)
    except Exception as e:
        print(f"❌ Async error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
```

3. test_filters.py - Filter Testing

```python
from telebot_router import Command, Text, TextContains, IsAdmin, CallbackData
from telebot.types import Message, CallbackQuery, User
import logging

logging.basicConfig(level=logging.INFO)

def test_all_filters():
    """Test all filters"""
    
    print("🔍 FILTER TESTING")
    print("=" * 40)
    
    # Test data
    test_message = Message()
    test_message.from_user = User()
    test_message.from_user.id = 123456789
    
    test_callback = CallbackQuery()
    test_callback.data = "test_data"
    
    # 1. Command filter test
    print("\n1. Testing Command Filter...")
    cmd_filter = Command(['start', 'help'])
    test_message.text = "/start"
    result = cmd_filter(test_message)
    print(f"   Command '/start': {result} ✅" if result else "   ❌ FAILED")
    
    # 2. Text filter test
    print("\n2. Testing Text Filter...")
    text_filter = Text('hello')
    test_message.text = "hello"
    result = text_filter(test_message)
    print(f"   Text 'hello': {result} ✅" if result else "   ❌ FAILED")
    
    # 3. TextContains filter test
    print("\n3. Testing TextContains Filter...")
    contains_filter = TextContains(['help', 'support'])
    test_message.text = "I need help"
    result = contains_filter(test_message)
    print(f"   Contains 'help': {result} ✅" if result else "   ❌ FAILED")
    
    # 4. IsAdmin filter test
    print("\n4. Testing IsAdmin Filter...")
    admin_filter = IsAdmin([123456789, 999999999])
    test_message.from_user.id = 123456789
    result = admin_filter(test_message)
    print(f"   Admin ID 123456789: {result} ✅" if result else "   ❌ FAILED")
    
    # 5. CallbackData filter test
    print("\n5. Testing CallbackData Filter...")
    callback_filter = CallbackData('test_data')
    test_callback.data = "test_data"
    result = callback_filter(test_callback)
    print(f"   Callback data 'test_data': {result} ✅" if result else "   ❌ FAILED")
    
    print("\n" + "=" * 40)
    print("🎉 ALL FILTER TESTS COMPLETED!")

if __name__ == "__main__":
    test_all_filters()
```

🚀 How to Use

1. Setup:

```bash
# Install required packages
pip install telebot-router

# Get bot token from @BotFather in Telegram
# Replace "YOUR_BOT_TOKEN_HERE" with your actual token
```

2. Run Tests:

```bash
# Run main test bot
python test_bot.py

# Run async test bot (in separate terminal)
python test_async_bot.py

# Run filter tests
python test_filters.py
```

3. Test Commands:

Send these to your bot:

- /start - Show help and bot info
- /ping - Test response speed
- /echo Hello - Echo test
- /stats - Router statistics
- /menu - Button tests
- hello - Text filter test
- help me - Contains filter test
- /admin - Admin test (if you're admin)

✅ Expected Results

- ✅ All commands should work
- ✅ Buttons should respond immediately
- ✅ Statistics should show handler counts
- ✅ Filters should match correct messages
- ✅ Async bot should work smoothly

This test suite covers all Telebot routers features! 🎉