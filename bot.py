# =========================
# ERA x PANEL - COMPLETE BOT CODE
# EXTRA LINK SYSTEM REMOVED
# ALL OTHER FEATURES WORKING
# =========================

import sqlite3
import random
import string
from datetime import datetime
import telebot
from telebot import types

# =========================
# CONFIGURATION
# =========================

BOT_TOKEN = "8952774592:AAHmy_dZ43Z9C-BMNNolf2zKdSVSGfC8CkM"
ADMIN_IDS = [7998643430]
ADMIN_USERNAME = "@R1898114"
MIN_WITHDRAW = 100

FORCE_CHANNELS = [
    {"name": "Era X Army", "username": "@eraXarmy"},
    {"name": "Era X Earning", "username": "@eraXearning"}
]

bot = telebot.TeleBot(BOT_TOKEN)

# =========================
# DATABASE SETUP
# =========================

def init_db():
    conn = sqlite3.connect("era_panel.db")
    cursor = conn.cursor()
    
    # Coupons Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS coupons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE,
            discount INTEGER,
            max_uses INTEGER DEFAULT 100,
            times_used INTEGER DEFAULT 0,
            status TEXT DEFAULT 'Active',
            created_at TEXT
        )
    ''')
    
    # Products Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            price REAL,
            apk_link TEXT,
            web_link TEXT,
            qr_file_id TEXT
        )
    ''')
    
    # Users Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            full_name TEXT,
            add_money_balance REAL DEFAULT 0,
            withdrawal_balance REAL DEFAULT 0,
            referred_by TEXT,
            referrals INTEGER DEFAULT 0
        )
    ''')
    
    # Used Coupons Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS used_coupons (
            user_id INTEGER,
            coupon_code TEXT,
            used_at TEXT,
            PRIMARY KEY (user_id, coupon_code)
        )
    ''')
    
    # Withdraw Requests Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS withdraw_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT,
            full_name TEXT,
            amount REAL,
            upi_id TEXT,
            status TEXT DEFAULT 'Pending',
            created_at TEXT
        )
    ''')
    
    # App Settings Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS app_settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')
    
    # Referral Rewards Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS refer_rewards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            refer_count INTEGER UNIQUE,
            reward_type TEXT,
            reward_value TEXT,
            created_at TEXT
        )
    ''')
    
    # Add default products if none exist
    cursor.execute("SELECT COUNT(*) FROM products")
    count = cursor.fetchone()[0]
    
    if count == 0:
        default_products = [
            ("SAM X PANEL", 99.0, "https://t.me/R1898114", "https://t.me/R1898114"),
            ("ULTIMATE PANEL", 99.0, "https://t.me/R1898114", "https://t.me/R1898114"),
            ("GOD x PANEL", 99.0, "https://t.me/R1898114", "https://t.me/R1898114"),
            ("ALEXA PANEL", 99.0, "https://t.me/R1898114", "https://t.me/R1898114"),
            ("HACKER XPANEL", 99.0, "https://t.me/R1898114", "https://t.me/R1898114"),
            ("XCORE PANEL", 99.0, "https://t.me/R1898114", "https://t.me/R1898114"),
            ("ANNE BELA PANEL", 99.0, "https://t.me/R1898114", "https://t.me/R1898114"),
            ("VIP YN (YONO) PANEL", 99.0, "https://t.me/R1898114", "https://t.me/R1898114"),
            ("9000 + NUMBER PACKAGE", 999.0, "https://t.me/R1898114", "https://t.me/R1898114"),
        ]
        
        for name, price, apk, web in default_products:
            cursor.execute('''
                INSERT INTO products (name, price, apk_link, web_link)
                VALUES (?, ?, ?, ?)
            ''', (name, price, apk, web))
        
        conn.commit()
        print("✅ Default products added!")
    
    conn.commit()
    conn.close()
    print("✅ Database initialized!")

init_db()

# =========================
# SYSTEM BUTTONS
# =========================

SYSTEM_BUTTONS = [
    "🔑 Panel Password", "👤 Profile", "👥 Refer",
    "💳 Balance", "💰 Add Money", "🛒 Buy Panel", "💵 Withdraw",
    "📞 Support", "⚙️ Admin Panel", "🎫 Manage Coupons", "⬅️ Main Menu",
    "👥 Total Users", "🖼 Set Project QR", "➕ Create New Coupon",
    "📋 List All Coupons", "🗑 Delete Coupon by ID", "🔄 Toggle Active/Inactive",
    "⬅️ Back to Admin", "🛒 Add Product", "🗑 Remove Product",
    "💰 Edit Product Price", "📸 Set Add Money QR", "👥 Per Refer Set",
    "📂 Manage Saved Rewards", "📢 Broadcast", "💰 Edit User Balance", 
    "📋 Withdraw Requests"
]

# =========================
# KEYBOARDS
# =========================

def main_menu_keyboard(user_id=None):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("🔑 Panel Password", "👤 Profile")
    markup.add("👥 Refer")
    markup.add("💳 Balance", "💰 Add Money")
    markup.add("🛒 Buy Panel", "💵 Withdraw")
    markup.add("📞 Support")
    
    if user_id in ADMIN_IDS:
        markup.add("⚙️ Admin Panel")
    
    return markup

def admin_menu_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("👥 Total Users", "💰 Edit User Balance")
    markup.add("📋 Withdraw Requests")
    markup.add("🛒 Add Product", "🗑 Remove Product")
    markup.add("💰 Edit Product Price", "🖼 Set Project QR")
    markup.add("📸 Set Add Money QR", "👥 Per Refer Set")
    markup.add("📂 Manage Saved Rewards", "📢 Broadcast")
    markup.add("🎫 Manage Coupons", "⬅️ Main Menu")
    return markup

def coupon_menu_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("➕ Create New Coupon", "📋 List All Coupons")
    markup.add("🗑 Delete Coupon by ID", "🔄 Toggle Active/Inactive")
    markup.add("⬅️ Back to Admin")
    return markup

def force_join_keyboard():
    markup = types.InlineKeyboardMarkup(row_width=1)
    for channel in FORCE_CHANNELS:
        markup.add(types.InlineKeyboardButton(
            f"📢 Join {channel['name']}",
            url=f"https://t.me/{channel['username'].replace('@', '')}"
        ))
    markup.add(types.InlineKeyboardButton("✅ I have joined", callback_data="check_force_join"))
    return markup

# =========================
# FORCE CHANNEL JOIN CHECK
# =========================

def is_user_subscribed(user_id):
    try:
        for channel in FORCE_CHANNELS:
            member = bot.get_chat_member(channel['username'], user_id)
            if member.status in ['left', 'kicked']:
                return False
        return True
    except:
        return False

# =========================
# DATABASE FUNCTIONS
# =========================

def get_coupon_by_code(code):
    conn = sqlite3.connect("era_panel.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, code, discount, max_uses, times_used, status FROM coupons WHERE code = ?", (code,))
    result = cursor.fetchone()
    conn.close()
    return result

def get_all_coupons():
    conn = sqlite3.connect("era_panel.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, code, discount, max_uses, times_used, status FROM coupons ORDER BY id")
    rows = cursor.fetchall()
    conn.close()
    return rows

def create_coupon(code, discount, max_uses=100):
    conn = sqlite3.connect("era_panel.db")
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO coupons (code, discount, max_uses, created_at) VALUES (?, ?, ?, ?)",
            (code, discount, max_uses, datetime.now().isoformat())
        )
        conn.commit()
        inserted_id = cursor.lastrowid
        conn.close()
        return inserted_id, True
    except sqlite3.IntegrityError:
        conn.close()
        return None, False

def delete_coupon_by_id(coupon_id):
    conn = sqlite3.connect("era_panel.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM coupons WHERE id = ?", (coupon_id,))
    deleted = cursor.rowcount
    
    if deleted > 0:
        cursor.execute("SELECT COUNT(*) FROM coupons")
        count = cursor.fetchone()[0]
        if count == 0:
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='coupons'")
    conn.commit()
    conn.close()
    return deleted > 0

def toggle_coupon_status(code):
    conn = sqlite3.connect("era_panel.db")
    cursor = conn.cursor()
    cursor.execute("SELECT status FROM coupons WHERE code = ?", (code,))
    result = cursor.fetchone()
    
    if not result:
        conn.close()
        return None
    
    new_status = "Inactive" if result[0] == "Active" else "Active"
    cursor.execute("UPDATE coupons SET status = ? WHERE code = ?", (new_status, code))
    conn.commit()
    conn.close()
    return new_status

def is_coupon_used_by_user(user_id, coupon_code):
    conn = sqlite3.connect("era_panel.db")
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM used_coupons WHERE user_id = ? AND coupon_code = ?", (user_id, coupon_code))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def mark_coupon_used(user_id, coupon_code):
    conn = sqlite3.connect("era_panel.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO used_coupons (user_id, coupon_code, used_at) VALUES (?, ?, ?)",
        (user_id, coupon_code, datetime.now().isoformat())
    )
    cursor.execute("UPDATE coupons SET times_used = times_used + 1 WHERE code = ?", (coupon_code,))
    conn.commit()
    conn.close()

def add_user_if_not_exists(user_id, username, full_name):
    conn = sqlite3.connect("era_panel.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR IGNORE INTO users (user_id, username, full_name) VALUES (?, ?, ?)",
        (user_id, username or "", full_name or "User")
    )
    conn.commit()
    conn.close()

