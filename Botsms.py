import os
import json
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

# ==================== CẤU HÌNH HỆ THỐNG ====================
BOT_TOKEN = "8830710724:AAGpzsBkui7kJCBGqYFkMu8Brbm-R49lCJs"
ADMIN_ID = 8985238179
CONTACT_ADMIN = "@Miutea88"

# Thông tin ngân hàng nạp tiền
BANK_NAME = "MB BANK"
ACCOUNT_NO = "2105200999999"
ACCOUNT_NAME = "KHONG QUOC BAO"

# Dữ liệu sản phẩm & Giá tiền
PRODUCTS = {
    "cert": {
        "name": "Mua Chứng Chỉ 🔓",
        "price": 185000,
        "desc": "Mô tả: Chứng chỉ giúp bạn cài các Tool/App/Chạy app crack\nGiá: 185,000đ",
        "guide": "Hướng dẫn sử dụng:\nB1: Cài app (app tôi đã gửi đây)\nB2: Cài chứng chỉ các app\nB3: Sử dụng"
    },
    "api": {
        "name": "Mua API/TOKEN 🎁",
        "price": 167800,
        "desc": "Mô tả: API/TOKEN là các api giúp app/tool hoạt động trơn chu mượt mà không delay.\nGiá: 167,800đ",
        "guide": "Tool lấy API: https://www.google.com/aclk?sa=L&ai=DChsSEwjxsYqG99-WAxWVwzwCHYZSHgMYACICCAEQABoCc2Y&co=1&gclid=Cj0KCQjw5P7UBhDaARIsAOSlS1PWcFfP_l8gZXR9TohR2mtj1MhbCQ68ukBXsCNKQeUfiE_yJ4ztp74aArvFEALw_wcB&cid=CAAS0gHkaPDYGW6-_BUJctpg8iv6rSziE3lexiA8ovrTXRFfaNlqmMkeJQNXHFd61yYsZVv9uP5_W_JN_ZD3bolFSipi5jE8jZQsKYF3B_GWjorn-07vBEpsS9ob08QWvnyH0hjF3LnYpPjZu_CEhwBoa87In1i3X2fW_5Ji1TrmabfAgYquq7iEYQj5xXyYgNfWDxOLTUZ-dNJjvcR2O0ZMpgxAOVHwKAtb93DVzYC_Mg06332uxSv-uEtYCxR6zsoECwqYQg4o7_xLTboSBh6cZ3A_JKo&cce=1&sig=AOD64_2sJT3FpUItT334PkcGPjOtSiHiZQ&q&adurl&ved=2ahUKEwjg-4WG99-WAxWGkOEIHUdNPKgQ0Qx6BAgMEAE"
    },
    "app": {
        "name": "Mua App 💻",
        "price": 123980,
        "desc": "Mô tả: Mua các app giúp bạn chạy tool, app, source code cực nhanh\nGiá: 123,980đ",
        "guide": "Các App giúp cài Source Code/Tool:\nScarlet: https://usescarlet.com/\nEsign: https://esign-ios.app/\nKsign: https://ksign-ios.com/\nFeather: https://github.com/claration/Feather"
    },
    "code": {
        "name": "Mua Code 👨‍💻",
        "price": 399999,
        "desc": "Mô tả: Các loại code và admin có nhận code theo yêu cầu\nGiá: 399,999đ",
        "guide": f"Liên hệ admin: {CONTACT_ADMIN} để được hỗ trợ\nhttps://t.me/miutea88"
    }
}

# ==================== QUẢN LÝ DỮ LIỆU NGƯỜI DÙNG ====================
DB_FILE = "users_db.json"

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_db(db):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=4)

# Lưu trạng thái tạm thời cho user (ví dụ: đang nhập số tiền nạp)
user_states = {}

