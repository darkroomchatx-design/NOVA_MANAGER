#!/usr/bin/env python3
# ═══════════════════════════════════════════════════════════════════════
# 💀 NEON AI — COMPLETE GROUP MANAGER BOT (FULLY WORKING) 💀
# 👑 OWNER: @TylerDurden21 (ID: 6650888707) + CO-OWNER (Add yours)
# 🔥 FEATURES: Welcome | Captcha | Warn | Mute | Ban | Filters | Notes | Locks | Schedule | Analytics
# ═══════════════════════════════════════════════════════════════════════

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import json
import os
import time
import threading
import random
import re
from datetime import datetime
from collections import defaultdict

# ═══════════════════════════════════════════════════════════════════════
# 🔥 CONFIGURATION — FIRST TIME SETUP
# ═══════════════════════════════════════════════════════════════════════

CONFIG_FILE = "neon_config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

config = load_config()
BOT_TOKEN = config.get("8717771974:AAFd_LnKygjb6RupT7f09PMai-u3OD_zWNY", "")
OWNER_IDS = config.get("6650888707", [])
OWNER_USERNAMES = config.get("@TylerDurden21", [])

# First time setup
if not BOT_TOKEN:
    print("\n" + "="*60)
    print("💀 NEON AI GROUP MANAGER — FIRST TIME SETUP 💀")
    print("="*60)
    BOT_TOKEN = input("\n🔑 Enter your Bot Token (from @BotFather): ").strip()
    
    print("\n👑 OWNER SETUP")
    owner_id = input("Enter your Telegram User ID (primary owner): ").strip()
    if owner_id.isdigit():
        OWNER_IDS = [int(owner_id)]
        owner_user = input("Enter your Telegram Username (without @): ").strip()
        if owner_user:
            OWNER_USERNAMES = [f"@{owner_user}"]
    
    add_second = input("\nAdd second owner? (y/n): ").strip().lower()
    if add_second == 'y':
        second_id = input("Enter second owner's User ID: ").strip()
        if second_id.isdigit():
            OWNER_IDS.append(int(second_id))
            second_user = input("Enter second owner's Username: ").strip()
            if second_user:
                OWNER_USERNAMES.append(f"@{second_user}")
    
    config["BOT_TOKEN"] = BOT_TOKEN
    config["OWNER_IDS"] = OWNER_IDS
    config["OWNER_USERNAMES"] = OWNER_USERNAMES
    save_config(config)
    
    print("\n✅ Configuration saved! Restart the bot.")
    print(f"👑 Primary Owner: {OWNER_USERNAMES[0] if OWNER_USERNAMES else OWNER_IDS[0]}")
    if len(OWNER_IDS) > 1:
        print(f"👑 Co-Owner: {OWNER_USERNAMES[1] if len(OWNER_USERNAMES) > 1 else OWNER_IDS[1]}")
    print("\n🚀 Run 'python bot.py' again to start!")
    exit(0)

# ═══════════════════════════════════════════════════════════════════════
# 🤖 BOT INITIALIZATION
# ═══════════════════════════════════════════════════════════════════════

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

# ═══════════════════════════════════════════════════════════════════════
# 📁 DATA FILES
# ═══════════════════════════════════════════════════════════════════════

WARNS_FILE = "neon_warns.json"
MUTES_FILE = "neon_mutes.json"
BANS_FILE = "neon_bans.json"
FILTERS_FILE = "neon_filters.json"
NOTES_FILE = "neon_notes.json"
LOCKS_FILE = "neon_locks.json"
SCHEDULES_FILE = "neon_schedules.json"
SETTINGS_FILE = "neon_settings.json"
BLACKLIST_FILE = "neon_blacklist.json"
CAPTCHA_FILE = "neon_captcha.json"
ANALYTICS_FILE = "neon_analytics.json"

# ═══════════════════════════════════════════════════════════════════════
# 🔧 HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════

def load_data(file, default={}):
    if os.path.exists(file):
        try:
            with open(file, 'r') as f:
                return json.load(f)
        except:
            return default
    return default

def save_data(file, data):
    try:
        with open(file, 'w') as f:
            json.dump(data, f, indent=2)
    except:
        pass

def is_owner(user_id):
    return user_id in OWNER_IDS

def is_admin(chat_id, user_id):
    if is_owner(user_id):
        return True
    try:
        member = bot.get_chat_member(chat_id, user_id)
        return member.status in ['administrator', 'creator']
    except:
        return False

def resolve_user(chat_id, user_input):
    user_input = user_input.strip()
    if user_input.startswith('@'):
        user_input = user_input[1:]
        try:
            for member in bot.get_chat_members(chat_id):
                if member.user.username and member.user.username.lower() == user_input.lower():
                    return member.user.id, member.user.first_name, member.user.username
        except:
            pass
    elif user_input.isdigit():
        try:
            member = bot.get_chat_member(chat_id, int(user_input))
            return member.user.id, member.user.first_name, member.user.username
        except:
            return int(user_input), str(user_input), None
    return None, None, None

def get_user_link(user_id, name=None):
    if name:
        return f"<a href='tg://user?id={user_id}'>{name}</a>"
    return f"<a href='tg://user?id={user_id}'>User</a>"

def parse_time(time_str):
    time_str = time_str.lower()
    if time_str.endswith('m'):
        return int(time_str[:-1]) * 60
    elif time_str.endswith('h'):
        return int(time_str[:-1]) * 3600
    elif time_str.endswith('d'):
        return int(time_str[:-1]) * 86400
    else:
        return int(time_str)

def format_time(seconds):
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        return f"{seconds//60}m"
    elif seconds < 86400:
        return f"{seconds//3600}h"
    else:
        return f"{seconds//86400}d"

# ═══════════════════════════════════════════════════════════════════════
# 🎨 SETTINGS MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════

def get_settings(chat_id):
    settings = load_data(SETTINGS_FILE, {})
    if str(chat_id) not in settings:
        settings[str(chat_id)] = {
            "welcome_enabled": False,
            "welcome_message": "👋 Welcome {mention} to {group}! You're member #{count}",
            "goodbye_enabled": False,
            "goodbye_message": "👋 {mention} left the group!",
            "captcha_enabled": False,
            "antiflood_enabled": False,
            "antiflood_limit": 5,
            "antichar_enabled": False,
            "antichar_limit": 60,
            "anticommunist_enabled": False,
            "flood_tracker": {}
        }
        save_data(SETTINGS_FILE, settings)
    return settings[str(chat_id)]

def save_settings(chat_id, settings):
    all_settings = load_data(SETTINGS_FILE, {})
    all_settings[str(chat_id)] = settings
    save_data(SETTINGS_FILE, all_settings)

# ═══════════════════════════════════════════════════════════════════════
# 🎨 CAPTCHA SYSTEM
# ═══════════════════════════════════════════════════════════════════════

def generate_captcha():
    num1 = random.randint(1, 10)
    num2 = random.randint(1, 10)
    operators = ['+', '-', '*']
    op = random.choice(operators)
    if op == '+':
        answer = num1 + num2
    elif op == '-':
        answer = num1 - num2
    else:
        answer = num1 * num2
    return f"{num1} {op} {num2} = ?", answer

def start_captcha(chat_id, user_id):
    captchas = load_data(CAPTCHA_FILE, {})
    question, answer = generate_captcha()
    captchas[f"{chat_id}_{user_id}"] = {"question": question, "answer": answer, "start": time.time()}
    save_data(CAPTCHA_FILE, captchas)
    return question