def get_user_balance(user_id):
    conn = sqlite3.connect("era_panel.db")
    cursor = conn.cursor()
    cursor.execute("SELECT add_money_balance, withdrawal_balance FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result if result else (0.0, 0.0)

def update_user_withdrawal_balance(user_id, amount):
    conn = sqlite3.connect("era_panel.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET withdrawal_balance = withdrawal_balance - ? WHERE user_id = ?", (amount, user_id))
    conn.commit()
    conn.close()

def get_all_products():
    conn = sqlite3.connect("era_panel.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, price, apk_link, web_link, qr_file_id FROM products")
    products = cursor.fetchall()
    conn.close()
    return products

def get_product_by_id(product_id):
    conn = sqlite3.connect("era_panel.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, price, apk_link, web_link, qr_file_id FROM products WHERE id = ?", (product_id,))
    product = cursor.fetchone()
    conn.close()
    return product

def update_product_qr(product_id, qr_file_id):
    conn = sqlite3.connect("era_panel.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE products SET qr_file_id = ? WHERE id = ?", (qr_file_id, product_id))
    conn.commit()
    conn.close()

def get_user(user_id):
    conn = sqlite3.connect("era_panel.db")
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, username, full_name, add_money_balance, withdrawal_balance, referrals FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result

def get_user_by_id(user_id):
    conn = sqlite3.connect("era_panel.db")
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, username, full_name, add_money_balance, withdrawal_balance, referrals FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result

def update_user_balance(user_id, new_balance):
    conn = sqlite3.connect("era_panel.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET add_money_balance = ? WHERE user_id = ?", (new_balance, user_id))
    updated = cursor.rowcount
    conn.commit()
    conn.close()
    return updated > 0

def get_setting(key):
    conn = sqlite3.connect("era_panel.db")
    cursor = conn.cursor()
    cursor.execute("SELECT value FROM app_settings WHERE key = ?", (key,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def save_setting(key, value):
    conn = sqlite3.connect("era_panel.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO app_settings (key, value) VALUES (?, ?)", (key, value))
    conn.commit()
    conn.close()

# =========================
# REFERRAL REWARD FUNCTIONS
# =========================

def add_refer_reward(refer_count, reward_type, reward_value):
    conn = sqlite3.connect("era_panel.db")
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO refer_rewards (refer_count, reward_type, reward_value, created_at) VALUES (?, ?, ?, ?)",
            (refer_count, reward_type, reward_value, datetime.now().isoformat())
        )
        inserted_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return inserted_id, True
    except sqlite3.IntegrityError:
        conn.close()
        return None, False

def get_all_refer_rewards():
    conn = sqlite3.connect("era_panel.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, refer_count, reward_type, reward_value FROM refer_rewards ORDER BY refer_count")
    rows = cursor.fetchall()
    conn.close()
    return rows

def delete_refer_reward(reward_id):
    conn = sqlite3.connect("era_panel.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM refer_rewards WHERE id = ?", (reward_id,))
    deleted = cursor.rowcount
    conn.commit()
    conn.close()
    return deleted > 0

def get_refer_reward_by_count(refer_count):
    conn = sqlite3.connect("era_panel.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, refer_count, reward_type, reward_value FROM refer_rewards WHERE refer_count = ?", (refer_count,))
    result = cursor.fetchone()
    conn.close()
    return result

def credit_referral_reward(referrer_id):
    conn = sqlite3.connect("era_panel.db")
    cursor = conn.cursor()
    cursor.execute("SELECT referrals FROM users WHERE user_id = ?", (referrer_id,))
    result = cursor.fetchone()
    
    if result:
        refer_count = result[0]
        
        cursor.execute("SELECT reward_type, reward_value FROM refer_rewards WHERE refer_count = ?", (refer_count,))
        reward = cursor.fetchone()
        conn.close()
        
        if reward:
            reward_type, reward_value = reward
            
            try:
                if reward_type == "apk":
                    bot.send_document(referrer_id, reward_value, caption=f"🎁 Reward for {refer_count} referrals!")
                elif reward_type == "panel":
                    bot.send_message(referrer_id, f"🎁 Reward for {refer_count} referrals!\n\n🔑 Panel Access:\n{reward_value}")
                else:
                    bot.send_message(referrer_id, f"🎁 Reward for {refer_count} referrals!\n\n{reward_value}")
            except:
                pass
            return True
    
    conn.close()
    return False

def update_user_referrals(user_id, amount=1):
    conn = sqlite3.connect("era_panel.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET referrals = referrals + ? WHERE user_id = ?", (amount, user_id))
    conn.commit()
    conn.close()

# =========================
# WITHDRAW FUNCTIONS
# =========================

def create_withdraw_request(user_id, username, full_name, amount, upi_id):
    conn = sqlite3.connect("era_panel.db")
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO withdraw_requests (user_id, username, full_name, amount, upi_id, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, username, full_name, amount, upi_id, datetime.now().isoformat()))
    request_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return request_id

def get_withdraw_requests(status="Pending"):
    conn = sqlite3.connect("era_panel.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, user_id, username, full_name, amount, upi_id, status, created_at FROM withdraw_requests WHERE status = ? ORDER BY created_at DESC", (status,))
    results = cursor.fetchall()
    conn.close()
    return results

def update_withdraw_status(request_id, status):
    conn = sqlite3.connect("era_panel.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE withdraw_requests SET status = ? WHERE id = ?", (status, request_id))
    updated = cursor.rowcount
    conn.commit()
    conn.close()
    return updated > 0

# =========================
# COMMAND HANDLERS
# =========================

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    add_user_if_not_exists(user_id, message.from_user.username, message.from_user.full_name)
    
    if not is_user_subscribed(user_id):
        text = "⚠️ **ACCESS DENIED!**\n\nBot use karne ke liye aapko hamare dono channels join karna zaroori hai:"
        bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=force_join_keyboard())
        return
    
    args = message.text.split()
    if len(args) > 1:
        referrer_id = args[1]
        if referrer_id.isdigit() and int(referrer_id) != user_id:
            conn = sqlite3.connect("era_panel.db")
            cursor = conn.cursor()
            cursor.execute("SELECT referred_by FROM users WHERE user_id = ?", (user_id,))
            result = cursor.fetchone()
            
            if result and result[0] is None:
                cursor.execute("UPDATE users SET referred_by = ? WHERE user_id = ?", (referrer_id, user_id))
                conn.commit()
                
                update_user_referrals(int(referrer_id))
                
                cursor.execute("UPDATE users SET add_money_balance = add_money_balance + 5, withdrawal_balance = withdrawal_balance + 5 WHERE user_id = ?", (int(referrer_id),))
                conn.commit()
                
                credit_referral_reward(int(referrer_id))
                
                try:
                    bot.send_message(int(referrer_id), f"🎉 Aapke referral ne join kiya!\n💰 ₹5 Deposit aur ₹5 Withdrawal balance me mil chuke hain!")
                except:
                    pass
            conn.close()
    
    welcome_text = "🎉 WELCOME TO ERA x PANEL 📱!"
    bot.send_message(message.chat.id, welcome_text, reply_markup=main_menu_keyboard(user_id))

@bot.callback_query_handler(func=lambda call: call.data == "check_force_join")
def check_force_join(call):
    user_id = call.from_user.id
    
    if is_user_subscribed(user_id):
        bot.answer_callback_query(call.id, "✅ Verification successful!")
        bot.delete_message(call.message.chat.id, call.message.message_id)
        
        welcome_text = "🎉 WELCOME TO ERA x PANEL 📱!"
        bot.send_message(call.message.chat.id, welcome_text, reply_markup=main_menu_keyboard(user_id))
    else:
        bot.answer_callback_query(call.id, "❌ Aapne abhi tak channels join nahi kiye!", show_alert=True)

@bot.message_handler(func=lambda msg: msg.text == "⬅️ Main Menu")
def main_menu(message):
    user_id = message.from_user.id
    
    if not is_user_subscribed(user_id):
        text = "⚠️ **ACCESS DENIED!**\n\nBot use karne ke liye aapko hamare dono channels join karna zaroori hai:"
        bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=force_join_keyboard())
        return
    
    bot.send_message(message.chat.id, "🏠 Main Menu", reply_markup=main_menu_keyboard(user_id))

@bot.message_handler(func=lambda msg: msg.text == "⚙️ Admin Panel")
def admin_panel(message):
    if message.from_user.id not in ADMIN_IDS:
        bot.send_message(message.chat.id, "❌ Access Denied! Only admins can use this.")
        return
    bot.send_message(message.chat.id, "⚙️ Admin Dashboard Controls:", reply_markup=admin_menu_keyboard())

@bot.message_handler(func=lambda msg: msg.text == "⬅️ Back to Admin")
def back_to_admin(message):
    admin_panel(message)

@bot.message_handler(func=lambda msg: msg.text == "🎫 Manage Coupons")
def manage_coupons(message):
    if message.from_user.id not in ADMIN_IDS:
        bot.send_message(message.chat.id, "❌ Access Denied!")
        return
    bot.send_message(message.chat.id, "🎫 COUPON MANAGEMENT\n\nSelect an action below:", reply_markup=coupon_menu_keyboard())

# =========================
# MAIN BUTTON HANDLERS (No Extra Earning)
# =========================

