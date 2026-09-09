# --- وب‌هوک تلگرام برای مدیریت دکمه‌ها و دستور /start ---
@app.post("/webhook")
async def telegram_webhook(req: Request):
    try:
        data = await req.json()
        print("WEBHOOK RECEIVED:", data) # این خط کمک می‌کند در لاگ‌های رندر ببینیم درخواست آمده یا نه
        
        if "message" in data:
            message = data["message"]
            chat_id = message["chat"]["id"]
            user = message.get("from", {})
            user_id = str(user.get("id"))
            username = user.get("username", "user")
            first_name = user.get("first_name", "بازیکن")
            language_code = user.get("language_code", "en")
            text = message.get("text", "")

            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            
            cursor.execute('SELECT user_id, referrals_count FROM users WHERE user_id = ?', (user_id,))
            existing_user = cursor.fetchone()

            if not existing_user:
                if text.startswith("/start ref_"):
                    ref_id = text.split("ref_")[1]
                    if ref_id != user_id:
                        cursor.execute('SELECT score, referrals_count FROM users WHERE user_id = ?', (ref_id,))
                        referrer = cursor.fetchone()
                        if referrer:
                            ref_score, ref_count = referrer
                            if ref_count < 20: 
                                cursor.execute('UPDATE users SET score = score + 5, referrals_count = referrals_count + 1 WHERE user_id = ?', (ref_id,))
                
                cursor.execute('INSERT OR IGNORE INTO users (user_id, username, score) VALUES (?, ?, 0)', (user_id, username))
                conn.commit()

            conn.close()

            if language_code.startswith("fa"):
                welcome_text = f"سلام {first_name} عزیز! 🎮 به بازی نکست‌تپ خوش آمدید.\nبرای شروع تپ کنید، کیف پول خود را متصل کنید و سکه جایزه بگیرید!"
                btn_play = "🚀 شروع بازی (مینی‌اپ)"
                btn_wallet = "💳 کیف پول من"
                btn_channel = "📢 عضویت در کانال"
                btn_ref = "👥 لینک دعوت (رفرال)"
            else:
                welcome_text = f"Hello {first_name}! 🎮 Welcome to NexaTap.\nTap to earn, connect your wallet, and invite friends!"
                btn_play = "🚀 Start Game (Mini App)"
                btn_wallet = "💳 My Wallet"
                btn_channel = "📢 Join Channel"
                btn_ref = "👥 Referral Link"

            keyboard = {
                "inline_keyboard": [
                    [{"text": btn_play, "web_app": {"url": "https://nexatap-backend.onrender.com/"}}],
                    [{"text": btn_wallet, "callback_data": "check_wallet"}, {"text": btn_channel, "url": f"https://t.me/{CHANNEL_USERNAME.replace('@', '')}"}],
                    [{"text": btn_ref, "callback_data": "get_ref_link"}]
                ]
            }

            send_telegram_message(chat_id, welcome_text, keyboard)

        elif "callback_query" in data:
            query = data["callback_query"]
            chat_id = query["message"]["chat"]["id"]
            user_id = str(query["from"]["id"])
            data_action = query["data"]

            if data_action == "check_wallet":
                conn = sqlite3.connect(DB_FILE)
                cursor = conn.cursor()
                cursor.execute('SELECT wallet FROM users WHERE user_id = ?', (user_id,))
                row = cursor.fetchone()
                conn.close()
                w = row[0] if row and row[0] else "هنوز ثبت نشده است."
                send_telegram_message(chat_id, f"💳 وضعیت کیف پول شما:\n{w}\n\nبرای تغییر یا ثبت ولت، وارد مینی‌اپ شوید.")

            elif data_action == "get_ref_link":
                ref_link = f"https://t.me/NexaTap_Bot?start=ref_{user_id}"
                # حذف parse_mode برای جلوگیری از ارور کاراکترهای خاص در لینک
                send_telegram_message(chat_id, f"👥 لینک دعوت اختصاصی شما:\n{ref_link}\n\nبا ارسال این لینک به دوستانتان، به ازای هر نفر ۵ امتیاز دریافت کنید!", parse_mode=None)

    except Exception as e:
        print("Webhook Error:", e)

    return {"status": "ok"}

def send_telegram_message(chat_id, text, reply_markup=None, parse_mode="Markdown"):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    if parse_mode:
        payload["parse_mode"] = parse_mode
    if reply_markup:
        payload["reply_markup"] = reply_markup
    try:
        response = requests.post(url, json=payload)
        print("Telegram API Response:", response.text) # برای بررسی خط احتمالی از سمت تلگرام
    except Exception as e:
        print(f"Error sending telegram message: {e}")
