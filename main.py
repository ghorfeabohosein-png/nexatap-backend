from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import sqlite3
import os
import requests

app = FastAPI()

# --- تنظیمات ربات تلگرام ---
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME", "@YourChannelUsername")

DB_FILE = "database.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            username TEXT,
            score INTEGER DEFAULT 0,
            wallet TEXT DEFAULT '',
            is_member INTEGER DEFAULT 0,
            referrals_count INTEGER DEFAULT 0,
            referred_by TEXT DEFAULT '',
            last_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

class ScoreUpdate(BaseModel):
    user_id: str
    username: str
    score: int

class WalletUpdate(BaseModel):
    user_id: str
    wallet: str

@app.post("/api/save_score")
async def save_score(data: ScoreUpdate):
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO users (user_id, username, score) 
            VALUES (?, ?, ?)
            ON CONFLICT(user_id) 
            DO UPDATE SET score = MAX(users.score, ?), username = ?
        ''', (data.user_id, data.username, data.score, data.score, data.username))
        conn.commit()
        conn.close()
        return {"status": "success", "message": "موجودی با موفقیت ذخیره شد!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/save_wallet")
async def save_wallet(data: WalletUpdate):
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET wallet = ? WHERE user_id = ?', (data.wallet, data.user_id))
        conn.commit()
        conn.close()
        return {"status": "success", "message": "کیف پول با موفقیت ثبت شد!"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/get_user/{user_id}")
async def get_user(user_id: str):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT score, wallet, is_member, referrals_count FROM users WHERE user_id = ?', (user_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            "user_id": user_id, 
            "score": row[0], 
            "wallet": row[1] or "", 
            "is_member": row[2], 
            "referrals_count": row[3]
        }
    else:
        return {"user_id": user_id, "score": 0, "wallet": "", "is_member": 0, "referrals_count": 0}

# --- وب‌هوک تلگرام برای مدیریت دکمه‌ها و دستور /start ---
@app.post("/webhook")
async def telegram_webhook(req: Request):
    try:
        data = await req.json()
        print("WEBHOOK RECEIVED:", data)
        
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
        print("Telegram API Response:", response.text)
    except Exception as e:
        print(f"Error sending telegram message: {e}")

# --- رابط کاربری مینی‌اپ (HTML/JS) ---
@app.get("/", response_class=HTMLResponse)
async def read_root():
    html_content = """
    <!DOCTYPE html>
    <html lang="fa" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
        <title>NexaTap - نکست‌تپ</title>
        <script src="https://telegram.org/js/telegram-web-app.js"></script>
        <style>
            * { box-sizing: border-box; user-select: none; -webkit-user-select: none; }
            body, html {
                margin: 0; padding: 0; width: 100%; height: 100%;
                overflow: hidden; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: #0c0c1e;
            }
            .game-container {
                position: relative; width: 100%; height: 100%;
                background-image: url('https://raw.githubusercontent.com/ghorfeabohosein-png/nexatap-backend/main/character.jpg');
                background-size: cover; background-position: center;
                display: flex; flex-direction: column; justify-content: space-between; align-items: center;
            }
            .overlay { position: absolute; top: 0; left: 0; width: 100%; height: 100%; background: rgba(12, 12, 30, 0.3); z-index: 1; }
            .header-top { position: absolute; top: 15px; right: 15px; z-index: 10; display: flex; gap: 10px; }
            .score-box, .menu-btn {
                background: rgba(20, 20, 40, 0.85);
                border: 2px solid #00ffcc; border-radius: 15px;
                padding: 6px 14px; display: flex; align-items: center; gap: 8px;
                box-shadow: 0 0 15px rgba(0, 255, 204, 0.3); backdrop-filter: blur(8px);
                color: #00ffcc; font-weight: bold; font-size: 14px; cursor: pointer;
            }
            .score-value { font-size: 22px; font-weight: 900; color: #ffd700; text-shadow: 0 0 10px rgba(255, 215, 0, 0.7); }
            .user-box {
                position: absolute; top: 15px; left: 15px; z-index: 10;
                background: rgba(20, 20, 40, 0.85); border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 12px; padding: 6px 12px; font-size: 12px; color: #00ffcc; backdrop-filter: blur(8px);
            }
            .main-content {
                position: absolute; bottom: 25px; width: 100%;
                display: flex; justify-content: space-around; align-items: center;
                z-index: 10; padding: 0 15px;
            }
            .save-btn, .wallet-btn {
                background: linear-gradient(135deg, #2ecc71, #27ae60);
                border: 2px solid #2ecc71; border-radius: 14px;
                padding: 12px 14px; font-size: 13px; font-weight: bold; color: white;
                cursor: pointer; box-shadow: 0 6px 20px rgba(46, 204, 113, 0.4); transition: transform 0.1s ease;
            }
            .wallet-btn { background: linear-gradient(135deg, #3498db, #2980b9); border-color: #3498db; box-shadow: 0 6px 20px rgba(52, 152, 219, 0.4); }
            .save-btn:active, .wallet-btn:active, .tap-btn:active { transform: scale(0.92); }
            
            .tap-btn {
                width: 120px; height: 120px;
                background: linear-gradient(135deg, #ffe600, #ff9900);
                border: 4px solid #ffffff; border-radius: 50%;
                font-size: 24px; font-weight: 900; color: #1a1a1a; cursor: pointer;
                box-shadow: 0 0 30px rgba(255, 230, 0, 0.8);
                display: flex; align-items: center; justify-content: center;
            }
            .floating-number {
                position: absolute; font-size: 24px; font-weight: 900; color: #ffd700;
                text-shadow: 0 0 10px rgba(255, 215, 0, 0.9); pointer-events: none; z-index: 20;
                animation: floatUp 0.6s ease-out forwards;
            }
            @keyframes floatUp {
                0% { opacity: 1; transform: translateY(0) scale(1); }
                100% { opacity: 0; transform: translateY(-60px) scale(1.3); }
            }
            .modal {
                display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%;
                background: rgba(0,0,0,0.8); z-index: 100; justify-content: center; align-items: center;
            }
            .modal-content {
                background: #141428; border: 2px solid #00ffcc; border-radius: 20px;
                padding: 20px; width: 85%; max-width: 320px; text-align: center; color: white;
                box-shadow: 0 0 25px rgba(0,255,204,0.4);
            }
            .modal-content input {
                width: 100%; padding: 10px; margin: 15px 0; border-radius: 10px;
                border: 1px solid #00ffcc; background: #0c0c1e; color: white; text-align: center;
            }
            .modal-content button {
                background: #00ffcc; color: #0c0c1e; border: none; padding: 10px 20px;
                font-weight: bold; border-radius: 10px; cursor: pointer; margin: 5px;
            }
        </style>
    </head>
    <body>

        <div class="game-container">
            <div class="overlay"></div>
            <div class="user-box" id="userInfo">بارگذاری...</div>

            <div class="header-top">
                <div class="menu-btn" id="refMenuBtn">👥 دعوت‌ها</div>
                <div class="score-box">
                    <span>🪙</span>
                    <div class="score-value" id="score">0</div>
                </div>
            </div>

            <div class="main-content">
                <button class="wallet-btn" id="walletBtn">💳 کیف پول</button>
                <button class="tap-btn" id="tapButton">TAP!</button>
                <button class="save-btn" id="saveBtn">💾 ذخیره</button>
            </div>
        </div>

        <div class="modal" id="walletModal">
            <div class="modal-content">
                <h3>اتصال کیف پول Ton</h3>
                <p style="font-size: 12px; color: #aaa;">آدرس ولت خود را وارد کنید:</p>
                <input type="text" id="walletInput" placeholder="UQAP... یا Tonkeeper...">
                <button id="saveWalletBtn">ثبت ولت</button>
                <button onclick="closeModals()" style="background: #e74c3c; color: white;">بستن</button>
            </div>
        </div>

        <div class="modal" id="refModal">
            <div class="modal-content">
                <h3>سیستم دعوت (رفرال)</h3>
                <p style="font-size: 13px; margin: 10px 0;">برای هر دعوت دوستان: <b style="color: #ffd700;">+5 امتیاز</b> (تا سقف 100 امتیاز)</p>
                <p id="refStats" style="font-size: 14px; color: #00ffcc; margin: 15px 0;"></p>
                <button id="copyRefBtn">کپی لینک دعوت</button>
                <button onclick="closeModals()" style="background: #e74c3c; color: white;">بستن</button>
            </div>
        </div>

        <script>
            const tg = window.Telegram.WebApp;
            tg.expand();

            let score = 0;
            let userId = "nexatap_user_default";
            let userName = "بازیکن";
            let userWallet = "";
            let refCount = 0;

            if (tg.initDataUnsafe && tg.initDataUnsafe.user && tg.initDataUnsafe.user.id) {
                userId = String(tg.initDataUnsafe.user.id);
                userName = tg.initDataUnsafe.user.first_name || "بازیکن";
            } else {
                let savedId = localStorage.getItem('nexatap_local_id');
                if (!savedId) {
                    savedId = 'user_' + Math.floor(Math.random() * 1000000);
                    localStorage.setItem('nexatap_local_id', savedId);
                }
                userId = savedId;
                userName = "کاربر تستی";
            }

            document.getElementById('userInfo').innerText = `سلام، ${userName}`;
            const scoreElement = document.getElementById('score');
            const tapButton = document.getElementById('tapButton');
            const saveBtn = document.getElementById('saveBtn');
            const walletBtn = document.getElementById('walletBtn');
            const refMenuBtn = document.getElementById('refMenuBtn');

            fetch(`/api/get_user/${userId}`)
                .then(res => res.json())
                .then(data => {
                    score = data.score;
                    scoreElement.innerText = score;
                    userWallet = data.wallet;
                    refCount = data.referrals_count;
                    if (userWallet) { walletBtn.innerText = "✅ ولت متصل"; }
                })
                .catch(err => {
                    let localScore = localStorage.getItem('nexatap_score_' + userId);
                    if (localScore) { score = parseInt(localScore); scoreElement.innerText = score; }
                });

            tapButton.addEventListener('click', (e) => {
                score += 1;
                scoreElement.innerText = score;
                localStorage.setItem('nexatap_score_' + userId, score);

                if (tg.HapticFeedback) tg.HapticFeedback.impactOccurred('medium');

                const rect = tapButton.getBoundingClientRect();
                const x = e.clientX || (rect.left + rect.width / 2);
                const y = e.clientY || rect.top;

                const floatText = document.createElement('div');
                floatText.className = 'floating-number';
                floatText.innerText = '+1';
                floatText.style.left = `${x - 10}px`;
                floatText.style.top = `${y - 30}px`;
                document.body.appendChild(floatText);
                setTimeout(() => floatText.remove(), 600);
            });

            saveBtn.addEventListener('click', () => {
                if (tg.HapticFeedback) tg.HapticFeedback.notificationOccurred('success');
                fetch('/api/save_score', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ user_id: userId, username: userName, score: score })
                }).then(res => res.json()).then(data => alert("موجودی با موفقیت ذخیره شد! ✅"));
            });

            walletBtn.addEventListener('click', () => {
                document.getElementById('walletInput').value = userWallet;
                document.getElementById('walletModal').style.display = 'flex';
            });

            refMenuBtn.addEventListener('click', () => {
                document.getElementById('refStats').innerText = `تعداد دوستان دعوت‌شده: ${refCount} نفر`;
                document.getElementById('refModal').style.display = 'flex';
            });

            function closeModals() {
                document.querySelectorAll('.modal').forEach(m => m.style.display = 'none');
            }

            document.getElementById('saveWalletBtn').addEventListener('click', () => {
                const wInput = document.getElementById('walletInput').value.trim();
                if(!wInput) return alert("لطفا آدرس معتبر وارد کنید");
                
                fetch('/api/save_wallet', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ user_id: userId, wallet: wInput })
                }).then(res => res.json()).then(data => {
                    userWallet = wInput;
                    walletBtn.innerText = "✅ ولت متصل";
                    closeModals();
                    alert("کیف پول ثبت شد!");
                });
            });

            document.getElementById('copyRefBtn').addEventListener('click', () => {
                const refLink = `https://t.me/NexaTap_Bot?start=ref_${userId}`;
                navigator.clipboard.writeText(refLink);
                alert("لینک دعوت کپی شد! برای دوستانتان بفرستید.");
            });
        </script>
    </body>
    </html>
    """
    return html_content

@app.get("/health")
async def health_check():
    return {"status": "online", "project": "NexaTap ($NXTP)", "database": "SQLite Active"}