def verify_captcha(chat_id, user_id, answer):
    captchas = load_data(CAPTCHA_FILE, {})
    key = f"{chat_id}_{user_id}"
    if key not in captchas:
        return False
    data = captchas[key]
    if time.time() - data["start"] > 120:
        del captchas[key]
        save_data(CAPTCHA_FILE, captchas)
        return False
    try:
        if int(answer) == data["answer"]:
            del captchas[key]
            save_data(CAPTCHA_FILE, captchas)
            return True
    except:
        pass
    return False

def check_captchas():
    captchas = load_data(CAPTCHA_FILE, {})
    now = time.time()
    for key, data in captchas.items():
        if now - data["start"] > 120:
            parts = key.split("_")
            if len(parts) == 2:
                try:
                    bot.kick_chat_member(int(parts[0]), int(parts[1]))
                    bot.unban_chat_member(int(parts[0]), int(parts[1]))
                except:
                    pass
    save_data(CAPTCHA_FILE, {})

# ═══════════════════════════════════════════════════════════════════════
# 🎨 WARNING SYSTEM
# ═══════════════════════════════════════════════════════════════════════

def add_warn(chat_id, user_id, reason, admin_id):
    warns = load_data(WARNS_FILE, {})
    key = f"{chat_id}_{user_id}"
    if key not in warns:
        warns[key] = []
    warns[key].append({"reason": reason, "admin": admin_id, "time": time.time()})
    save_data(WARNS_FILE, warns)
    if len(warns[key]) >= 3:
        try:
            bot.ban_chat_member(chat_id, user_id)
            return True
        except:
            pass
    return False

def get_warns(chat_id, user_id):
    warns = load_data(WARNS_FILE, {})
    key = f"{chat_id}_{user_id}"
    return warns.get(key, [])

def remove_warn(chat_id, user_id):
    warns = load_data(WARNS_FILE, {})
    key = f"{chat_id}_{user_id}"
    if key in warns and warns[key]:
        warns[key].pop()
        if not warns[key]:
            del warns[key]
        save_data(WARNS_FILE, warns)
        return True
    return False

def reset_warns(chat_id, user_id):
    warns = load_data(WARNS_FILE, {})
    key = f"{chat_id}_{user_id}"
    if key in warns:
        del warns[key]
        save_data(WARNS_FILE, warns)
        return True
    return False

# ═══════════════════════════════════════════════════════════════════════
# 🎨 MUTE SYSTEM
# ═══════════════════════════════════════════════════════════════════════

def mute_user(chat_id, user_id, duration=None, reason=""):
    mutes = load_data(MUTES_FILE, {})
    key = f"{chat_id}_{user_id}"
    mutes[key] = {"until": time.time() + duration if duration else None, "reason": reason}
    save_data(MUTES_FILE, mutes)
    try:
        if duration:
            until_date = int((time.time() + duration) * 1000)
            bot.restrict_chat_member(chat_id, user_id, can_send_messages=False, until_date=until_date)
        else:
            bot.restrict_chat_member(chat_id, user_id, can_send_messages=False)
    except:
        pass

def unmute_user(chat_id, user_id):
    mutes = load_data(MUTES_FILE, {})
    key = f"{chat_id}_{user_id}"
    if key in mutes:
        del mutes[key]
        save_data(MUTES_FILE, mutes)
    try:
        bot.restrict_chat_member(chat_id, user_id, can_send_messages=True)
    except:
        pass

def is_muted(chat_id, user_id):
    mutes = load_data(MUTES_FILE, {})
    key = f"{chat_id}_{user_id}"
    if key in mutes:
        if mutes[key]["until"] and mutes[key]["until"] < time.time():
            unmute_user(chat_id, user_id)
            return False
        return True
    return False

# ═══════════════════════════════════════════════════════════════════════
# 🎨 BAN SYSTEM
# ═══════════════════════════════════════════════════════════════════════

def ban_user(chat_id, user_id, duration=None, reason=""):
    bans = load_data(BANS_FILE, {})
    key = f"{chat_id}_{user_id}"
    bans[key] = {"until": time.time() + duration if duration else None, "reason": reason}
    save_data(BANS_FILE, bans)
    try:
        if duration:
            until_date = int((time.time() + duration) * 1000)
            bot.ban_chat_member(chat_id, user_id, until_date=until_date)
        else:
            bot.ban_chat_member(chat_id, user_id)
    except:
        pass

def unban_user(chat_id, user_id):
    bans = load_data(BANS_FILE, {})
    key = f"{chat_id}_{user_id}"
    if key in bans:
        del bans[key]
        save_data(BANS_FILE, bans)
    try:
        bot.unban_chat_member(chat_id, user_id)
    except:
        pass

def kick_user(chat_id, user_id):
    try:
        bot.ban_chat_member(chat_id, user_id)
        bot.unban_chat_member(chat_id, user_id)
        return True
    except:
        return False

# ═══════════════════════════════════════════════════════════════════════
# 🎨 FILTER SYSTEM
# ═══════════════════════════════════════════════════════════════════════

def add_filter(chat_id, word):
    filters = load_data(FILTERS_FILE, {})
    if str(chat_id) not in filters:
        filters[str(chat_id)] = []
    if word.lower() not in filters[str(chat_id)]:
        filters[str(chat_id)].append(word.lower())
        save_data(FILTERS_FILE, filters)
        return True
    return False

def remove_filter(chat_id, word):
    filters = load_data(FILTERS_FILE, {})
    if str(chat_id) in filters and word.lower() in filters[str(chat_id)]:
        filters[str(chat_id)].remove(word.lower())
        save_data(FILTERS_FILE, filters)
        return True
    return False

def get_filters(chat_id):
    filters = load_data(FILTERS_FILE, {})
    return filters.get(str(chat_id), [])

def check_filter(chat_id, text):
    for word in get_filters(chat_id):
        if word in text.lower():
            return True
    return False

# ═══════════════════════════════════════════════════════════════════════
# 🎨 NOTES SYSTEM
# ═══════════════════════════════════════════════════════════════════════

def save_note(chat_id, name, content):
    notes = load_data(NOTES_FILE, {})
    if str(chat_id) not in notes:
        notes[str(chat_id)] = {}
    notes[str(chat_id)][name.lower()] = {"content": content, "time": time.time()}
    save_data(NOTES_FILE, notes)

def get_note(chat_id, name):
    notes = load_data(NOTES_FILE, {})
    return notes.get(str(chat_id), {}).get(name.lower())

def delete_note(chat_id, name):
    notes = load_data(NOTES_FILE, {})
    if str(chat_id) in notes and name.lower() in notes[str(chat_id)]:
        del notes[str(chat_id)][name.lower()]
        save_data(NOTES_FILE, notes)
        return True
    return False

def get_all_notes(chat_id):
    notes = load_data(NOTES_FILE, {})
    return list(notes.get(str(chat_id), {}).keys())

# ═══════════════════════════════════════════════════════════════════════
# 🎨 BLACKLIST SYSTEM
# ═══════════════════════════════════════════════════════════════════════

def blacklist_user(user_id, reason, admin_id):
    blacklist = load_data(BLACKLIST_FILE, {})
    blacklist[str(user_id)] = {"reason": reason, "admin": admin_id, "time": time.time()}
    save_data(BLACKLIST_FILE, blacklist)

def unblacklist_user(user_id):
    blacklist = load_data(BLACKLIST_FILE, {})
    if str(user_id) in blacklist:
        del blacklist[str(user_id)]
        save_data(BLACKLIST_FILE, blacklist)
        return True
    return False

