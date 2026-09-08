import os
import json
import http.server
import socketserver
import threading
import urllib.parse
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# ==================== WEB SERVER MINI CHO RENDER ====================
PORT = int(os.environ.get("PORT", 10000))

class HealthCheckHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is active and running 24/7!")

def run_web_server():
    with socketserver.TCPServer(("", PORT), HealthCheckHandler) as httpd:
        httpd.serve_forever()

threading.Thread(target=run_web_server, daemon=True).start()

# ==================== CẤU HÌNH HỆ THỐNG ====================
BOT_TOKEN = "8830710724:AAGpzsBkui7kJCBGqYFkMu8Brbm-R49lCJs"
ADMIN_ID = 8985238179
CONTACT_ADMIN = "@Miutea88"

BANK_NAME = "MB BANK"
ACCOUNT_NO = "2105200999999"
ACCOUNT_NAME = "KHONG QUOC BAO"

PRODUCTS = {
    "cert": {
        "name": "Mua Chứng Chỉ 🔓",
        "price": 185000,
        "desc": "Mô tả: Chứng chỉ giúp bạn cài các Tool/App/Chạy app crack\nGiá: 185,000đ",
        "guide": "Hướng dẫn sử dụng:\nB1: Cài app\nB2: Cài chứng chỉ các app\nB3: Sử dụng"
    },
    "api": {
        "name": "Mua API/TOKEN 🎁",
        "price": 167800,
        "desc": "Mô tả: API/TOKEN giúp app/tool hoạt động trơn chu không delay.\nGiá: 167,800đ",
        "guide": "Tool lấy API: https://www.google.com/aclk?sa=L&ai=DChsSEwjxsYqG99-WAxWVwzwCHYZSHgMYACICCAEQABoCc2Y&co=1&gclid=Cj0KCQjw5P7UBhDaARIsAOSlS1PWcFfP_l8gZXR9TohR2mtj1MhbCQ68ukBXsCNKQeUfiE_yJ4ztp74aArvFEALw_wcB&cid=CAAS0gHkaPDYGW6-_BUJctpg8iv6rSziE3lexiA8ovrTXRFfaNlqmMkeJQNXHFd61yYsZVv9uP5_W_JN_ZD3bolFSipi5jE8jZQsKYF3B_GWjorn-07vBEpsS9ob08QWvnyH0hjF3LnYpPjZu_CEhwBoa87In1i3X2fW_5Ji1TrmabfAgYquq7iEYQj5xXyYgNfWDxOLTUZ-dNJjvcR2O0ZMpgxAOVHwKAtb93DVzYC_Mg06332uxSv-uEtYCxR6zsoECwqYQg4o7_xLTboSBh6cZ3A_JKo&cce=1&sig=AOD64_2sJT3FpUItT334PkcGPjOtSiHiZQ&q&adurl&ved=2ahUKEwjg-4WG99-WAxWGkOEIHUdNPKgQ0Qx6BAgMEAE"
    },
    "app": {
        "name": "Mua App 💻",
        "price": 123980,
        "desc": "Mô tả: Mua các app giúp bạn chạy tool, app cực nhanh\nGiá: 123,980đ",
        "guide": "Các App giúp cài Source Code/Tool:\nScarlet: https://usescarlet.com/\nEsign: https://esign-ios.app/\nKsign: https://ksign-ios.com/\nFeather: https://github.com/claration/Feather"
    },
    "code": {
        "name": "Mua Code 👨‍💻",
        "price": 399999,
        "desc": "Mô tả: Các loại code và admin có nhận code theo yêu cầu\nGiá: 399,999đ",
        "guide": f"Liên hệ admin: {CONTACT_ADMIN} để được hỗ trợ\nhttps://t.me/miutea88"
    }
}

DB_FILE = "users_db.json"

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_db(db):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=4)