@bot.message_handler(func=lambda msg: msg.text == "👤 Profile")
def profile(message):
    user_id = message.from_user.id
    
    if not is_user_subscribed(user_id):
        text = "⚠️ **ACCESS DENIED!**\n\nBot use karne ke liye aapko hamare dono channels join karna zaroori hai:"
        bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=force_join_keyboard())
        return
    
    add_money, withdrawal = get_user_balance(user_id)
    
    conn = sqlite3.connect("era_panel.db")
    cursor = conn.cursor()
    cursor.execute("SELECT referrals FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    referrals = result[0] if result else 0
    conn.close()
    
    profile_text = (
        f"────────────────\n"
        f"👤 YOUR PROFILE\n\n"
        f"🆔 User ID: {user_id}\n"
        f"📛 Name: {message.from_user.full_name}\n"
        f"🔗 Username: @{message.from_user.username or 'N/A'}\n"
        f"👥 Referrals: {referrals}\n"
        f"💰 Add Money Balance: ₹{add_money:.2f}\n"
        f"💸 Withdrawal Balance: ₹{withdrawal:.2f}\n"
        f"────────────────"
    )
    bot.send_message(message.chat.id, profile_text)

@bot.message_handler(func=lambda msg: msg.text == "💳 Balance")
def balance(message):
    user_id = message.from_user.id
    
    if not is_user_subscribed(user_id):
        text = "⚠️ **ACCESS DENIED!**\n\nBot use karne ke liye aapko hamare dono channels join karna zaroori hai:"
        bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=force_join_keyboard())
        return
    
    add_money, withdrawal = get_user_balance(user_id)
    
    balance_text = (
        f"────────────────\n"
        f"💳 Your Wallet\n\n"
        f"💰 Add Money Balance: ₹{add_money:.2f}\n"
        f"💸 Withdrawal Balance: ₹{withdrawal:.2f}\n\n"
        f"🆔 User ID: {user_id}\n"
        f"────────────────"
    )
    bot.send_message(message.chat.id, balance_text)

@bot.message_handler(func=lambda msg: msg.text == "🔑 Panel Password")
def panel_password(message):
    user_id = message.from_user.id
    
    if not is_user_subscribed(user_id):
        text = "⚠️ **ACCESS DENIED!**\n\nBot use karne ke liye aapko hamare dono channels join karna zaroori hai:"
        bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=force_join_keyboard())
        return
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔑 Open Panel", url="https://t.me/eraXcrack_bot"))
    bot.send_message(
        message.chat.id,
        "────────────────\n"
        "🔑 PANEL PASSWORD\n\n"
        "📱 Get Your Panel Access:\n"
        "Click the button below to access the panel.\n"
        "────────────────",
        reply_markup=markup
    )

@bot.message_handler(func=lambda msg: msg.text == "👥 Refer")
def refer(message):
    user_id = message.from_user.id
    
    if not is_user_subscribed(user_id):
        text = "⚠️ **ACCESS DENIED!**\n\nBot use karne ke liye aapko hamare dono channels join karna zaroori hai:"
        bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=force_join_keyboard())
        return
    
    bot_info = bot.get_me()
    link = f"https://t.me/{bot_info.username}?start={message.from_user.id}"
    
    conn = sqlite3.connect("era_panel.db")
    cursor = conn.cursor()
    cursor.execute("SELECT referrals FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    referrals = result[0] if result else 0
    conn.close()
    
    next_level = referrals + 1
    reward = get_refer_reward_by_count(next_level)
    
    reward_msg = ""
    if reward:
        reward_msg = f"\n🎯 Next Reward: {next_level} referrals!"
    
    bot.send_message(
        message.chat.id,
        f"👥 REFER AND EARN\n\n"
        f"👥 Your Referrals: {referrals}\n"
        f"💰 Per Active Refer: ₹5 Deposit + ₹5 Withdrawal\n"
        f"{reward_msg}\n\n"
        f"🔗 Your Link:\n{link}"
    )

@bot.message_handler(func=lambda msg: msg.text == "📞 Support")
def support(message):
    user_id = message.from_user.id
    
    if not is_user_subscribed(user_id):
        text = "⚠️ **ACCESS DENIED!**\n\nBot use karne ke liye aapko hamare dono channels join karna zaroori hai:"
        bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=force_join_keyboard())
        return
    
    bot.send_message(
        message.chat.id,
        f"────────────────\n"
        f"📞 SUPPORT CENTER\n\n"
        f"🧑‍💻 Contact Admin Directly:\n👉 {ADMIN_USERNAME}\n\n"
        f"Thank You ❤️\n"
        f"────────────────"
    )

@bot.message_handler(func=lambda msg: msg.text == "💰 Add Money")
def add_money(message):
    user_id = message.from_user.id
    
    if not is_user_subscribed(user_id):
        text = "⚠️ **ACCESS DENIED!**\n\nBot use karne ke liye aapko hamare dono channels join karna zaroori hai:"
        bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=force_join_keyboard())
        return
    
    qr_file_id = get_setting("add_money_qr")
    
    text = f"💰 ADD MONEY\n\nSupport Context: {ADMIN_USERNAME}\n\nNiche diye QR code par payment karke screenshot yahan bhejein."
    
    if qr_file_id:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("📤 Submit Screenshot", callback_data="submit_screenshot"))
        bot.send_photo(message.chat.id, qr_file_id, caption=text, reply_markup=markup)
    else:
        bot.send_message(
            message.chat.id,
            f"💰 ADD MONEY\n\nSupport Context: {ADMIN_USERNAME}\n\nQR code not set yet. Please contact admin.",
            reply_markup=main_menu_keyboard(user_id)
        )

# =========================
# BUY PANEL
# =========================

@bot.message_handler(func=lambda msg: msg.text == "🛒 Buy Panel")
def buy_panel(message):
    user_id = message.from_user.id
    
    if not is_user_subscribed(user_id):
        text = "⚠️ **ACCESS DENIED!**\n\nBot use karne ke liye aapko hamare dono channels join karna zaroori hai:"
        bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=force_join_keyboard())
        return
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    
    products = get_all_products()
    
    if products:
        for pid, name, price, apk, web, qr in products:
            markup.add(types.InlineKeyboardButton(f"🛒 {name} - ₹{price}", callback_data=f"buy_{pid}"))
    else:
        markup.add(types.InlineKeyboardButton("⚠️ No Products Available", callback_data="no_product"))
    
    markup.add(types.InlineKeyboardButton("🎫 Apply Coupon", callback_data="show_coupon_input"))
    
    bot.send_message(message.chat.id, "🛒 BUY PANEL\n\nChoose a plan:", reply_markup=markup)

# =========================
# WITHDRAW SYSTEM
# =========================

@bot.message_handler(func=lambda msg: msg.text == "💵 Withdraw")
def withdraw_start(message):
    user_id = message.from_user.id
    
    if not is_user_subscribed(user_id):
        text = "⚠️ **ACCESS DENIED!**\n\nBot use karne ke liye aapko hamare dono channels join karna zaroori hai:"
        bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=force_join_keyboard())
        return
    
    add_money, withdrawal = get_user_balance(user_id)
    
    if withdrawal < MIN_WITHDRAW:
        bot.send_message(
            message.chat.id,
            f"💵 WITHDRAW PANEL\n\n"
            f"💰 Your Balance: ₹{withdrawal:.2f}\n"
            f"⚠️ Minimum Withdrawal: ₹{MIN_WITHDRAW}\n\n"
            f"❌ Aapka balance minimum withdrawal limit se kam hai!",
            reply_markup=main_menu_keyboard(user_id)
        )
        return
    
    msg = bot.send_message(
        message.chat.id,
        f"💵 WITHDRAW PANEL\n\n"
        f"💰 Your Balance: ₹{withdrawal:.2f}\n"
        f"⚠️ Minimum Withdrawal: ₹{MIN_WITHDRAW}\n\n"
        f"✍️ Jitna amount withdraw karna chahte hain enter karein:",
        reply_markup=main_menu_keyboard(user_id)
    )
    bot.register_next_step_handler(msg, process_withdraw_amount)

def process_withdraw_amount(message):
    if message.text in SYSTEM_BUTTONS:
        handle_menu_redirect(message)
        return
    
    user_id = message.from_user.id
    add_money, withdrawal = get_user_balance(user_id)
    
    try:
        amount = float(message.text.strip())
        if amount < MIN_WITHDRAW:
            msg = bot.send_message(
                message.chat.id,
                f"❌ Minimum withdrawal amount ₹{MIN_WITHDRAW} hai!\n\n"
                f"✍️ Please enter amount again:"
            )
            bot.register_next_step_handler(msg, process_withdraw_amount)
            return
        
        if amount > withdrawal:
            msg = bot.send_message(
                message.chat.id,
                f"❌ Aapke paas itna balance nahi hai!\n"
                f"💰 Your Balance: ₹{withdrawal:.2f}\n\n"
                f"✍️ Please enter amount again:"
            )
            bot.register_next_step_handler(msg, process_withdraw_amount)
            return
        
        msg = bot.send_message(
            message.chat.id,
            f"✍️ Apna UPI ID enter karein (e.g. example@upi):"
        )
        bot.register_next_step_handler(msg, process_withdraw_upi, amount)
        
    except ValueError:
        msg = bot.send_message(
            message.chat.id,
            "❌ Galat format! Kripya sirf number enter karein:"
        )
        bot.register_next_step_handler(msg, process_withdraw_amount)