def is_blacklisted(user_id):
    blacklist = load_data(BLACKLIST_FILE, {})
    return str(user_id) in blacklist

# ═══════════════════════════════════════════════════════════════════════
# 🎨 SCHEDULED MESSAGES
# ═══════════════════════════════════════════════════════════════════════

def add_schedule(chat_id, minutes, message, user_id):
    schedules = load_data(SCHEDULES_FILE, {})
    schedule_id = int(time.time())
    execute_time = time.time() + (minutes * 60)
    schedules[str(schedule_id)] = {"chat_id": chat_id, "execute_time": execute_time, "message": message, "user_id": user_id}
    save_data(SCHEDULES_FILE, schedules)
    timer = threading.Timer(minutes * 60, execute_schedule, args=[schedule_id])
    timer.daemon = True
    timer.start()
    return schedule_id

def execute_schedule(schedule_id):
    schedules = load_data(SCHEDULES_FILE, {})
    if str(schedule_id) in schedules:
        data = schedules[str(schedule_id)]
        try:
            bot.send_message(data["chat_id"], f"⏰ **Scheduled Message**\n\n{data['message']}")
        except:
            pass
        del schedules[str(schedule_id)]
        save_data(SCHEDULES_FILE, schedules)

def load_schedules():
    schedules = load_data(SCHEDULES_FILE, {})
    now = time.time()
    for sid, data in schedules.items():
        if data["execute_time"] > now:
            delay = data["execute_time"] - now
            timer = threading.Timer(delay, execute_schedule, args=[int(sid)])
            timer.daemon = True
            timer.start()

# ═══════════════════════════════════════════════════════════════════════
# 🎨 ANALYTICS
# ═══════════════════════════════════════════════════════════════════════

def track_message(chat_id, user_id):
    analytics = load_data(ANALYTICS_FILE, {})
    key = f"{chat_id}_{user_id}"
    today = datetime.now().strftime("%Y-%m-%d")
    if key not in analytics:
        analytics[key] = {"messages": {}, "total": 0}
    analytics[key]["messages"][today] = analytics[key]["messages"].get(today, 0) + 1
    analytics[key]["total"] += 1
    save_data(ANALYTICS_FILE, analytics)

def get_analytics(chat_id):
    analytics = load_data(ANALYTICS_FILE, {})
    stats = []
    total = 0
    for key, data in analytics.items():
        if key.startswith(f"{chat_id}_"):
            user_id = int(key.split("_")[1])
            stats.append({"user_id": user_id, "total": data["total"]})
            total += data["total"]
    stats.sort(key=lambda x: x["total"], reverse=True)
    return stats[:10], total

# ═══════════════════════════════════════════════════════════════════════
# 🎨 ANTI-FLOOD
# ═══════════════════════════════════════════════════════════════════════

def check_flood(chat_id, user_id):
    settings = get_settings(chat_id)
    if not settings.get("antiflood_enabled", False):
        return False
    tracker = settings.get("flood_tracker", {})
    now = time.time()
    if str(user_id) not in tracker:
        tracker[str(user_id)] = []
    tracker[str(user_id)] = [t for t in tracker[str(user_id)] if now - t < 5]
    tracker[str(user_id)].append(now)
    if len(tracker[str(user_id)]) > settings.get("antiflood_limit", 5):
        mute_user(chat_id, user_id, 60, "Flooding")
        settings["flood_tracker"][str(user_id)] = []
        save_settings(chat_id, settings)
        return True
    settings["flood_tracker"] = tracker
    save_settings(chat_id, settings)
    return False

# ═══════════════════════════════════════════════════════════════════════
# 🤖 COMMAND HANDLERS
# ═══════════════════════════════════════════════════════════════════════

@bot.message_handler(commands=['start'])
def start_cmd(message):
    if message.chat.type != 'private':
        return
    user_id = message.from_user.id
    text = f"""💀 **NEON AI GROUP MANAGER** 💀

🔥 Bot is alive and ready!
👑 Owner: {', '.join(OWNER_USERNAMES) if OWNER_USERNAMES else 'Configured'}

📌 **Commands:**
/help - Show all commands
/start - Show this message

⚠️ Add me to your group as ADMIN to use moderation features!"""
    bot.reply_to(message, text)

@bot.message_handler(commands=['help'])
def help_cmd(message):
    if message.chat.type != 'private':
        return
    text = """💀 **NEON AI GROUP MANAGER — HELP** 💀

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**🛡️ MODERATION COMMANDS:**
/warn <user> [reason] - Warn a user
/unwarn <user> - Remove warning
/warns <user> - Check warnings
/resetwarns <user> - Reset warnings
/mute <user> [reason] - Mute user
/tmute <user> <time> [reason] - Temp mute (1m, 1h, 1d)
/unmute <user> - Unmute user
/mutelist - List muted users
/ban <user> [reason] - Ban user
/tban <user> <time> [reason] - Temp ban
/unban <user> - Unban user
/kick <user> [reason] - Kick user
/banlist - List banned users

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**⚙️ SETTINGS COMMANDS:**
/welcome on/off - Toggle welcome
/setwelcome <message> - Set welcome message
/goodbye on/off - Toggle goodbye
/setgoodbye <message> - Set goodbye message
/captcha on/off - Toggle CAPTCHA
/flood <count> - Set flood limit
/setflood on/off - Toggle flood control
/anticommunist on/off - Block invites
/antichar on/off - Block caps
/antichar <limit> - Set caps limit
/lock <type> - Lock (stickers/gifs/links/forwards/invites/bots)
/unlock <type> - Unlock
/locks - Show locks
/filter <word> - Add filter
/filters - List filters
/stop <word> - Remove filter

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**📝 NOTES & INFO:**
/save <name> <content> - Save note
/notes - List notes
/get <name> - Get note
/delete <name> - Delete note
/info <user> - User info
/groupinfo - Group info
/admins - List admins

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**⏰ CUSTOM COMMANDS:**
/schedule <minutes> "<message>" - Schedule message
/schedules - List schedules
/cancelschedule <id> - Cancel schedule
/analytics - Group statistics
/set show - Show settings

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**👑 OWNER COMMANDS:**
/addowner <user_id> - Add co-owner
/removeowner <user_id> - Remove owner
/owners - List owners
/block <user> [reason] - Blacklist user
/unblock <user> - Unblacklist
/blocklist - Show blacklist

💀 @TylerDurden21"""
    bot.reply_to(message, text)

@bot.message_handler(commands=['warn'])
def warn_cmd(message):
    if message.chat.type == 'private':
        return
    if not is_admin(message.chat.id, message.from_user.id):
        bot.reply_to(message, "❌ Admin access required!")
        return
    args = message.text.split(maxsplit=2)
    if len(args) < 2:
        bot.reply_to(message, "Usage: /warn @username [reason]")
        return
    user_id, name, username = resolve_user(message.chat.id, args[1])
    if not user_id:
        bot.reply_to(message, "❌ User not found!")
        return
    reason = args[2] if len(args) > 2 else "No reason"
    if add_warn(message.chat.id, user_id, reason, message.from_user.id):
        bot.reply_to(message, f"⚠️ {get_user_link(user_id, name)} has been **AUTO-BANNED** after 3 warnings!\nReason: {reason}")
    else:
        warns = get_warns(message.chat.id, user_id)
        bot.reply_to(message, f"⚠️ {get_user_link(user_id, name)} warned!\nReason: {reason}\nWarnings: {len(warns)}/3")