user_states = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id_str = str(user.id)
    db = load_db()
    
    if user_id_str not in db:
        db[user_id_str] = {
            "first_name": user.first_name or "",
            "username": user.username or "Không có",
            "balance": 0,
            "join_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        save_db(db)
        try:
            msg_admin = (
                f"👤 *KHÁCH HÀNG MỚI THAM GIA*\n"
                f"• Tên Telegram: {user.full_name}\n"
                f"• Username: @{user.username or 'Không có'}\n"
                f"• ID khách: `{user.id}`\n"
                f"• Số dư: `0đ`\n"
                f"• Ngày tham gia: {db[user_id_str]['join_date']}"
            )
            await context.bot.send_message(chat_id=ADMIN_ID, text=msg_admin, parse_mode="Markdown")
        except Exception as e:
            print(f"Lỗi gửi thông báo cho admin: {e}")

    user_data = db[user_id_str]
    welcome_text = (
        f"👋 Chào mừng *{user.full_name}* tới với hệ thống!\n\n"
        f"📋 *Thông tin tài khoản của bạn:*\n"
        f"• Tên Telegram: {user.full_name}\n"
        f"• Username: @{user_data['username']}\n"
        f"• ID khách: `{user.id}`\n"
        f"• Số dư: `{user_data['balance']:,}đ`\n"
        f"• Ngày tham gia: {user_data['join_date']}\n\n"
        f"📌 *Hướng dẫn sử dụng lệnh:*\n"
        f"• `/start` - Khởi động lại bot và xem thông tin\n"
        f"• `/naptien <số tiền>` - Nạp tiền nhanh (Ví dụ: `/naptien 50000`)"
    )
    
    keyboard = [
        [InlineKeyboardButton("📂 Menu", callback_data="menu"),
         InlineKeyboardButton("💳 Nạp Tiền", callback_data="deposit")],
        [InlineKeyboardButton("📞 Liên hệ Admin", url=f"https://t.me/Miutea88")]
    ]
    await update.message.reply_text(welcome_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def show_menu(query):
    keyboard = [
        [InlineKeyboardButton("Mua Chứng Chỉ 🔓", callback_data="buy_cert")],
        [InlineKeyboardButton("Mua API/TOKEN 🎁", callback_data="buy_api")],
        [InlineKeyboardButton("Mua App 💻", callback_data="buy_app")],
        [InlineKeyboardButton("Mua Code 👨‍💻", callback_data="buy_code")],
        [InlineKeyboardButton("« Quay lại", callback_data="back_home")]
    ]
    await query.edit_message_text("📂 *HỆ THỐNG DỊCH VỤ - VUI LÒNG CHỌN MỤC:*", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def handle_purchase(query, product_key, user_id):
    product = PRODUCTS[product_key]
    db = load_db()
    user_id_str = str(user_id)
    
    if user_id_str not in db:
        db[user_id_str] = {"balance": 0}
        
    current_balance = db[user_id_str].get("balance", 0)
    price = product["price"]
    
    if current_balance < price:
        text = (
            f"❌ *Số dư của bạn không đủ để mua sản phẩm này!*\n\n"
            f"• Sản phẩm: *{product['name']}*\n"
            f"• Giá: `{price:,}đ` | Số dư: `{current_balance:,}đ`\n"
            f"• Còn thiếu: `{price - current_balance:,}đ`"
        )
        keyboard = [
            [InlineKeyboardButton("💳 Nạp Tiền Ngay", callback_data="deposit")],
            [InlineKeyboardButton("« Quay lại Menu", callback_data="menu")]
        ]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        return

    db[user_id_str]["balance"] -= price
    save_db(db)
    new_balance = db[user_id_str]["balance"]
    
    success_text = (
        f"✅ *GIAO DỊCH THÀNH CÔNG!*\n\n"
        f"• Sản phẩm: *{product['name']}*\n"
        f"• Đã trừ: `{price:,}đ` | Số dư còn lại: `{new_balance:,}đ`\n\n"
        f"📜 *{product['desc']}*\n\n"
        f"📖 *Hướng dẫn:*\n{product['guide']}"
    )
    await query.edit_message_text(success_text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("« Quay lại Menu", callback_data="menu")]]), parse_mode="Markdown")