def process_withdraw_upi(message, amount):
    if message.text in SYSTEM_BUTTONS:
        handle_menu_redirect(message)
        return
    
    user_id = message.from_user.id
    upi_id = message.text.strip()
    
    if not upi_id or len(upi_id) < 5:
        msg = bot.send_message(
            message.chat.id,
            "❌ Galat UPI ID! Kripya sahi UPI ID enter karein:"
        )
        bot.register_next_step_handler(msg, process_withdraw_upi, amount)
        return
    
    user = get_user(user_id)
    username = user[1] or "N/A"
    full_name = user[2] or "User"
    
    update_user_withdrawal_balance(user_id, amount)
    
    request_id = create_withdraw_request(user_id, username, full_name, amount, upi_id)
    
    bot.send_message(
        message.chat.id,
        f"✅ Withdrawal request submitted successfully!\n\n"
        f"📋 Request ID: #{request_id}\n"
        f"💰 Amount: ₹{amount:.2f}\n"
        f"📱 UPI: {upi_id}\n\n"
        f"⏳ Admin will process your request soon.",
        reply_markup=main_menu_keyboard(user_id)
    )
    
    admin_text = (
        f"💵 NEW WITHDRAW REQUEST\n\n"
        f"📋 Request ID: #{request_id}\n"
        f"👤 User: {full_name}\n"
        f"🆔 User ID: {user_id}\n"
        f"💰 Amount: ₹{amount:.2f}\n"
        f"📱 UPI: {upi_id}\n"
        f"📅 Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
        f"Status: ⏳ Pending"
    )
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("✅ Approve", callback_data=f"approve_withdraw_{request_id}"),
        types.InlineKeyboardButton("❌ Reject", callback_data=f"reject_withdraw_{request_id}")
    )
    
    for admin_id in ADMIN_IDS:
        try:
            bot.send_message(admin_id, admin_text, reply_markup=markup)
        except:
            pass

# =========================
# ADMIN - WITHDRAW REQUESTS
# =========================

@bot.message_handler(func=lambda msg: msg.text == "📋 Withdraw Requests")
def withdraw_requests(message):
    if message.from_user.id not in ADMIN_IDS:
        bot.send_message(message.chat.id, "❌ Access Denied!")
        return
    
    requests = get_withdraw_requests("Pending")
    
    if not requests:
        bot.send_message(message.chat.id, "📭 No pending withdraw requests!", reply_markup=admin_menu_keyboard())
        return
    
    text = "📋 PENDING WITHDRAW REQUESTS\n\n"
    for req in requests:
        rid, uid, username, full_name, amount, upi, status, created = req
        text += f"━━━━━━━━━━━━━━━━━━\n"
        text += f"🆔 Request ID: #{rid}\n"
        text += f"👤 User: {full_name}\n"
        text += f"🆔 User ID: {uid}\n"
        text += f"💰 Amount: ₹{amount:.2f}\n"
        text += f"📱 UPI: {upi}\n"
        text += f"━━━━━━━━━━━━━━━━━━\n\n"
    
    bot.send_message(message.chat.id, text, reply_markup=admin_menu_keyboard())

# =========================
# WITHDRAW CALLBACKS
# =========================

@bot.callback_query_handler(func=lambda call: call.data.startswith("approve_withdraw_"))
def approve_withdraw(call):
    user_id = call.from_user.id
    
    if user_id not in ADMIN_IDS:
        bot.answer_callback_query(call.id, "❌ Only admins can do this!", show_alert=True)
        return
    
    request_id = int(call.data.replace("approve_withdraw_", ""))
    
    if update_withdraw_status(request_id, "Approved"):
        bot.answer_callback_query(call.id, "✅ Withdraw approved!")
        bot.edit_message_text(
            call.message.text + "\n\n✅ APPROVED",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=None
        )
        
        conn = sqlite3.connect("era_panel.db")
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, amount FROM withdraw_requests WHERE id = ?", (request_id,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            user_id, amount = result
            try:
                bot.send_message(
                    user_id,
                    f"✅ Your withdraw request of ₹{amount:.2f} has been APPROVED!"
                )
            except:
                pass
    else:
        bot.answer_callback_query(call.id, "❌ Failed to approve!")

@bot.callback_query_handler(func=lambda call: call.data.startswith("reject_withdraw_"))
def reject_withdraw(call):
    user_id = call.from_user.id
    
    if user_id not in ADMIN_IDS:
        bot.answer_callback_query(call.id, "❌ Only admins can do this!", show_alert=True)
        return
    
    request_id = int(call.data.replace("reject_withdraw_", ""))
    
    if update_withdraw_status(request_id, "Rejected"):
        bot.answer_callback_query(call.id, "❌ Withdraw rejected!")
        bot.edit_message_text(
            call.message.text + "\n\n❌ REJECTED",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=None
        )
        
        conn = sqlite3.connect("era_panel.db")
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, amount FROM withdraw_requests WHERE id = ?", (request_id,))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            user_id, amount = result
            try:
                bot.send_message(
                    user_id,
                    f"❌ Your withdraw request of ₹{amount:.2f} has been REJECTED!"
                )
            except:
                pass
    else:
        bot.answer_callback_query(call.id, "❌ Failed to reject!")

# =========================
# DEPOSIT APPROVE/REJECT
# =========================

@bot.callback_query_handler(func=lambda call: call.data.startswith("approve_deposit_"))
def approve_deposit(call):
    user_id = int(call.data.replace("approve_deposit_", ""))
    
    if call.from_user.id not in ADMIN_IDS:
        bot.answer_callback_query(call.id, "❌ Only admins can do this!", show_alert=True)
        return
    
    msg = bot.send_message(
        call.message.chat.id,
        f"✍️ Enter amount to add for user {user_id}:"
    )
    bot.register_next_step_handler(msg, process_deposit_amount, user_id, call.message)
    bot.answer_callback_query(call.id)

def process_deposit_amount(message, user_id, admin_msg):
    if message.text in SYSTEM_BUTTONS:
        handle_menu_redirect(message)
        return
    
    try:
        amount = float(message.text.strip())
        if amount <= 0:
            raise ValueError
        
        conn = sqlite3.connect("era_panel.db")
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET add_money_balance = add_money_balance + ? WHERE user_id = ?", (amount, user_id))
        cursor.execute("UPDATE users SET withdrawal_balance = withdrawal_balance + ? WHERE user_id = ?", (amount, user_id))
        conn.commit()
        conn.close()
        
        try:
            bot.edit_message_text(
                admin_msg.text + f"\n\n✅ APPROVED - ₹{amount:.2f} added",
                admin_msg.chat.id,
                admin_msg.message_id,
                reply_markup=None
            )
        except:
            pass
        
        try:
            bot.send_message(
                user_id,
                f"✅ Your deposit of ₹{amount:.2f} has been approved!"
            )
        except:
            pass
        
        bot.send_message(
            message.chat.id,
            f"✅ ₹{amount:.2f} added to user {user_id}!",
            reply_markup=admin_menu_keyboard()
        )
        
    except ValueError:
        msg = bot.send_message(
            message.chat.id,
            "❌ Galat amount! Kripya sahi amount enter karein:"
        )
        bot.register_next_step_handler(msg, process_deposit_amount, user_id, admin_msg)

@bot.callback_query_handler(func=lambda call: call.data.startswith("reject_deposit_"))
def reject_deposit(call):
    user_id = int(call.data.replace("reject_deposit_", ""))
    
    if call.from_user.id not in ADMIN_IDS:
        bot.answer_callback_query(call.id, "❌ Only admins can do this!", show_alert=True)
        return
    
    bot.answer_callback_query(call.id, "❌ Deposit rejected!")
    
    try:
        bot.edit_message_text(
            call.message.text + "\n\n❌ REJECTED",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=None
        )
    except:
        pass
    
    try:
        bot.send_message(
            user_id,
            "❌ Your deposit request has been rejected!"
        )
    except:
        pass

@bot.callback_query_handler(func=lambda call: call.data == "submit_screenshot")
def submit_screenshot(call):
    bot.answer_callback_query(call.id)
    msg = bot.send_message(
        call.message.chat.id,
        "📤 Please send your payment screenshot:"
    )
    bot.register_next_step_handler(msg, process_screenshot)

def process_screenshot(message):
    if message.text in SYSTEM_BUTTONS:
        handle_menu_redirect(message)
        return
    
    if not message.photo:
        msg = bot.send_message(message.chat.id, "❌ Please send a photo as screenshot:")
        bot.register_next_step_handler(msg, process_screenshot)
        return
    
    user_id = message.from_user.id
    file_id = message.photo[-1].file_id
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("✅ Approve", callback_data=f"approve_deposit_{user_id}"),
        types.InlineKeyboardButton("❌ Reject", callback_data=f"reject_deposit_{user_id}")
    )
    
    for admin_id in ADMIN_IDS:
        try:
            bot.send_photo(
                admin_id,
                file_id,
                caption=f"📩 Deposit Request\n\n👤 User: {message.from_user.full_name}\n🆔 ID: {user_id}",
                reply_markup=markup
            )
        except:
            pass
    
    bot.send_message(
        message.chat.id,
        "✅ Screenshot received! Admin will verify and add balance soon.",
        reply_markup=main_menu_keyboard(user_id)
    )

# =========================
# COUPON FUNCTIONS
# =========================

@bot.message_handler(func=lambda msg: msg.text == "➕ Create New Coupon")
def ask_coupon_code(message):
    if message.from_user.id not in ADMIN_IDS:
        bot.send_message(message.chat.id, "❌ Access Denied!")
        return
    
    msg = bot.send_message(message.chat.id, "✍️ Coupon Code enter karein (e.g. SAVE50):", reply_markup=coupon_menu_keyboard())
    bot.register_next_step_handler(msg, process_coupon_code)

def process_coupon_code(message):
    if message.text in SYSTEM_BUTTONS:
        handle_menu_redirect(message)
        return
    
    coupon_code = message.text.upper().strip()
    if not coupon_code or len(coupon_code) < 3:
        msg = bot.send_message(message.chat.id, "❌ Code at least 3 characters long hona chahiye! Try again:")
        bot.register_next_step_handler(msg, process_coupon_code)
        return
    
    msg = bot.send_message(message.chat.id, f"✍️ Discount amount enter karein for '{coupon_code}' (e.g. 50 for ₹50 OFF):")
    bot.register_next_step_handler(msg, process_discount_amount, coupon_code)