@bot.message_handler(commands=['unwarn'])
def unwarn_cmd(message):
    if message.chat.type == 'private':
        return
    if not is_admin(message.chat.id, message.from_user.id):
        bot.reply_to(message, "❌ Admin access required!")
        return
    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, "Usage: /unwarn @username")
        return
    user_id, name, username = resolve_user(message.chat.id, args[1])
    if not user_id:
        bot.reply_to(message, "❌ User not found!")
        return
    if remove_warn(message.chat.id, user_id):
        bot.reply_to(message, f"✅ Warning removed for {get_user_link(user_id, name)}")
    else:
        bot.reply_to(message, "❌ No warnings found!")

@bot.message_handler(commands=['warns'])
def warns_cmd(message):
    if message.chat.type == 'private':
        return
    if not is_admin(message.chat.id, message.from_user.id):
        bot.reply_to(message, "❌ Admin access required!")
        return
    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, "Usage: /warns @username")
        return
    user_id, name, username = resolve_user(message.chat.id, args[1])
    if not user_id:
        bot.reply_to(message, "❌ User not found!")
        return
    warns = get_warns(message.chat.id, user_id)
    if warns:
        text = f"⚠️ **Warnings for {get_user_link(user_id, name)}** ⚠️\n\n"
        for i, w in enumerate(warns, 1):
            text += f"{i}. {w['reason']} (by {w['admin']})\n"
        bot.reply_to(message, text)
    else:
        bot.reply_to(message, f"✅ {get_user_link(user_id, name)} has no warnings.")

@bot.message_handler(commands=['resetwarns'])
def resetwarns_cmd(message):
    if message.chat.type == 'private':
        return
    if not is_admin(message.chat.id, message.from_user.id):
        bot.reply_to(message, "❌ Admin access required!")
        return
    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, "Usage: /resetwarns @username")
        return
    user_id, name, username = resolve_user(message.chat.id, args[1])
    if not user_id:
        bot.reply_to(message, "❌ User not found!")
        return
    if reset_warns(message.chat.id, user_id):
        bot.reply_to(message, f"✅ Warnings reset for {get_user_link(user_id, name)}")
    else:
        bot.reply_to(message, "❌ No warnings found!")

@bot.message_handler(commands=['mute'])
def mute_cmd(message):
    if message.chat.type == 'private':
        return
    if not is_admin(message.chat.id, message.from_user.id):
        bot.reply_to(message, "❌ Admin access required!")
        return
    args = message.text.split(maxsplit=2)
    if len(args) < 2:
        bot.reply_to(message, "Usage: /mute @username [reason]")
        return
    user_id, name, username = resolve_user(message.chat.id, args[1])
    if not user_id:
        bot.reply_to(message, "❌ User not found!")
        return
    reason = args[2] if len(args) > 2 else "No reason"
    mute_user(message.chat.id, user_id, None, reason)
    bot.reply_to(message, f"🔇 {get_user_link(user_id, name)} has been muted!\nReason: {reason}")

@bot.message_handler(commands=['tmute'])
def tmute_cmd(message):
    if message.chat.type == 'private':
        return
    if not is_admin(message.chat.id, message.from_user.id):
        bot.reply_to(message, "❌ Admin access required!")
        return
    args = message.text.split(maxsplit=3)
    if len(args) < 3:
        bot.reply_to(message, "Usage: /tmute @username 1m/1h/1d [reason]")
        return
    user_id, name, username = resolve_user(message.chat.id, args[1])
    if not user_id:
        bot.reply_to(message, "❌ User not found!")
        return
    duration = parse_time(args[2])
    reason = args[3] if len(args) > 3 else "No reason"
    mute_user(message.chat.id, user_id, duration, reason)
    bot.reply_to(message, f"🔇 {get_user_link(user_id, name)} has been muted for {args[2]}!\nReason: {reason}")

@bot.message_handler(commands=['unmute'])
def unmute_cmd(message):
    if message.chat.type == 'private':
        return
    if not is_admin(message.chat.id, message.from_user.id):
        bot.reply_to(message, "❌ Admin access required!")
        return
    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, "Usage: /unmute @username")
        return
    user_id, name, username = resolve_user(message.chat.id, args[1])
    if not user_id:
        bot.reply_to(message, "❌ User not found!")
        return
    unmute_user(message.chat.id, user_id)
    bot.reply_to(message, f"🔊 {get_user_link(user_id, name)} has been unmuted!")

@bot.message_handler(commands=['mutelist'])
def mutelist_cmd(message):
    if message.chat.type == 'private':
        return
    if not is_admin(message.chat.id, message.from_user.id):
        bot.reply_to(message, "❌ Admin access required!")
        return
    mutes = load_data(MUTES_FILE, {})
    muted = []
    for key, data in mutes.items():
        if key.startswith(f"{message.chat.id}_"):
            user_id = int(key.split("_")[1])
            remaining = int(data["until"] - time.time()) if data["until"] else 0
            muted.append(f"• {get_user_link(user_id)} - {format_time(remaining)} left" if remaining else f"• {get_user_link(user_id)} - Permanent")
    if muted:
        bot.reply_to(message, "🔇 **Muted Users:**\n\n" + "\n".join(muted[:20]))
    else:
        bot.reply_to(message, "✅ No muted users.")

@bot.message_handler(commands=['ban'])
def ban_cmd(message):
    if message.chat.type == 'private':
        return
    if not is_admin(message.chat.id, message.from_user.id):
        bot.reply_to(message, "❌ Admin access required!")
        return
    args = message.text.split(maxsplit=2)
    if len(args) < 2:
        bot.reply_to(message, "Usage: /ban @username [reason]")
        return
    user_id, name, username = resolve_user(message.chat.id, args[1])
    if not user_id:
        bot.reply_to(message, "❌ User not found!")
        return
    reason = args[2] if len(args) > 2 else "No reason"
    ban_user(message.chat.id, user_id, None, reason)
    bot.reply_to(message, f"🚫 {get_user_link(user_id, name)} has been banned!\nReason: {reason}")

@bot.message_handler(commands=['tban'])
def tban_cmd(message):
    if message.chat.type == 'private':
        return
    if not is_admin(message.chat.id, message.from_user.id):
        bot.reply_to(message, "❌ Admin access required!")
        return
    args = message.text.split(maxsplit=3)
    if len(args) < 3:
        bot.reply_to(message, "Usage: /tban @username 1m/1h/1d [reason]")
        return
    user_id, name, username = resolve_user(message.chat.id, args[1])
    if not user_id:
        bot.reply_to(message, "❌ User not found!")
        return
    duration = parse_time(args[2])
    reason = args[3] if len(args) > 3 else "No reason"
    ban_user(message.chat.id, user_id, duration, reason)
    bot.reply_to(message, f"🚫 {get_user_link(user_id, name)} has been banned for {args[2]}!\nReason: {reason}")

@bot.message_handler(commands=['unban'])
def unban_cmd(message):
    if message.chat.type == 'private':
        return
    if not is_admin(message.chat.id, message.from_user.id):
        bot.reply_to(message, "❌ Admin access required!")
        return
    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, "Usage: /unban @username")
        return
    user_id, name, username = resolve_user(message.chat.id, args[1])
    if not user_id:
        bot.reply_to(message, "❌ User not found!")
        return
    unban_user(message.chat.id, user_id)
    bot.reply_to(message, f"✅ {get_user_link(user_id, name)} has been unbanned!")