# ==================== HÀM XỬ LÝ LỆNH /START ====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id_str = str(user.id)
    db = load_db()
    
    is_new = False
    if user_id_str not in db:
        is_new = True
        db[user_id_str] = {
            "first_name": user.first_name or "",
            "username": user.username or "Không có",
            "balance": 0,
            "join_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        save_db(db)
        
        # Thông báo cho admin khi có khách mới
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
        f"• `/naptien <số tiền>` - Nạp tiền nhanh (Ví dụ: `/naptien 50000`)\n"
        f"Hoặc sử dụng các nút menu bên dưới để thao tác nhanh!"
    )
    
    keyboard = [
        [InlineKeyboardButton("📂 Menu", callback_data="menu"),
         InlineKeyboardButton("💳 Nạp Tiền", callback_data="deposit")],
        [InlineKeyboardButton("📞 Liên hệ Admin", url=f"https://t.me/Miutea88")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode="Markdown")

# ==================== MENU CHÍNH ====================
async def show_menu(query):
    keyboard = [
        [InlineKeyboardButton("Mua Chứng Chỉ 🔓", callback_data="buy_cert")],
        [InlineKeyboardButton("Mua API/TOKEN 🎁", callback_data="buy_api")],
        [InlineKeyboardButton("Mua App 💻", callback_data="buy_app")],
        [InlineKeyboardButton("Mua Code 👨‍💻", callback_data="buy_code")],
        [InlineKeyboardButton("« Quay lại", callback_data="back_home")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("📂 *HỆ THỐNG DỊCH VỤ - VUI LÒNG CHỌN MỤC:*", reply_markup=reply_markup, parse_mode="Markdown")

# ==================== XỬ LÝ MUA HÀNG ====================
async def handle_purchase(query, product_key, user_id):
    product = PRODUCTS[product_key]
    db = load_db()
    user_id_str = str(user_id)
    
    if user_id_str not in db:
        db[user_id_str] = {"balance": 0}
        
    current_balance = db[user_id_str].get("balance", 0)
    price = product["price"]
    
    # Kiểm tra số dư
    if current_balance < price:
        text = (
            f"❌ *Số dư của bạn không đủ để mua sản phẩm này!*\n\n"
            f"• Sản phẩm: *{product['name']}*\n"
            f"• Giá tiền: `{price:,}đ`\n"
            f"• Số dư hiện tại: `{current_balance:,}đ`\n"
            f"• Còn thiếu: `{price - current_balance:,}đ`\n\n"
            f"Vui lòng bấm nút nạp tiền bên dưới để tiếp tục!"
        )
        keyboard = [
            [InlineKeyboardButton("💳 Nạp Tiền Ngay", callback_data="deposit")],
            [InlineKeyboardButton("« Quay lại Menu", callback_data="menu")]
        ]
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
        return

    # Trừ tiền tự động
    db[user_id_str]["balance"] -= price
    save_db(db)
    new_balance = db[user_id_str]["balance"]
    
    success_text = (
        f"✅ *GIAO DỊCH THÀNH CÔNG!*\n\n"
        f"• Sản phẩm: *{product['name']}*\n"
        f"• Đã trừ: `{price:,}đ`\n"
        f"• Số dư còn lại: `{new_balance:,}đ`\n\n"
        f"📜 *{product['desc']}*\n\n"
        f"📖 *Hướng dẫn nhận sản phẩm:*\n{product['guide']}"
    )
    keyboard = [[InlineKeyboardButton("« Quay lại Menu", callback_data="menu")]]
    await query.edit_message_text(success_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

# ==================== NẠP TIỀN & QR CODE ====================
async def request_deposit_input(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id, amount):
    if amount <= 0:
        await update.message.reply_text("❌ Số tiền nạp không hợp lệ.")
        return
    
    content = f"NAP{user_id}"
    qr_url = f"https://img.vietqr.io/image/MB-{ACCOUNT_NO}-compact2.png?amount={amount}&addInfo={content}&accountName={urllib_quote(ACCOUNT_NAME)}"
    
    text = (
        f"💳 *THÔNG TIN CHUYỂN KHOẢN NẠP TIỀN*\n\n"
        f"• Ngân hàng: *{BANK_NAME}*\n"
        f"• Số tài khoản: `{ACCOUNT_NO}`\n"
        f"• Chủ tài khoản: *{ACCOUNT_NAME}*\n"
        f"• Số tiền: `{amount:,}đ`\n"
        f"• Nội dung chuyển khoản (BẮT BUỘC): `{content}`\n\n"
        f"⚠️ *Lưu ý:* Vui lòng chuyển đúng nội dung để hệ thống tự động nhận diện hoặc chờ Admin duyệt."
    )
    
    keyboard = [
        [InlineKeyboardButton("✅ Tôi đã chuyển khoản", callback_data=f"sent_money_{amount}")],
        [InlineKeyboardButton("« Quay lại Menu", callback_data="menu")]
    ]
    
    # Gửi QR code
    if update.message:
        await update.message.reply_photo(photo=qr_url, caption=text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
    elif update.callback_query:
        await update.callback_query.message.reply_photo(photo=qr_url, caption=text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

import urllib.parse
def urllib_quote(text):
    return urllib.parse.quote(text)

# ==================== XỬ LÝ CALLBACK & TIN NHẮN ====================
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id
    
    if data == "menu":
        await show_menu(query)
    elif data == "back_home":
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
        await query.edit_message_text(
            "💳 Vui lòng nhập số tiền bạn muốn nạp (Ví dụ: `50000`):",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("« Quay lại", callback_data="menu")]]),
            parse_mode="Markdown"
        )
    elif data.startswith("buy_"):
        product_key = data.split("_")[1]
        await handle_purchase(query, product_key, user_id)
    elif data.startswith("sent_money_"):
        amount = data.split("_")[2]
        user = query.from_user
        user_states.pop(user.id, None)
        
        await query.edit_message_caption(
            caption=query.message.caption + "\n\n⏳ *Đã gửi yêu cầu xác nhận tới Admin. Vui lòng chờ duyệt!*",
            parse_mode="Markdown"
        )
        
        # Báo cáo cho Admin kèm nút Duyệt / Từ chối
        admin_text = (
            f"🔔 *CÓ YÊU CẦU NẠP TIỀN MỚI*\n\n"
            f"• Khách hàng: {user.full_name}\n"
            f"• Username: @{user.username or 'Không có'}\n"
            f"• ID khách: `{user.id}`\n"
            f"• Số tiền nạp: `{int(amount):,}đ`\n"
            f"• Nội dung: `NAP{user.id}`"
        )
        admin_keyboard = [
            [
                InlineKeyboardButton("✅ Duyệt", callback_data=f"approve_{user.id}_{amount}"),
                InlineKeyboardButton("❌ Từ chối", callback_data=f"reject_{user.id}_{amount}")
            ]
        ]
        await context.bot.send_message(chat_id=ADMIN_ID, text=admin_text, reply_markup=InlineKeyboardMarkup(admin_keyboard), parse_mode="Markdown")
        
    elif data.startswith("approve_") or data.startswith("reject_"):
        if query.from_user.id != ADMIN_ID:
            await query.answer("Bạn không có quyền thao tác này!", show_alert=True)
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
            
            await query.edit_message_text(f"✅ Đã DUYỆT nạp `{amount:,}đ` cho user `{target_user_id}` thành công.")
            try:
                await context.bot.send_message(
                    chat_id=target_user_id,
                    text=f"✅ Nạp tiền thành công! Tài khoản của bạn đã được cộng thêm `{amount:,}đ`.\nSố dư hiện tại: `{db[target_str]['balance']:,}đ`",
                    parse_mode="Markdown"
                )
            except:
                pass
        else:
            await query.edit_message_text(f"❌ Đã TỪ CHỐI giao dịch nạp tiền của user `{target_user_id}`.")
            try:
                await context.bot.send_message(
                    chat_id=target_user_id,
                    text="❌ Yêu cầu nạp tiền của bạn đã bị từ chối bởi Admin. Vui lòng liên hệ @Miutea88 nếu có nhầm lẫn."
                )
            except:
                pass

async def handle_message_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    text = update.message.text.strip()
    
    if user_states.get(user_id) == "waiting_deposit_amount":
        if text.isdigit():
            amount = int(text)
            user_states.pop(user_id, None)
            await request_deposit_input(update, context, user_id, amount)
        else:
            await update.message.reply_text("❌ Số tiền không hợp lệ. Vui lòng nhập một số nguyên (Ví dụ: `50000`):")

# ==================== LỆNH ADMIN ====================
async def cmd_addtien(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    args = context.args
    if len(args) < 2:
        await update.message.reply_text("Sai cú pháp! Dùng: `/addtien <id> <số_tiền>`", parse_mode="Markdown")
        return
    try:
        target_id = str(args[0])
        amount = int(args[1])
        db = load_db()
        if target_id not in db:
            db[target_id] = {"balance": 0}
        db[target_id]["balance"] += amount
        save_db(db)
        await update.message.reply_text(f"✅ Đã cộng `{amount:,}đ` cho user `{target_id}`. Số dư mới: `{db[target_id]['balance']:,}đ`", parse_mode="Markdown")
        try:
            await context.bot.send_message(chat_id=int(target_id), text=f"🎁 Tài khoản của bạn vừa được Admin cộng thêm `{amount:,}đ`!", parse_mode="Markdown")
        except:
            pass
    except Exception as e:
        await update.message.reply_text(f"Lỗi: {e}")

async def cmd_trutien(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    args = context.args
    if len(args) < 2:
        await update.message.reply_text("Sai cú pháp! Dùng: `/trutien <id> <số_tiền>`", parse_mode="Markdown")
        return
    try:
        target_id = str(args[0])
        amount = int(args[1])
        db = load_db()
        if target_id not in db:
            db[target_id] = {"balance": 0}
        db[target_id]["balance"] = max(0, db[target_id]["balance"] - amount)
        save_db(db)
        await update.message.reply_text(f"✅ Đã trừ `{amount:,}đ` của user `{target_id}`. Số dư mới: `{db[target_id]['balance']:,}đ`", parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"Lỗi: {e}")

async def cmd_thongbao(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    content = " ".join(context.args)
    if not content:
        await update.message.reply_text("Vui lòng nhập nội dung thông báo! Dùng: `/thongbao <nội dung>`", parse_mode="Markdown")
        return
    
    db = load_db()
    success_count = 0
    for uid in db.keys():
        try:
            await context.bot.send_message(chat_id=int(uid), text=f"📢 *THÔNG BÁO TỪ HỆ THỐNG*\n\n{content}", parse_mode="Markdown")
            success_count += 1
        except:
            pass
    await update.message.reply_text(f"✅ Đã gửi thông báo tới `{success_count}` người dùng thành công.")

async def cmd_naptien(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args or not args[0].isdigit():
        await update.message.reply_text("Vui lòng dùng cú pháp: `/naptien <số_tiền>` (Ví dụ: `/naptien 50000`)", parse_mode="Markdown")
        return
    amount = int(args[0])
    await request_deposit_input(update, context, update.effective_user.id, amount)

# ==================== MAIN CONFIG ====================
async def post_init(application: Application):
    # Cài đặt menu gợi ý các lệnh cho user ngay cạnh khung chat
    commands = [
        BotCommand("start", "Khởi động bot và xem thông tin"),
        BotCommand("naptien", "Nạp tiền nhanh (VD: /naptien 50000)")
    ]
    await application.bot.set_my_commands(commands)

def main():
    application = Application.builder().token(BOT_TOKEN).post_init(post_init).build()
    
    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("naptien", cmd_naptien))
    application.add_handler(CommandHandler("addtien", cmd_addtien))
    application.add_handler(CommandHandler("trutien", cmd_trutien))
    application.add_handler(CommandHandler("thongbao", cmd_thongbao))
    
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message_text))
    
    print("Bot Shop đang chạy...")
    application.run_polling()

if __name__ == "__main__":
    main()