def process_discount_amount(message, coupon_code):
    if message.text in SYSTEM_BUTTONS:
        handle_menu_redirect(message)
        return
    
    try:
        discount = int(message.text.strip())
        if discount <= 0:
            raise ValueError
    except ValueError:
        msg = bot.send_message(message.chat.id, "❌ Galat format! Kripya sirf number enter karein (e.g. 50 for ₹50 OFF):")
        bot.register_next_step_handler(msg, process_discount_amount, coupon_code)
        return
    
    msg = bot.send_message(message.chat.id, f"✍️ Is coupon ko kitne log use kar sakte hain? (Max Uses, default 100):")
    bot.register_next_step_handler(msg, process_max_uses, coupon_code, discount)

def process_max_uses(message, coupon_code, discount):
    if message.text in SYSTEM_BUTTONS:
        handle_menu_redirect(message)
        return
    
    try:
        max_uses = int(message.text.strip())
        if max_uses <= 0:
            raise ValueError
    except ValueError:
        max_uses = 100
    
    coupon_id, success = create_coupon(coupon_code, discount, max_uses)
    
    if success:
        bot.send_message(
            message.chat.id,
            f"✅ Coupon Created Successfully!\n\n"
            f"🎫 Code: {coupon_code}\n"
            f"💰 Discount: ₹{discount} OFF\n"
            f"👥 Max Uses: {max_uses}\n"
            f"🆔 Coupon ID: {coupon_id}",
            reply_markup=coupon_menu_keyboard()
        )
    else:
        bot.send_message(
            message.chat.id,
            f"❌ Coupon '{coupon_code}' already exists!",
            reply_markup=coupon_menu_keyboard()
        )

@bot.message_handler(func=lambda msg: msg.text == "📋 List All Coupons")
def list_all_coupons(message):
    if message.from_user.id not in ADMIN_IDS:
        bot.send_message(message.chat.id, "❌ Access Denied!")
        return
    
    coupons = get_all_coupons()
    
    if not coupons:
        bot.send_message(message.chat.id, "📭 No coupons available!", reply_markup=coupon_menu_keyboard())
        return
    
    response = "📋 ALL COUPONS\n\n"
    response += f"📊 Total Coupons: {len(coupons)}\n"
    response += "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    for row in coupons:
        cid, code, discount, max_uses, times_used, status = row
        status_emoji = "✅ Active" if status == "Active" else "❌ Inactive"
        remaining = max_uses - times_used
        
        response += f"🆔 ID: {cid}\n"
        response += f"🎫 Code: {code}\n"
        response += f"💰 Discount: ₹{discount} OFF\n"
        response += f"👥 Usage: {times_used}/{max_uses} used ({remaining} remaining)\n"
        response += f"📊 Status: {status_emoji}\n"
        response += "━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
    
    bot.send_message(message.chat.id, response, reply_markup=coupon_menu_keyboard())

@bot.message_handler(func=lambda msg: msg.text == "🗑 Delete Coupon by ID")
def ask_delete_id(message):
    if message.from_user.id not in ADMIN_IDS:
        bot.send_message(message.chat.id, "❌ Access Denied!")
        return
    
    coupons = get_all_coupons()
    if not coupons:
        bot.send_message(message.chat.id, "📭 No coupons to delete!", reply_markup=coupon_menu_keyboard())
        return
    
    msg_text = "📋 Available Coupon IDs:\n\n"
    for row in coupons:
        msg_text += f"🆔 ID: {row[0]} → {row[1]} (₹{row[2]} OFF)\n"
    
    msg_text += "\n✍️ Delete karne ke liye Coupon ID enter karein:"
    
    msg = bot.send_message(message.chat.id, msg_text, reply_markup=coupon_menu_keyboard())
    bot.register_next_step_handler(msg, process_delete_coupon)

def process_delete_coupon(message):
    if message.text in SYSTEM_BUTTONS:
        handle_menu_redirect(message)
        return
    
    try:
        coupon_id = int(message.text.strip())
    except ValueError:
        msg = bot.send_message(message.chat.id, "❌ Galat ID! Kripya sirf number enter karein:")
        bot.register_next_step_handler(msg, process_delete_coupon)
        return
    
    if delete_coupon_by_id(coupon_id):
        bot.send_message(message.chat.id, f"✅ Coupon ID {coupon_id} deleted successfully!", reply_markup=coupon_menu_keyboard())
    else:
        bot.send_message(message.chat.id, f"❌ Coupon ID {coupon_id} not found!", reply_markup=coupon_menu_keyboard())

@bot.message_handler(func=lambda msg: msg.text == "🔄 Toggle Active/Inactive")
def ask_toggle_code(message):
    if message.from_user.id not in ADMIN_IDS:
        bot.send_message(message.chat.id, "❌ Access Denied!")
        return
    
    msg = bot.send_message(message.chat.id, "✍️ Toggle karne ke liye Coupon CODE enter karein:", reply_markup=coupon_menu_keyboard())
    bot.register_next_step_handler(msg, process_toggle_coupon)

def process_toggle_coupon(message):
    if message.text in SYSTEM_BUTTONS:
        handle_menu_redirect(message)
        return
    
    code = message.text.upper().strip()
    new_status = toggle_coupon_status(code)
    
    if new_status is None:
        bot.send_message(message.chat.id, f"❌ Coupon '{code}' not found!", reply_markup=coupon_menu_keyboard())
    else:
        status_emoji = "✅ ACTIVE" if new_status == "Active" else "❌ INACTIVE"
        bot.send_message(message.chat.id, f"🔄 Coupon '{code}' ab {status_emoji} hai!", reply_markup=coupon_menu_keyboard())

# =========================
# COUPON IN BUY PANEL
# =========================

@bot.callback_query_handler(func=lambda call: call.data == "show_coupon_input")
def show_coupon_input(call):
    bot.answer_callback_query(call.id)
    msg = bot.send_message(call.message.chat.id, "🎫 Enter Your Coupon Code\n\nPlease enter your coupon code:")
    bot.register_next_step_handler(msg, process_coupon_in_buy, call.message)

def process_coupon_in_buy(message, original_message):
    if message.text in SYSTEM_BUTTONS:
        handle_menu_redirect(message)
        return
    
    coupon_code = message.text.upper().strip()
    user_id = message.from_user.id
    
    coupon = get_coupon_by_code(coupon_code)
    
    if not coupon:
        bot.send_message(message.chat.id, "❌ Invalid coupon code!")
        return
    
    cid, code, discount, max_uses, times_used, status = coupon
    
    if status != "Active":
        bot.send_message(message.chat.id, "❌ Yeh coupon EXPIRED ho chuka hai!")
        return
    
    if times_used >= max_uses:
        bot.send_message(message.chat.id, "❌ Yeh coupon already fully used ho chuka hai!")
        return
    
    if is_coupon_used_by_user(user_id, coupon_code):
        bot.send_message(message.chat.id, "❌ Aap already is coupon ko use kar chuke hain!")
        return
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    
    products = get_all_products()
    
    for pid, name, price, apk, web, qr in products:
        discounted_price = max(0, price - discount)
        markup.add(types.InlineKeyboardButton(
            f"🛒 {name} - ₹{price} → ₹{discounted_price}",
            callback_data=f"buy_with_coupon_{pid}_{coupon_code}"
        ))
    
    markup.add(types.InlineKeyboardButton("❌ Remove Coupon", callback_data="remove_coupon"))
    
    bot.send_message(
        message.chat.id,
        f"🎫 Coupon Applied: {coupon_code}\n"
        f"💰 ₹{discount} OFF Available!\n\n"
        f"🛒 Choose a plan to purchase:",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data == "remove_coupon")