@bot.message_handler(commands=['kick'])
def kick_cmd(message):
    if message.chat.type == 'private':
        return
    if not is_admin(message.chat.id, message.from_user.id):
        bot.reply_to(message, "❌ Admin access required!")
        return
    args = message.text.split(maxsplit=2)
    if len(args) < 2:
        bot.reply_to(message, "Usage: /kick @username [reason]")
        return
    user_id, name, username = resolve_user(message.chat.id, args[1])
    if not user_id:
        bot.reply_to(message, "❌ User not found!")
        return
    reason = args[2] if len(args) > 2 else "No reason"
    if kick_user(message.chat.id, user_id):
        bot.reply_to(message, f"👢 {get_user_link(user_id, name)} has been kicked!\nReason: {reason}")
    else:
        bot.reply_to(message, "❌ Failed to kick user!")

@bot.message_handler(commands=['banlist'])
def banlist_cmd(message):
    if message.chat.type == 'private':
        return
    if not is_admin(message.chat.id, message.from_user.id):
        bot.reply_to(message, "❌ Admin access required!")
        return
    bans = load_data(BANS_FILE, {})
    banned = []
    for key, data in bans.items():
        if key.startswith(f"{message.chat.id}_"):
            user_id = int(key.split("_")[1])
            remaining = int(data["until"] - time.time()) if data["until"] else 0
            banned.append(f"• {get_user_link(user_id)} - {format_time(remaining)} left" if remaining else f"• {get_user_link(user_id)} - Permanent")
    if banned:
        bot.reply_to(message, "🚫 **Banned Users:**\n\n" + "\n".join(banned[:20]))
    else:
        bot.reply_to(message, "✅ No banned users.")

@bot.message_handler(commands=['filter'])
def filter_cmd(message):
    if message.chat.type == 'private':
        return
    if not is_admin(message.chat.id, message.from_user.id):
        bot.reply_to(message, "❌ Admin access required!")
        return
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        bot.reply_to(message, "Usage: /filter <word>")
        return
    word = args[1].lower()
    if add_filter(message.chat.id, word):
        bot.reply_to(message, f"✅ Filter added: `{word}`")
    else:
        bot.reply_to(message, f"❌ Filter `{word}` already exists!")

@bot.message_handler(commands=['filters'])
def filters_cmd(message):
    if message.chat.type == 'private':
        return
    if not is_admin(message.chat.id, message.from_user.id):
        bot.reply_to(message, "❌ Admin access required!")
        return
    filters = get_filters(message.chat.id)
    if filters:
        bot.reply_to(message, "📋 **Active Filters:**\n\n" + "\n".join([f"• `{w}`" for w in filters]))
    else:
        bot.reply_to(message, "✅ No active filters.")

@bot.message_handler(commands=['stop'])
def stop_cmd(message):
    if message.chat.type == 'private':
        return
    if not is_admin(message.chat.id, message.from_user.id):
        bot.reply_to(message, "❌ Admin access required!")
        return
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        bot.reply_to(message, "Usage: /stop <word>")
        return
    word = args[1].lower()
    if remove_filter(message.chat.id, word):
        bot.reply_to(message, f"✅ Filter removed: `{word}`")
    else:
        bot.reply_to(message, f"❌ Filter `{word}` not found!")

@bot.message_handler(commands=['save'])
def save_cmd(message):
    if message.chat.type == 'private':
        return
    if not is_admin(message.chat.id, message.from_user.id):
        bot.reply_to(message, "❌ Admin access required!")
        return
    args = message.text.split(maxsplit=2)
    if len(args) < 3:
        bot.reply_to(message, "Usage: /save <name> <content>")
        return
    name = args[1].lower()
    content = args[2]
    save_note(message.chat.id, name, content)
    bot.reply_to(message, f"✅ Note `{name}` saved!")

@bot.message_handler(commands=['notes'])
def notes_cmd(message):
    if message.chat.type == 'private':
        return
    if not is_admin(message.chat.id, message.from_user.id):
        bot.reply_to(message, "❌ Admin access required!")
        return
    notes = get_all_notes(message.chat.id)
    if notes:
        bot.reply_to(message, "📝 **Available Notes:**\n\n" + "\n".join([f"• `{n}`" for n in notes]))
    else:
        bot.reply_to(message, "📝 No notes saved.")

@bot.message_handler(commands=['get'])
def get_cmd(message):
    if message.chat.type == 'private':
        return
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        bot.reply_to(message, "Usage: /get <note_name>")
        return
    name = args[1].lower()
    note = get_note(message.chat.id, name)
    if note:
        bot.reply_to(message, note["content"])
    else:
        bot.reply_to(message, f"❌ Note `{name}` not found!")

@bot.message_handler(commands=['delete'])
def delete_cmd(message):
    if message.chat.type == 'private':
        return
    if not is_admin(message.chat.id, message.from_user.id):
        bot.reply_to(message, "❌ Admin access required!")
        return
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        bot.reply_to(message, "Usage: /delete <note_name>")
        return
    name = args[1].lower()
    if delete_note(message.chat.id, name):
        bot.reply_to(message, f"✅ Note `{name}` deleted!")
    else:
        bot.reply_to(message, f"❌ Note `{name}` not found!")

@bot.message_handler(commands=['lock'])
def lock_cmd(message):
    if message.chat.type == 'private':
        return
    if not is_admin(message.chat.id, message.from_user.id):
        bot.reply_to(message, "❌ Admin access required!")
        return
    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, "Usage: /lock <stickers/gifs/links/forwards/invites/bots>")
        return
    lock_type = args[1].lower()
    settings = get_settings(message.chat.id)
    if lock_type in settings.get("locks", {}):
        settings["locks"][lock_type] = True
        save_settings(message.chat.id, settings)
        bot.reply_to(message, f"🔒 {lock_type.capitalize()} locked!")
    else:
        bot.reply_to(message, f"❌ Invalid lock type! Options: stickers, gifs, links, forwards, invites, bots")

@bot.message_handler(commands=['unlock'])
def unlock_cmd(message):
    if message.chat.type == 'private':
        return
    if not is_admin(message.chat.id, message.from_user.id):
        bot.reply_to(message, "❌ Admin access required!")
        return
    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, "Usage: /unlock <stickers/gifs/links/forwards/invites/bots>")
        return
    lock_type = args[1].lower()
    settings = get_settings(message.chat.id)
    if lock_type in settings.get("locks", {}):
        settings["locks"][lock_type] = False
        save_settings(message.chat.id, settings)
        bot.reply_to(message, f"🔓 {lock_type.capitalize()} unlocked!")
    else:
        bot.reply_to(message, f"❌ Invalid lock type!")

@bot.message_handler(commands=['locks'])
def locks_cmd(message):
    if message.chat.type == 'private':
        return
    if not is_admin(message.chat.id, message.from_user.id):
        bot.reply_to(message, "❌ Admin access required!")
        return
    settings = get_settings(message.chat.id)
    locks = settings.get("locks", {})
    if locks:
        text = "🔒 **Current Locks:**\n\n"
        for lock_type, locked in locks.items():
            text += f"• {lock_type.capitalize()}: {'🔒 Locked' if locked else '🔓 Unlocked'}\n"
        bot.reply_to(message, text)
    else:
        bot.reply_to(message, "🔒 No locks configured.")

@bot.message_handler(commands=['flood'])
def flood_cmd(message):
    if message.chat.type == 'private':
        return
    if not is_admin(message.chat.id, message.from_user.id):
        bot.reply_to(message, "❌ Admin access required!")
        return
    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, "Usage: /flood <count> (messages per 5 seconds)")
        return
    try:
        limit = int(args[1])
        settings = get_settings(message.chat.id)
        settings["antiflood_limit"] = limit
        save_settings(message.chat.id, settings)
        bot.reply_to(message, f"✅ Flood limit set to {limit} messages per 5 seconds!")
    except:
        bot.reply_to(message, "❌ Invalid number!")