async def request_deposit_input(update, context, user_id, amount):
    if amount <= 0:
        return
    content = f"NAP{user_id}"
    qr_url = f"https://img.vietqr.io/image/MB-{ACCOUNT_NO}-compact2.png?amount={amount}&addInfo={content}&accountName={urllib.parse.quote(ACCOUNT_NAME)}"
    
    text = (
        f"💳 *THÔNG TIN CHUYỂN KHOẢN NẠP TIỀN*\n\n"
        f"• Ngân hàng: *{BANK_NAME}* | STK: `{ACCOUNT_NO}`\n"
        f"• Chủ TK: *{ACCOUNT_NAME}*\n"
        f"• Số tiền: `{amount:,}đ`\n"
        f"• Nội dung: `{content}`"
    )
    keyboard = [
        [InlineKeyboardButton("✅ Tôi đã chuyển khoản", callback_data=f"sent_money_{amount}")],
        [InlineKeyboardButton("« Quay lại Menu", callback_data="menu")]
    ]
    
    if update.message:
        await update.message.reply_photo(photo=qr_url, caption=text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    elif update.callback_query:
        await update.callback_query.message.reply_photo(photo=qr_url, caption=text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id
    
    if data == "menu":
        user_states.pop(user_id, None)
        await show_menu(query)
    elif data == "back_home":
        user_states.pop(user_id, None)
        user = query.from_user
        db = load_db()
        bal = db.get(str(user.id), {}).get("balance", 0)
        text = f"🤖 Chào mừng trở lại, {user.full_name}!\n• Số dư: `{bal:,}đ`"
        keyboard = [
            [InlineKeyboardButton("📂 Menu", callback_data="menu"),
             InlineKeyboardButton("💳 Nạp Tiền", callback_data="deposit")],
            [InlineKeyboardButton("📞 Liên hệ Admin", url=f"https://t.me/Miutea88")]
        ]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    elif data == "deposit":
        user_states[user_id] = "waiting_deposit_amount"
        await context.bot.send_message(
            chat_id=user_id,
            text="💳 Vui lòng nhập số tiền cần nạp (Ví dụ: `50000`):",
            parse_mode="Markdown"
        )
    elif data.startswith("buy_"):
        await handle_purchase(query, data.split("_")[1], user_id)
    elif data.startswith("sent_money_"):
        amount = data.split("_")[2]
        user = query.from_user
        user_states.pop(user.id, None)
        try:
            await query.edit_message_caption(caption=query.message.caption + "\n\n⏳ *Đã gửi yêu cầu xác nhận tới Admin!*", parse_mode="Markdown")
        except:
            await query.message.reply_text("⏳ *Đã gửi yêu cầu xác nhận tới Admin!*", parse_mode="Markdown")
        
        admin_text = (
            f"🔔 *CÓ YÊU CẦU NẠP TIỀN MỚI*\n\n"
            f"• Khách: {user.full_name} (@{user.username or 'None'})\n"
            f"• ID: `{user.id}` | Số tiền: `{int(amount):,}đ`\n"
            f"• Nội dung: `NAP{user.id}`"
        )
        admin_keyboard = [[
            InlineKeyboardButton("✅ Duyệt", callback_data=f"approve_{user.id}_{amount}"),
            InlineKeyboardButton("❌ Từ chối", callback_data=f"reject_{user.id}_{amount}")
        ]]
        await context.bot.send_message(chat_id=ADMIN_ID, text=admin_text, reply_markup=InlineKeyboardMarkup(admin_keyboard), parse_mode="Markdown")
        
    elif data.startswith("approve_") or data.startswith("reject_"):
        if query.from_user.id != ADMIN_ID:
            return
        parts = data.split("_")
        action, target_user_id, amount = parts[0], int(parts[1]), int(parts[2])
        db = load_db()
        target_str = str(target_user_id)
        
        if action == "approve":
            if target_str not in db:
                db[target_str] = {"balance": 0}
            db[target_str]["balance"] += amount
            save_db(db)
            await query.edit_message_text(f"✅ Đã DUYỆT `{amount:,}đ` cho `{target_user_id}`.")
            try:
                await context.bot.send_message(chat_id=target_user_id, text=f"✅ Nạp tiền thành công! Cộng thêm `{amount:,}đ` vào tài khoản.", parse_mode="Markdown")
            except:
                pass
        else:
            await query.edit_message_text(f"❌ Đã TỪ CHỐI nạp tiền của `{target_user_id}`.")

async def handle_message_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()
    
    clean_text = text.replace(".", "").replace(",", "").replace("đ", "").replace("VND", "").strip()
    
    if user_states.get(user_id) == "waiting_deposit_amount" or clean_text.isdigit():
        if clean_text.isdigit():
            amount = int(clean_text)
            if amount >= 1000:
                user_states.pop(user_id, None)
                await request_deposit_input(update, context, user_id, amount)
                return
        
        if user_states.get(user_id) == "waiting_deposit_amount":
            await update.message.reply_text("❌ Số tiền không hợp lệ. Vui lòng nhập số nguyên lớn hơn 1,000 (Ví dụ: `50000`):", parse_mode="Markdown")

async def cmd_naptien(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args or not args[0].replace(".", "").replace(",", "").isdigit():
        user_states[update.effective_user.id] = "waiting_deposit_amount"
        await update.message.reply_text("💳 Vui lòng nhập số tiền bạn muốn nạp (Ví dụ: `50000`):", parse_mode="Markdown")
        return
    
    amount = int(args[0].replace(".", "").replace(",", ""))
    if amount >= 1000:
        await request_deposit_input(update, context, update.effective_user.id, amount)
    else:
        await update.message.reply_text("❌ Số tiền nạp tối thiểu là 1,000đ.")

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("naptien", cmd_naptien))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message_text))
    
    print("Bot Shop đang chạy...")
    application.run_polling()

if __name__ == "__main__":
    main()