def remove_coupon(call):
    bot.answer_callback_query(call.id, "Coupon removed!")
    bot.delete_message(call.message.chat.id, call.message.message_id)
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    products = get_all_products()
    
    for pid, name, price, apk, web, qr in products:
        markup.add(types.InlineKeyboardButton(f"🛒 {name} - ₹{price}", callback_data=f"buy_{pid}"))
    markup.add(types.InlineKeyboardButton("🎫 Apply Coupon", callback_data="show_coupon_input"))
    
    bot.send_message(call.message.chat.id, "🛒 BUY PANEL\n\nChoose a plan:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("buy_with_coupon_"))
def buy_with_coupon(call):
    user_id = call.from_user.id
    parts = call.data.split("_")
    pid = parts[3]
    coupon_code = parts[4]
    
    product = get_product_by_id(pid)
    coupon = get_coupon_by_code(coupon_code)
    
    if not product or not coupon:
        bot.answer_callback_query(call.id, "Error!", show_alert=True)
        return
    
    pid, name, price, apk, web, qr = product
    cid, code, discount, max_uses, times_used, status = coupon
    
    final_price = max(0, price - discount)
    add_money, withdrawal = get_user_balance(user_id)
    
    if add_money >= final_price:
        conn = sqlite3.connect("era_panel.db")
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET add_money_balance = add_money_balance - ? WHERE user_id = ?", (final_price, user_id))
        conn.commit()
        conn.close()
        
        mark_coupon_used(user_id, coupon_code)
        
        bot.answer_callback_query(call.id, "✅ Purchase successful!", show_alert=True)
        
        success_msg = f"🎉 Aapne {name} successfully buy kar liya hai!"
        success_msg += f"\n\n🎫 Coupon Used: {coupon_code}"
        success_msg += f"\n💰 You Saved: ₹{discount}"
        success_msg += f"\n💵 Final Price: ₹{final_price}"
        success_msg += f"\n\n📥 Your Links:\n🤖 APK Link: {apk}\n🌐 Web Link: {web}"
        
        if qr:
            bot.send_photo(call.message.chat.id, qr, caption=success_msg)
        else:
            bot.send_message(call.message.chat.id, success_msg)
    else:
        bot.answer_callback_query(call.id, "❌ Insufficient Balance!", show_alert=True)
        
        insufficient_msg = (
            f"❌ Insufficient Balance!\n\n"
            f"📦 Plan Name: {name}\n"
            f"💰 Price: ₹{final_price}\n"
            f"🎫 Coupon Applied: {coupon_code}\n"
            f"💳 Your Balance: ₹{add_money:.2f}\n\n"
            f"👇 Is plan ko active karne ke liye QR code par exact ₹{final_price} send karein:"
        )
        
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🎫 Apply Coupon Here", callback_data="show_coupon_input"))
        
        if qr:
            bot.send_photo(call.message.chat.id, qr, caption=insufficient_msg, reply_markup=markup)
        else:
            bot.send_message(call.message.chat.id, insufficient_msg, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("buy_"))
def buy_product(call):
    pid = call.data.replace("buy_", "")
    
    if pid == "no_product":
        bot.answer_callback_query(call.id, "No products available!", show_alert=True)
        return
    
    product = get_product_by_id(pid)
    
    if not product:
        bot.answer_callback_query(call.id, "Product not found!", show_alert=True)
        return
    
    pid, name, price, apk, web, qr = product
    user_id = call.from_user.id
    add_money, withdrawal = get_user_balance(user_id)
    
    if add_money >= price:
        conn = sqlite3.connect("era_panel.db")
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET add_money_balance = add_money_balance - ? WHERE user_id = ?", (price, user_id))
        conn.commit()
        conn.close()
        
        bot.answer_callback_query(call.id, "✅ Purchase successful!", show_alert=True)
        
        success_msg = f"🎉 Aapne {name} successfully buy kar liya hai!"
        success_msg += f"\n\n📥 Your Links:\n🤖 APK Link: {apk}\n🌐 Web Link: {web}"
        
        if qr:
            bot.send_photo(call.message.chat.id, qr, caption=success_msg)
        else:
            bot.send_message(call.message.chat.id, success_msg)
    else:
        bot.answer_callback_query(call.id, "❌ Insufficient Balance!", show_alert=True)
        
        insufficient_msg = (
            f"❌ Insufficient Balance!\n\n"
            f"📦 Plan Name: {name}\n"
            f"💰 Price: ₹{price}\n"
            f"💳 Your Balance: ₹{add_money:.2f}\n\n"
            f"👇 Is plan ko active karne ke liye QR code par exact ₹{price} send karein:"
        )
        
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🎫 Apply Coupon Here", callback_data="show_coupon_input"))
        
        if qr:
            bot.send_photo(call.message.chat.id, qr, caption=insufficient_msg, reply_markup=markup)
        else:
            bot.send_message(call.message.chat.id, insufficient_msg, reply_markup=markup)

# =========================
# REFERRAL REWARD - SET
# =========================

@bot.message_handler(func=lambda msg: msg.text == "👥 Per Refer Set")
def per_refer_set(message):
    if message.from_user.id not in ADMIN_IDS:
        bot.send_message(message.chat.id, "❌ Access Denied!")
        return
    
    rewards = get_all_refer_rewards()
    if rewards:
        text = "📋 EXISTING REWARDS\n\n"
        for rid, refer_count, reward_type, reward_value in rewards:
            text += f"🆔 ID: {rid} → {refer_count} referrals = {reward_type.upper()}\n"
        text += "\n✍️ New referral count enter karein (e.g. 5 for 5 referrals):"
    else:
        text = "✍️ Referral count enter karein (e.g. 5 for 5 referrals):"
    
    msg = bot.send_message(message.chat.id, text, reply_markup=admin_menu_keyboard())
    bot.register_next_step_handler(msg, process_refer_count)

def process_refer_count(message):
    if message.text in SYSTEM_BUTTONS:
        handle_menu_redirect(message)
        return
    
    try:
        refer_count = int(message.text.strip())
        if refer_count <= 0:
            raise ValueError
        
        existing = get_refer_reward_by_count(refer_count)
        if existing:
            bot.send_message(
                message.chat.id,
                f"❌ Reward for {refer_count} referrals already exists!",
                reply_markup=admin_menu_keyboard()
            )
            return
        
        msg = bot.send_message(
            message.chat.id,
            f"✍️ Reward type for {refer_count} referrals:\n\n"
            f"Type 'apk' - For APK file\n"
            f"Type 'panel' - For Panel Access\n\n"
            f"Enter reward type:",
            reply_markup=admin_menu_keyboard()
        )
        bot.register_next_step_handler(msg, process_reward_type, refer_count)
        
    except ValueError:
        msg = bot.send_message(
            message.chat.id,
            "❌ Galat format! Kripya number enter karein:"
        )
        bot.register_next_step_handler(msg, process_refer_count)

def process_reward_type(message, refer_count):
    if message.text in SYSTEM_BUTTONS:
        handle_menu_redirect(message)
        return
    
    reward_type = message.text.lower().strip()
    
    if reward_type not in ["apk", "panel"]:
        msg = bot.send_message(
            message.chat.id,
            "❌ Galat type! Select from: apk, panel"
        )
        bot.register_next_step_handler(msg, process_reward_type, refer_count)
        return
    
    if reward_type == "apk":
        msg = bot.send_message(
            message.chat.id,
            f"📤 Send APK file as reward for {refer_count} referrals:",
            reply_markup=admin_menu_keyboard()
        )
        bot.register_next_step_handler(msg, process_reward_file, refer_count, reward_type)
    else:
        msg = bot.send_message(
            message.chat.id,
            f"✍️ Enter Panel Link/Access Code for {refer_count} referrals:",
            reply_markup=admin_menu_keyboard()
        )
        bot.register_next_step_handler(msg, process_reward_value, refer_count, reward_type)

def process_reward_file(message, refer_count, reward_type):
    if message.text in SYSTEM_BUTTONS:
        handle_menu_redirect(message)
        return
    
    if not message.document:
        msg = bot.send_message(
            message.chat.id,
            "❌ Please send an APK file:"
        )
        bot.register_next_step_handler(msg, process_reward_file, refer_count, reward_type)
        return
    
    file_id = message.document.file_id
    
    reward_id, success = add_refer_reward(refer_count, reward_type, file_id)
    
    if success:
        bot.send_message(
            message.chat.id,
            f"✅ Referral reward set successfully!\n\n"
            f"📊 Refer Count: {refer_count}\n"
            f"📦 Reward Type: APK File\n"
            f"🆔 Reward ID: {reward_id}",
            reply_markup=admin_menu_keyboard()
        )
    else:
        bot.send_message(
            message.chat.id,
            f"❌ Reward for {refer_count} referrals already exists!",
            reply_markup=admin_menu_keyboard()
        )

def process_reward_value(message, refer_count, reward_type):
    if message.text in SYSTEM_BUTTONS:
        handle_menu_redirect(message)
        return
    
    reward_value = message.text.strip()
    
    if not reward_value:
        msg = bot.send_message(
            message.chat.id,
            "❌ Please enter a valid reward value:"
        )
        bot.register_next_step_handler(msg, process_reward_value, refer_count, reward_type)
        return
    
    reward_id, success = add_refer_reward(refer_count, reward_type, reward_value)
    
    if success:
        bot.send_message(
            message.chat.id,
            f"✅ Referral reward set successfully!\n\n"
            f"📊 Refer Count: {refer_count}\n"
            f"📦 Reward Type: Panel Access\n"
            f"🆔 Reward ID: {reward_id}\n"
            f"🔗 Panel Link: {reward_value}",
            reply_markup=admin_menu_keyboard()
        )
    else:
        bot.send_message(
            message.chat.id,
            f"❌ Reward for {refer_count} referrals already exists!",
            reply_markup=admin_menu_keyboard()
        )

# =========================
# REFERRAL REWARD - MANAGE
# =========================

@bot.message_handler(func=lambda msg: msg.text == "📂 Manage Saved Rewards")
def manage_saved_rewards(message):
    if message.from_user.id not in ADMIN_IDS:
        bot.send_message(message.chat.id, "❌ Access Denied!")
        return
    
    rewards = get_all_refer_rewards()
    
    if not rewards:
        bot.send_message(
            message.chat.id,
            "📭 No referral rewards set!",
            reply_markup=admin_menu_keyboard()
        )
        return
    
    text = "📂 SAVED REFERRAL REWARDS\n\n"
    for rid, refer_count, reward_type, reward_value in rewards:
        text += f"━━━━━━━━━━━━━━━━━━\n"
        text += f"🆔 ID: {rid}\n"
        text += f"📊 Refer Count: {refer_count}\n"
        text += f"📦 Type: {reward_type.upper()}\n"
        if reward_type == "apk":
            text += f"📎 APK File\n"
        else:
            text += f"🔗 Link: {reward_value[:50]}{'...' if len(reward_value) > 50 else ''}\n"
        text += f"━━━━━━━━━━━━━━━━━━\n\n"
    
    text += "\n🗑 Delete karne ke liye Reward ID enter karein:"
    
    msg = bot.send_message(message.chat.id, text, reply_markup=admin_menu_keyboard())
    bot.register_next_step_handler(msg, process_delete_reward)

def process_delete_reward(message):
    if message.text in SYSTEM_BUTTONS:
        handle_menu_redirect(message)
        return
    
    try:
        reward_id = int(message.text.strip())
        
        if delete_refer_reward(reward_id):
            bot.send_message(
                message.chat.id,
                f"✅ Reward ID {reward_id} deleted successfully!",
                reply_markup=admin_menu_keyboard()
            )
        else:
            bot.send_message(
                message.chat.id,
                f"❌ Reward ID {reward_id} not found!",
                reply_markup=admin_menu_keyboard()
            )
    except ValueError:
        msg = bot.send_message(
            message.chat.id,
            "❌ Galat ID! Kripya number enter karein:"
        )
        bot.register_next_step_handler(msg, process_delete_reward)

# =========================
# EDIT USER BALANCE
# =========================

@bot.message_handler(func=lambda msg: msg.text == "💰 Edit User Balance")
def edit_user_balance(message):
    if message.from_user.id not in ADMIN_IDS:
        bot.send_message(message.chat.id, "❌ Access Denied!")
        return
    
    msg = bot.send_message(
        message.chat.id,
        "✍️ User ID enter karein:",
        reply_markup=admin_menu_keyboard()
    )
    bot.register_next_step_handler(msg, process_edit_balance_user)

def process_edit_balance_user(message):
    if message.text in SYSTEM_BUTTONS:
        handle_menu_redirect(message)
        return
    
    try:
        user_id = int(message.text.strip())
        user = get_user_by_id(user_id)
        
        if not user:
            msg = bot.send_message(
                message.chat.id,
                "❌ User not found! Please enter valid ID:",
                reply_markup=admin_menu_keyboard()
            )
            bot.register_next_step_handler(msg, process_edit_balance_user)
            return
        
        uid, username, full_name, add_balance, withdraw_balance, referrals = user
        
        text = (
            f"👤 USER FOUND\n\n"
            f"🆔 User ID: {uid}\n"
            f"📛 Name: {full_name}\n"
            f"🔗 Username: @{username or 'N/A'}\n"
            f"👥 Referrals: {referrals}\n"
            f"💰 Current Add Money Balance: ₹{add_balance:.2f}\n"
            f"💸 Current Withdrawal Balance: ₹{withdraw_balance:.2f}\n\n"
            f"✍️ Enter amount with operation:\n"
            f"➕ Add: Type +50 to add ₹50\n"
            f"➖ Subtract: Type -30 to subtract ₹30\n"
            f"🔢 Set: Type 100 to set exact ₹100"
        )
        
        msg = bot.send_message(message.chat.id, text, reply_markup=admin_menu_keyboard())
        bot.register_next_step_handler(msg, process_edit_balance_amount, user_id, add_balance)
        
    except ValueError:
        msg = bot.send_message(
            message.chat.id,
            "❌ Galat ID! Kripya number enter karein:",
            reply_markup=admin_menu_keyboard()
        )
        bot.register_next_step_handler(msg, process_edit_balance_user)

def process_edit_balance_amount(message, user_id, current_balance):
    if message.text in SYSTEM_BUTTONS:
        handle_menu_redirect(message)
        return
    
    input_text = message.text.strip()
    new_balance = current_balance
    operation = "SET"
    
    try:
        if input_text.startswith("+"):
            amount = float(input_text[1:].strip())
            new_balance = current_balance + amount
            operation = f"ADDED +{amount}"
        elif input_text.startswith("-"):
            amount = float(input_text[1:].strip())
            new_balance = current_balance - amount
            operation = f"SUBTRACTED -{amount}"
        else:
            new_balance = float(input_text)
            operation = f"SET TO {new_balance}"
        
        if new_balance < 0:
            bot.send_message(
                message.chat.id,
                "❌ Balance 0 se kam nahi ho sakta!",
                reply_markup=admin_menu_keyboard()
            )
            msg = bot.send_message(
                message.chat.id,
                f"✍️ Current balance: ₹{current_balance:.2f}\n"
                f"Enter amount with + or - or exact number:",
                reply_markup=admin_menu_keyboard()
            )
            bot.register_next_step_handler(msg, process_edit_balance_amount, user_id, current_balance)
            return
        
        if update_user_balance(user_id, new_balance):
            user = get_user_by_id(user_id)
            text = (
                f"✅ Balance updated successfully!\n\n"
                f"🆔 User ID: {user_id}\n"
                f"📛 Name: {user[2]}\n"
                f"💰 Old Balance: ₹{current_balance:.2f}\n"
                f"💰 New Balance: ₹{new_balance:.2f}\n"
                f"📊 Operation: {operation}"
            )
            bot.send_message(message.chat.id, text, reply_markup=admin_menu_keyboard())
        else:
            bot.send_message(
                message.chat.id,
                "❌ Failed to update balance!",
                reply_markup=admin_menu_keyboard()
            )
            
    except ValueError:
        msg = bot.send_message(
            message.chat.id,
            "❌ Galat format! Use:\n"
            "➕ +50 - Add ₹50\n"
            "➖ -30 - Subtract ₹30\n"
            "🔢 100 - Set exact ₹100",
            reply_markup=admin_menu_keyboard()
        )
        bot.register_next_step_handler(msg, process_edit_balance_amount, user_id, current_balance)

# =========================
# SET PROJECT QR
# =========================

@bot.message_handler(func=lambda msg: msg.text == "🖼 Set Project QR")
def set_project_qr(message):
    if message.from_user.id not in ADMIN_IDS:
        bot.send_message(message.chat.id, "❌ Access Denied!")
        return
    
    products = get_all_products()
    
    if not products:
        bot.send_message(message.chat.id, "📭 No products available!", reply_markup=admin_menu_keyboard())
        return
    
    msg_text = "📋 **Select a product to set QR code:**\n\n"
    for pid, name, price, apk, web, qr in products:
        status = "✅" if qr else "❌"
        msg_text += f"🆔 ID: `{pid}` → {name} (₹{price}) - QR: {status}\n"
    
    msg_text += "\n✍️ Product ID enter karein (e.g. 1):"
    
    msg = bot.send_message(message.chat.id, msg_text, parse_mode="Markdown", reply_markup=admin_menu_keyboard())
    bot.register_next_step_handler(msg, process_project_qr_product)

def process_project_qr_product(message):
    if message.text in SYSTEM_BUTTONS:
        handle_menu_redirect(message)
        return
    
    try:
        product_id = int(message.text.strip())
        product = get_product_by_id(product_id)
        
        if not product:
            msg = bot.send_message(message.chat.id, "❌ Product ID not found!")
            bot.register_next_step_handler(msg, process_project_qr_product)
            return
        
        pid, name, price, apk, web, qr = product
        
        bot.send_message(
            message.chat.id,
            f"✅ Product selected: {name} (ID: {pid})\n\n"
            f"📸 Send a photo as QR code:",
            reply_markup=admin_menu_keyboard()
        )
        bot.register_next_step_handler(message, process_project_qr_photo, product_id)
        
    except ValueError:
        msg = bot.send_message(message.chat.id, "❌ Galat ID!")
        bot.register_next_step_handler(msg, process_project_qr_product)

def process_project_qr_photo(message, product_id):
    if message.text in SYSTEM_BUTTONS:
        handle_menu_redirect(message)
        return
    
    if not message.photo:
        msg = bot.send_message(message.chat.id, "❌ Please send a photo:")
        bot.register_next_step_handler(msg, process_project_qr_photo, product_id)
        return
    
    file_id = message.photo[-1].file_id
    update_product_qr(product_id, file_id)
    
    product = get_product_by_id(product_id)
    bot.send_message(
        message.chat.id,
        f"✅ QR code set successfully for {product[1]}!",
        reply_markup=admin_menu_keyboard()
    )

# =========================
# SET ADD MONEY QR
# =========================

@bot.message_handler(func=lambda msg: msg.text == "📸 Set Add Money QR")
def set_add_money_qr(message):
    if message.from_user.id not in ADMIN_IDS:
        bot.send_message(message.chat.id, "❌ Access Denied!")
        return
    
    msg = bot.send_message(
        message.chat.id,
        "📸 Send a photo as Add Money QR code:",
        reply_markup=admin_menu_keyboard()
    )
    bot.register_next_step_handler(msg, process_add_money_qr)

def process_add_money_qr(message):
    if message.text in SYSTEM_BUTTONS:
        handle_menu_redirect(message)
        return
    
    if not message.photo:
        msg = bot.send_message(message.chat.id, "❌ Please send a photo:")
        bot.register_next_step_handler(msg, process_add_money_qr)
        return
    
    file_id = message.photo[-1].file_id
    save_setting("add_money_qr", file_id)
    
    bot.send_message(
        message.chat.id,
        "✅ Add Money QR code saved successfully!",
        reply_markup=admin_menu_keyboard()
    )

# =========================
# ADD PRODUCT
# =========================

@bot.message_handler(func=lambda msg: msg.text == "🛒 Add Product")
def add_product(message):
    if message.from_user.id not in ADMIN_IDS:
        bot.send_message(message.chat.id, "❌ Access Denied!")
        return
    msg = bot.send_message(message.chat.id, "✍️ Product Name | Price | APK Link | Web Link\n\nExample: VIP Panel | 99 | https://t.me/link | https://t.me/link", reply_markup=admin_menu_keyboard())
    bot.register_next_step_handler(msg, process_add_product)

def process_add_product(message):
    if message.text in SYSTEM_BUTTONS:
        handle_menu_redirect(message)
        return
    
    parts = [p.strip() for p in message.text.split("|")]
    if len(parts) < 3:
        msg = bot.send_message(message.chat.id, "❌ Format error! Use: Name | Price | APK Link | Web Link")
        bot.register_next_step_handler(msg, process_add_product)
        return
    
    name = parts[0]
    try:
        price = float(parts[1])
    except ValueError:
        msg = bot.send_message(message.chat.id, "❌ Price must be a number!")
        bot.register_next_step_handler(msg, process_add_product)
        return
    
    apk_link = parts[2]
    web_link = parts[3] if len(parts) > 3 else "https://t.me/R1898114"
    
    conn = sqlite3.connect("era_panel.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO products (name, price, apk_link, web_link) VALUES (?, ?, ?, ?)",
        (name, price, apk_link, web_link)
    )
    conn.commit()
    conn.close()
    
    bot.send_message(message.chat.id, f"✅ Product '{name}' added successfully!", reply_markup=admin_menu_keyboard())

# =========================
# REMOVE PRODUCT
# =========================

@bot.message_handler(func=lambda msg: msg.text == "🗑 Remove Product")
def remove_product(message):
    if message.from_user.id not in ADMIN_IDS:
        bot.send_message(message.chat.id, "❌ Access Denied!")
        return
    
    products = get_all_products()
    if not products:
        bot.send_message(message.chat.id, "📭 No products to remove!", reply_markup=admin_menu_keyboard())
        return
    
    msg_text = "📋 Available Products:\n\n"
    for pid, name, price, apk, web, qr in products:
        msg_text += f"🆔 ID: {pid} → {name} (₹{price})\n"
    
    msg_text += "\n✍️ Remove karne ke liye Product ID enter karein:"
    
    msg = bot.send_message(message.chat.id, msg_text, reply_markup=admin_menu_keyboard())
    bot.register_next_step_handler(msg, process_remove_product)

def process_remove_product(message):
    if message.text in SYSTEM_BUTTONS:
        handle_menu_redirect(message)
        return
    
    try:
        pid = int(message.text.strip())
        conn = sqlite3.connect("era_panel.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM products WHERE id = ?", (pid,))
        deleted = cursor.rowcount
        conn.commit()
        conn.close()
        
        if deleted > 0:
            bot.send_message(message.chat.id, f"✅ Product ID {pid} removed successfully!", reply_markup=admin_menu_keyboard())
        else:
            bot.send_message(message.chat.id, f"❌ Product ID {pid} not found!", reply_markup=admin_menu_keyboard())
    except ValueError:
        msg = bot.send_message(message.chat.id, "❌ Galat ID!")
        bot.register_next_step_handler(msg, process_remove_product)

# =========================
# EDIT PRODUCT PRICE
# =========================

@bot.message_handler(func=lambda msg: msg.text == "💰 Edit Product Price")
def edit_product_price(message):
    if message.from_user.id not in ADMIN_IDS:
        bot.send_message(message.chat.id, "❌ Access Denied!")
        return
    
    products = get_all_products()
    if not products:
        bot.send_message(message.chat.id, "📭 No products available!", reply_markup=admin_menu_keyboard())
        return
    
    msg_text = "📋 Available Products:\n\n"
    for pid, name, price, apk, web, qr in products:
        msg_text += f"🆔 ID: {pid} → {name} (₹{price})\n"
    
    msg_text += "\n✍️ Edit karne ke liye Product ID enter karein:"
    
    msg = bot.send_message(message.chat.id, msg_text, reply_markup=admin_menu_keyboard())
    bot.register_next_step_handler(msg, process_edit_product_price)

def process_edit_product_price(message):
    if message.text in SYSTEM_BUTTONS:
        handle_menu_redirect(message)
        return
    
    try:
        pid = int(message.text.strip())
        product = get_product_by_id(pid)
        if not product:
            msg = bot.send_message(message.chat.id, "❌ Product ID not found!")
            bot.register_next_step_handler(msg, process_edit_product_price)
            return
        
        msg = bot.send_message(message.chat.id, f"✍️ Naya price enter karein for {product[1]} (Current: ₹{product[2]}):")
        bot.register_next_step_handler(msg, process_edit_product_price_final, pid)
        
    except ValueError:
        msg = bot.send_message(message.chat.id, "❌ Galat ID!")
        bot.register_next_step_handler(msg, process_edit_product_price)

def process_edit_product_price_final(message, pid):
    if message.text in SYSTEM_BUTTONS:
        handle_menu_redirect(message)
        return
    
    try:
        new_price = float(message.text.strip())
        if new_price <= 0:
            raise ValueError
        
        conn = sqlite3.connect("era_panel.db")
        cursor = conn.cursor()
        cursor.execute("UPDATE products SET price = ? WHERE id = ?", (new_price, pid))
        conn.commit()
        conn.close()
        
        bot.send_message(message.chat.id, f"✅ Product price updated successfully!", reply_markup=admin_menu_keyboard())
        
    except ValueError:
        msg = bot.send_message(message.chat.id, "❌ Galat price!")
        bot.register_next_step_handler(msg, process_edit_product_price_final, pid)

# =========================
# TOTAL USERS
# =========================

@bot.message_handler(func=lambda msg: msg.text == "👥 Total Users")
def total_users(message):
    if message.from_user.id not in ADMIN_IDS:
        bot.send_message(message.chat.id, "❌ Access Denied!")
        return
    conn = sqlite3.connect("era_panel.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    conn.close()
    bot.send_message(message.chat.id, f"👥 Total Registered Users: {count}", reply_markup=admin_menu_keyboard())

# =========================
# BROADCAST
# =========================

@bot.message_handler(func=lambda msg: msg.text == "📢 Broadcast")
def broadcast_start(message):
    if message.from_user.id not in ADMIN_IDS:
        bot.send_message(message.chat.id, "❌ Access Denied!")
        return
    
    msg = bot.send_message(
        message.chat.id,
        "📢 Broadcast message bhejein (Text, Photo, Video, Document, Audio sab chalega!):",
        reply_markup=admin_menu_keyboard()
    )
    bot.register_next_step_handler(msg, process_broadcast)

def process_broadcast(message):
    if message.text in SYSTEM_BUTTONS:
        handle_menu_redirect(message)
        return
    
    conn = sqlite3.connect("era_panel.db")
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users")
    users = cursor.fetchall()
    conn.close()
    
    sent = 0
    failed = 0
    
    progress_msg = bot.send_message(message.chat.id, f"📢 Broadcasting to {len(users)} users...")
    
    for user in users:
        try:
            user_id = user[0]
            
            if message.text:
                bot.send_message(user_id, f"📢 {message.text}")
            elif message.photo:
                bot.send_photo(user_id, message.photo[-1].file_id, caption=f"📢 {message.caption or ''}")
            elif message.document:
                bot.send_document(user_id, message.document.file_id, caption=f"📢 {message.caption or ''}")
            elif message.video:
                bot.send_video(user_id, message.video.file_id, caption=f"📢 {message.caption or ''}")
            elif message.audio:
                bot.send_audio(user_id, message.audio.file_id, caption=f"📢 {message.caption or ''}")
            elif message.voice:
                bot.send_voice(user_id, message.voice.file_id, caption=f"📢 {message.caption or ''}")
            elif message.animation:
                bot.send_animation(user_id, message.animation.file_id, caption=f"📢 {message.caption or ''}")
            elif message.sticker:
                bot.send_sticker(user_id, message.sticker.file_id)
            else:
                bot.forward_message(user_id, message.chat.id, message.message_id)
            
            sent += 1
        except Exception as e:
            failed += 1
        
        if sent % 10 == 0:
            import time
            time.sleep(0.1)
    
    bot.edit_message_text(
        f"✅ Broadcast Completed!\n\n"
        f"👥 Total Users: {len(users)}\n"
        f"✅ Sent: {sent}\n"
        f"❌ Failed: {failed}",
        progress_msg.chat.id,
        progress_msg.message_id,
        reply_markup=admin_menu_keyboard()
    )

# =========================
# STATE LOCK / MENU REDIRECT
# =========================

def handle_menu_redirect(message):
    text = message.text
    
    if text == "⚙️ Admin Panel" or text == "⬅️ Back to Admin":
        admin_panel(message)
    elif text == "🎫 Manage Coupons":
        manage_coupons(message)
    elif text == "⬅️ Main Menu":
        main_menu(message)
    elif text == "👥 Total Users":
        total_users(message)
    elif text == "📋 Withdraw Requests":
        withdraw_requests(message)
    elif text == "📂 Manage Saved Rewards":
        manage_saved_rewards(message)
    elif text == "👥 Per Refer Set":
        per_refer_set(message)
    elif text == "💰 Edit User Balance":
        edit_user_balance(message)
    else:
        user_id = message.from_user.id
        bot.send_message(message.chat.id, "🔙 Returning to main menu...", reply_markup=main_menu_keyboard(user_id))

# =========================
# BOT START
# =========================

print("🚀 ERA x PANEL - Complete Bot Starting...")
print("✅ SQLite Database Connected")
print("✅ Coupon System Active")
print("✅ Withdraw System Active (Min: ₹100)")
print("✅ Referral Reward System Active")
print("✅ Edit User Balance - + Add / - Subtract")
print("✅ Broadcast - Text, Photo, Video, Document, Audio")
print("✅ Force Channel Join - @eraXarmy, @eraXearning")
print("✅ Extra Link System - COMPLETELY REMOVED")
print("=" * 40)

if __name__ == "__main__":
    try:
        print("🤖 Polling started...")
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
    except Exception as e:
        print(f"⚠️ Error: {e}")
        print("🔄 Retrying in 5 seconds...")