@bot.message_handler(commands=['setflood'])
def setflood_cmd(message):
    if message.chat.type == 'private':
        return
    if not is_admin(message.chat.id, message.from_user.id):
        bot.reply_to(message, "❌ Admin access required!")
        return
    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, "Usage: /setflood on/off")
        return
    settings = get_settings(message.chat.id)
    settings["antiflood_enabled"] = args[1].lower() == "on"
    save_settings(message.chat.id, settings)
    bot.reply_to(message, f"✅ Flood control {'ENABLED' if settings['antiflood_enabled'] else 'DISABLED'}!")

@bot.message_handler(commands=['anticommunist'])
def anticommunist_cmd(message):
    if message.chat.type == 'private':
        return
    if not is_admin(message.chat.id, message.from_user.id):
        bot.reply_to(message, "❌ Admin access required!")
        return
    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, "Usage: /anticommunist on/off")
        return
    settings = get_settings(message.chat.id)
    settings["anticommunist_enabled"] = args[1].lower() == "on"
    save_settings(message.chat.id, settings)
    bot.reply_to(message, f"✅ Link protection {'ENABLED' if settings['anticommunist_enabled'] else 'DISABLED'}!")

@bot.message_handler(commands=['antichar'])
def antichar_cmd(message):
    if message.chat.type == 'private':
        return
    if not is_admin(message.chat.id, message.from_user.id):
        bot.reply_to(message, "❌ Admin access required!")
        return
    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, "Usage: /antichar on/off OR /antichar <limit>")
        return
    settings = get_settings(message.chat.id)
    if args[1].lower() == "on" or args[1].lower() == "off":
        settings["antichar_enabled"] = args[1].lower() == "on"
        save_settings(message.chat.id, settings)
        bot.reply_to(message, f"✅ Caps protection {'ENABLED' if settings['antichar_enabled'] else 'DISABLED'}!")
    else:
        try:
            limit = int(args[1])
            settings["antichar_limit"] = limit
            save_settings(message.chat.id, settings)
            bot.reply_to(message, f"✅ Caps limit set to {limit}%!")
        except:
            bot.reply_to(message, "❌ Invalid number!")

@bot.message_handler(commands=['welcome'])
def welcome_cmd(message):
    if message.chat.type == 'private':
        return
    if not is_admin(message.chat.id, message.from_user.id):
        bot.reply_to(message, "❌ Admin access required!")
        return
    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, "Usage: /welcome on/off")
        return
    settings = get_settings(message.chat.id)
    settings["welcome_enabled"] = args[1].lower() == "on"
    save_settings(message.chat.id, settings)
    bot.reply_to(message, f"✅ Welcome messages {'ENABLED' if settings['welcome_enabled'] else 'DISABLED'}!")

@bot.message_handler(commands=['setwelcome'])
def setwelcome_cmd(message):
    if message.chat.type == 'private':
        return
    if not is_admin(message.chat.id, message.from_user.id):
        bot.reply_to(message, "❌ Admin access required!")
        return
    msg = message.text.replace("/setwelcome", "").strip()
    if not msg:
        bot.reply_to(message, "Usage: /setwelcome <message>")
        return
    settings = get_settings(message.chat.id)
    settings["welcome_message"] = msg
    save_settings(message.chat.id, settings)
    bot.reply_to(message, f"✅ Welcome message set!\n\n{msg}")

@bot.message_handler(commands=['goodbye'])
def goodbye_cmd(message):
    if message.chat.type == 'private':
        return
    if not is_admin(message.chat.id, message.from_user.id):
        bot.reply_to(message, "❌ Admin access required!")
        return
    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, "Usage: /goodbye on/off")
        return
    settings = get_settings(message.chat.id)
    settings["goodbye_enabled"] = args[1].lower() == "on"
    save_settings(message.chat.id, settings)
    bot.reply_to(message, f"✅ Goodbye messages {'ENABLED' if settings['goodbye_enabled'] else 'DISABLED'}!")

@bot.message_handler(commands=['setgoodbye'])
def setgoodbye_cmd(message):
    if message.chat.type == 'private':
        return
    if not is_admin(message.chat.id, message.from_user.id):
        bot.reply_to(message, "❌ Admin access required!")
        return
    msg = message.text.replace("/setgoodbye", "").strip()
    if not msg:
        bot.reply_to(message, "Usage: /setgoodbye <message>")
        return
    settings = get_settings(message.chat.id)
    settings["goodbye_message"] = msg
    save_settings(message.chat.id, settings)
    bot.reply_to(message, f"✅ Goodbye message set!\n\n{msg}")

@bot.message_handler(commands=['captcha'])
def captcha_cmd(message):
    if message.chat.type == 'private':
        return
    if not is_admin(message.chat.id, message.from_user.id):
        bot.reply_to(message, "❌ Admin access required!")
        return
    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, "Usage: /captcha on/off")
        return
    settings = get_settings(message.chat.id)
    settings["captcha_enabled"] = args[1].lower() == "on"
    save_settings(message.chat.id, settings)
    bot.reply_to(message, f"✅ CAPTCHA {'ENABLED' if settings['captcha_enabled'] else 'DISABLED'}!")

@bot.message_handler(commands=['schedule'])
def schedule_cmd(message):
    if message.chat.type == 'private':
        return
    if not is_admin(message.chat.id, message.from_user.id):
        bot.reply_to(message, "❌ Admin access required!")
        return
    args = message.text.split(maxsplit=2)
    if len(args) < 3:
        bot.reply_to(message, "Usage: /schedule <minutes> <message>")
        return
    try:
        minutes = int(args[1])
        msg = args[2]
        schedule_id = add_schedule(message.chat.id, minutes, msg, message.from_user.id)
        bot.reply_to(message, f"✅ Message scheduled!\nID: `{schedule_id}`\nWill send in {minutes} minutes.")
    except:
        bot.reply_to(message, "❌ Invalid minutes!")

@bot.message_handler(commands=['schedules'])
def schedules_cmd(message):
    if message.chat.type == 'private':
        return
    if not is_admin(message.chat.id, message.from_user.id):
        bot.reply_to(message, "❌ Admin access required!")
        return
    schedules = load_data(SCHEDULES_FILE, {})
    active = []
    for sid, data in schedules.items():
        if data["chat_id"] == message.chat.id and data["execute_time"] > time.time():
            remaining = int(data["execute_time"] - time.time())
            active.append(f"ID: `{sid}` - {format_time(remaining)} left - {data['message'][:30]}...")
    if active:
        bot.reply_to(message, "⏰ **Active Schedules:**\n\n" + "\n".join(active))
    else:
        bot.reply_to(message, "⏰ No active schedules.")

@bot.message_handler(commands=['cancelschedule'])
def cancelschedule_cmd(message):
    if message.chat.type == 'private':
        return
    if not is_admin(message.chat.id, message.from_user.id):
        bot.reply_to(message, "❌ Admin access required!")
        return
    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, "Usage: /cancelschedule <id>")
        return
    schedules = load_data(SCHEDULES_FILE, {})
    if args[1] in schedules:
        del schedules[args[1]]
        save_data(SCHEDULES_FILE, schedules)
        bot.reply_to(message, f"✅ Schedule {args[1]} cancelled!")
    else:
        bot.reply_to(message, "❌ Schedule not found!")

@bot.message_handler(commands=['analytics'])
def analytics_cmd(message):
    if message.chat.type == 'private':
        return
    if not is_admin(message.chat.id, message.from_user.id):
        bot.reply_to(message, "❌ Admin access required!")
        return
    try:
        member_count = bot.get_chat_members_count(message.chat.id)
        admins = 0
        for member in bot.get_chat_members(message.chat.id, filter="administrators"):
            admins += 1
        top_users, total_msgs = get_analytics(message.chat.id)
        warns = load_data(WARNS_FILE, {})
        warn_count = 0
        for key in warns:
            if key.startswith(f"{message.chat.id}_"):
                warn_count += len(warns[key])
        text = f"📊 **Group Analytics** 📊\n\n"
        text += f"👥 **Members:** {member_count}\n"
        text += f"👑 **Admins:** {admins}\n"
        text += f"💬 **Total Messages:** {total_msgs}\n"
        text += f"⚠️ **Total Warnings:** {warn_count}\n\n"
        text += f"🏆 **Top 10 Active Users:**\n"
        for i, user in enumerate(top_users[:10], 1):
            try:
                u = bot.get_chat_member(message.chat.id, user["user_id"]).user
                name = u.first_name
            except:
                name = str(user["user_id"])
            text += f"{i}. {get_user_link(user['user_id'], name)} - {user['total']} msgs\n"
        bot.reply_to(message, text)
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)[:100]}")

@bot.message_handler(commands=['set'])
def set_cmd(message):
    if message.chat.type == 'private':
        return
    if not is_admin(message.chat.id, message.from_user.id):
        bot.reply_to(message, "❌ Admin access required!")
        return
    args = message.text.split(maxsplit=2)
    if len(args) < 2:
        bot.reply_to(message, "Usage: /set show - Show settings\n/set welcome on/off - Toggle welcome\n/set welcome <message> - Set welcome")
        return
    if args[1] == "show":
        settings = get_settings(message.chat.id)
        text = f"⚙️ **Current Settings** ⚙️\n\n"
        text += f"Welcome: {'✅' if settings['welcome_enabled'] else '❌'}\n"
        text += f"Goodbye: {'✅' if settings['goodbye_enabled'] else '❌'}\n"
        text += f"CAPTCHA: {'✅' if settings['captcha_enabled'] else '❌'}\n"
        text += f"Anti-Flood: {'✅' if settings['antiflood_enabled'] else '❌'} (Limit: {settings['antiflood_limit']})\n"
        text += f"Anti-Char: {'✅' if settings['antichar_enabled'] else '❌'} (Limit: {settings['antichar_limit']}%)\n"
        text += f"Link Protection: {'✅' if settings['anticommunist_enabled'] else '❌'}\n"
        bot.reply_to(message, text)
    elif args[1] == "welcome" and len(args) == 3:
        if args[2].lower() in ["on", "off"]:
            settings = get_settings(message.chat.id)
            settings["welcome_enabled"] = args[2].lower() == "on"
            save_settings(message.chat.id, settings)
            bot.reply_to(message, f"✅ Welcome {'ENABLED' if settings['welcome_enabled'] else 'DISABLED'}!")
        else:
            settings = get_settings(message.chat.id)
            settings["welcome_message"] = args[2]
            save_settings(message.chat.id, settings)
            bot.reply_to(message, f"✅ Welcome message set!")

@bot.message_handler(commands=['info'])
def info_cmd(message):
    if message.chat.type == 'private':
        return
    if not is_admin(message.chat.id, message.from_user.id):
        bot.reply_to(message, "❌ Admin access required!")
        return
    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, "Usage: /info @username")
        return
    user_id, name, username = resolve_user(message.chat.id, args[1])
    if not user_id:
        bot.reply_to(message, "❌ User not found!")
        return
    warns = get_warns(message.chat.id, user_id)
    is_muted_status = is_muted(message.chat.id, user_id)
    text = f"👤 **User Information**\n\n"
    text += f"Name: {get_user_link(user_id, name)}\n"
    text += f"ID: `{user_id}`\n"
    if username:
        text += f"Username: @{username}\n"
    text += f"Warnings: {len(warns)}/3\n"
    text += f"Muted: {'Yes' if is_muted_status else 'No'}\n"
    bot.reply_to(message, text)

@bot.message_handler(commands=['groupinfo'])
def groupinfo_cmd(message):
    if message.chat.type == 'private':
        return
    try:
        chat = bot.get_chat(message.chat.id)
        member_count = bot.get_chat_members_count(message.chat.id)
        admins = 0
        for member in bot.get_chat_members(message.chat.id, filter="administrators"):
            admins += 1
        text = f"📊 **Group Information**\n\n"
        text += f"Name: {chat.title}\n"
        text += f"ID: `{chat.id}`\n"
        if chat.username:
            text += f"Username: @{chat.username}\n"
        text += f"Members: {member_count}\n"
        text += f"Admins: {admins}\n"
        if chat.description:
            text += f"Description: {chat.description[:100]}\n"
        bot.reply_to(message, text)
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)[:100]}")

@bot.message_handler(commands=['admins'])
def admins_cmd(message):
    if message.chat.type == 'private':
        return
    try:
        admin_list = []
        for member in bot.get_chat_members(message.chat.id, filter="administrators"):
            admin_list.append(f"• {get_user_link(member.user.id, member.user.first_name)}")
        text = "👑 **Admin List** 👑\n\n" + "\n".join(admin_list)
        bot.reply_to(message, text)
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)[:100]}")

@bot.message_handler(commands=['block'])
def block_cmd(message):
    if not is_owner(message.from_user.id):
        bot.reply_to(message, "❌ Owner access required!")
        return
    args = message.text.split(maxsplit=2)
    if len(args) < 2:
        bot.reply_to(message, "Usage: /block @username [reason]")
        return
    user_id, name, username = resolve_user(message.chat.id, args[1])
    if not user_id:
        bot.reply_to(message, "❌ User not found!")
        return
    reason = args[2] if len(args) > 2 else "No reason"
    blacklist_user(user_id, reason, message.from_user.id)
    bot.reply_to(message, f"🚫 {get_user_link(user_id, name)} blacklisted!\nReason: {reason}")

@bot.message_handler(commands=['unblock'])
def unblock_cmd(message):
    if not is_owner(message.from_user.id):
        bot.reply_to(message, "❌ Owner access required!")
        return
    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, "Usage: /unblock @username")
        return
    user_id, name, username = resolve_user(message.chat.id, args[1])
    if not user_id:
        bot.reply_to(message, "❌ User not found!")
        return
    if unblacklist_user(user_id):
        bot.reply_to(message, f"✅ {get_user_link(user_id, name)} removed from blacklist!")
    else:
        bot.reply_to(message, "❌ User not blacklisted!")

@bot.message_handler(commands=['blocklist'])
def blocklist_cmd(message):
    if not is_owner(message.from_user.id):
        bot.reply_to(message, "❌ Owner access required!")
        return
    blacklist = load_data(BLACKLIST_FILE, {})
    if blacklist:
        text = "🚫 **Blacklisted Users** 🚫\n\n"
        for uid, data in blacklist.items():
            text += f"• {get_user_link(int(uid))}\n  Reason: {data['reason']}\n"
        bot.reply_to(message, text)
    else:
        bot.reply_to(message, "✅ No blacklisted users.")

@bot.message_handler(commands=['addowner'])
def addowner_cmd(message):
    if not is_owner(message.from_user.id):
        bot.reply_to(message, "❌ Owner access required!")
        return
    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, "Usage: /addowner <user_id>")
        return
    try:
        new_owner = int(args[1])
        if new_owner not in OWNER_IDS:
            OWNER_IDS.append(new_owner)
            config["OWNER_IDS"] = OWNER_IDS
            save_config(config)
            bot.reply_to(message, f"✅ User {new_owner} added as co-owner!")
        else:
            bot.reply_to(message, "❌ User is already an owner!")
    except:
        bot.reply_to(message, "❌ Invalid user ID!")

@bot.message_handler(commands=['removeowner'])
def removeowner_cmd(message):
    if not is_owner(message.from_user.id):
        bot.reply_to(message, "❌ Owner access required!")
        return
    args = message.text.split()
    if len(args) < 2:
        bot.reply_to(message, "Usage: /removeowner <user_id>")
        return
    try:
        rem_owner = int(args[1])
        if rem_owner in OWNER_IDS and rem_owner != OWNER_IDS[0]:
            OWNER_IDS.remove(rem_owner)
            config["OWNER_IDS"] = OWNER_IDS
            save_config(config)
            bot.reply_to(message, f"✅ User {rem_owner} removed from owners!")
        else:
            bot.reply_to(message, "❌ Cannot remove primary owner or user not owner!")
    except:
        bot.reply_to(message, "❌ Invalid user ID!")

@bot.message_handler(commands=['owners'])
def owners_cmd(message):
    if not is_owner(message.from_user.id):
        bot.reply_to(message, "❌ Owner access required!")
        return
    text = "👑 **Bot Owners** 👑\n\n"
    for i, uid in enumerate(OWNER_IDS, 1):
        text += f"{i}. {get_user_link(uid)}"
        if OWNER_USERNAMES and i-1 < len(OWNER_USERNAMES):
            text += f" ({OWNER_USERNAMES[i-1]})"
        text += "\n"
    bot.reply_to(message, text)

# ═══════════════════════════════════════════════════════════════════════
# 🎯 GROUP EVENT HANDLERS
# ═══════════════════════════════════════════════════════════════════════

@bot.message_handler(content_types=['new_chat_members'])
def welcome_new_member(message):
    for new_member in message.new_chat_members:
        if new_member.id == bot.get_me().id:
            continue
        settings = get_settings(message.chat.id)
        if settings.get("welcome_enabled"):
            member_count = message.chat.members_count
            welcome_msg = settings["welcome_message"]
            welcome_msg = welcome_msg.replace("{mention}", new_member.mention)
            welcome_msg = welcome_msg.replace("{name}", new_member.first_name)
            welcome_msg = welcome_msg.replace("{group}", message.chat.title)
            welcome_msg = welcome_msg.replace("{count}", str(member_count))
            bot.reply_to(message, welcome_msg)
        if settings.get("captcha_enabled"):
            question = start_captcha(message.chat.id, new_member.id)
            markup = InlineKeyboardMarkup()
            markup.add(InlineKeyboardButton("❌ Not a robot", callback_data=f"captcha_{new_member.id}"))
            bot.send_message(message.chat.id, f"🔐 {new_member.mention}, solve this CAPTCHA to stay:\n\n{question}", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("captcha_"))
def captcha_callback(call):
    user_id = int(call.data.split("_")[1])
    if call.from_user.id != user_id:
        bot.answer_callback_query(call.id, "This CAPTCHA is not for you!", show_alert=True)
        return
    bot.answer_callback_query(call.id, "Please answer in chat!")
    bot.send_message(call.message.chat.id, f"{call.from_user.mention}, type your answer:")

@bot.message_handler(content_types=['left_chat_member'])
def goodbye_member(message):
    if message.left_chat_member.id == bot.get_me().id:
        return
    settings = get_settings(message.chat.id)
    if settings.get("goodbye_enabled"):
        goodbye_msg = settings["goodbye_message"]
        goodbye_msg = goodbye_msg.replace("{mention}", message.left_chat_member.mention)
        goodbye_msg = goodbye_msg.replace("{name}", message.left_chat_member.first_name)
        goodbye_msg = goodbye_msg.replace("{group}", message.chat.title)
        bot.reply_to(message, goodbye_msg)

@bot.message_handler(func=lambda message: True, content_types=['text'])
def handle_messages(message):
    if message.chat.type == 'private':
        return
    if is_blacklisted(message.from_user.id):
        try:
            bot.kick_chat_member(message.chat.id, message.from_user.id)
        except:
            pass
        return
    if is_muted(message.chat.id, message.from_user.id):
        try:
            bot.delete_message(message.chat.id, message.message_id)
        except:
            pass
        return
    if check_flood(message.chat.id, message.from_user.id):
        try:
            bot.delete_message(message.chat.id, message.message_id)
            bot.send_message(message.chat.id, f"🚫 {message.from_user.mention} muted for flooding!")
        except:
            pass
        return
    settings = get_settings(message.chat.id)
    if settings.get("anticommunist_enabled"):
        if "t.me/" in message.text or "telegram.me/" in message.text:
            if not is_admin(message.chat.id, message.from_user.id):
                try:
                    bot.delete_message(message.chat.id, message.message_id)
                except:
                    pass
    if settings.get("antichar_enabled"):
        caps = sum(1 for c in message.text if c.isupper())
        letters = sum(1 for c in message.text if c.isalpha())
        if letters > 0:
            caps_percent = (caps / letters) * 100
            if caps_percent > settings.get("antichar_limit", 60):
                if not is_admin(message.chat.id, message.from_user.id):
                    try:
                        bot.delete_message(message.chat.id, message.message_id)
                    except:
                        pass
    if check_filter(message.chat.id, message.text):
        if not is_admin(message.chat.id, message.from_user.id):
            try:
                bot.delete_message(message.chat.id, message.message_id)
                bot.send_message(message.chat.id, f"⚠️ {message.from_user.mention}, filtered word detected!")
            except:
                pass
    track_message(message.chat.id, message.from_user.id)
    settings = get_settings(message.chat.id)
    locks = settings.get("locks", {})
    if message.sticker and locks.get("stickers", False):
        if not is_admin(message.chat.id, message.from_user.id):
            try:
                bot.delete_message(message.chat.id, message.message_id)
            except:
                pass
    if message.animation and locks.get("gifs", False):
        if not is_admin(message.chat.id, message.from_user.id):
            try:
                bot.delete_message(message.chat.id, message.message_id)
            except:
                pass
    if message.forward_from and locks.get("forwards", False):
        if not is_admin(message.chat.id, message.from_user.id):
            try:
                bot.delete_message(message.chat.id, message.message_id)
            except:
                pass
    text = message.text or message.caption or ""
    if text.startswith('#'):
        note_name = text[1:].split()[0].lower()
        note = get_note(message.chat.id, note_name)
        if note:
            bot.reply_to(message, note["content"])

# ═══════════════════════════════════════════════════════════════════════
# 🚀 START THE BOT
# ═══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("\n" + "="*60)
    print("💀 NEON AI GROUP MANAGER BOT STARTED 💀")
    print("="*60)
    print(f"👑 Owners: {', '.join([str(uid) for uid in OWNER_IDS])}")
    print(f"🤖 Bot Token: {BOT_TOKEN[:10]}...")
    print("✅ Bot is running...")
    print("="*60 + "\n")
    
    load_schedules()
    
    while True:
        try:
            bot.polling(none_stop=True, timeout=60)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(10)