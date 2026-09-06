from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

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
            * {
                box-sizing: border-box;
                user-select: none;
                -webkit-user-select: none;
            }
            body, html {
                margin: 0;
                padding: 0;
                width: 100%;
                height: 100%;
                overflow: hidden;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: #0c0c1e;
            }
            /* پس‌زمینه متصل به لینک مستقیم گیت‌هاب شما */
            .game-container {
                position: relative;
                width: 100%;
                height: 100%;
                background-image: url('https://raw.githubusercontent.com/ghorfeabohosein-png/nexatap-backend/main/character.jpg');
                background-size: cover;
                background-position: center;
                display: flex;
                flex-direction: column;
                justify-content: space-between;
                align-items: center;
            }
            
            /* لایه تاریک‌کننده ملایم */
            .overlay {
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(12, 12, 30, 0.25);
                z-index: 1;
            }

            /* امتیاز در بالا سمت راست */
            .header-top {
                position: absolute;
                top: 20px;
                right: 20px;
                z-index: 10;
            }
            .score-box {
                background: rgba(20, 20, 40, 0.85);
                border: 2px solid #00ffcc;
                border-radius: 20px;
                padding: 8px 18px;
                display: flex;
                align-items: center;
                gap: 10px;
                box-shadow: 0 0 20px rgba(0, 255, 204, 0.4);
                backdrop-filter: blur(8px);
            }
            .score-value {
                font-size: 26px;
                font-weight: 900;
                color: #ffd700;
                text-shadow: 0 0 12px rgba(255, 215, 0, 0.7);
            }

            /* خوش‌آمدگویی بالا سمت چپ */
            .user-box {
                position: absolute;
                top: 20px;
                left: 20px;
                z-index: 10;
                background: rgba(20, 20, 40, 0.85);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 15px;
                padding: 8px 14px;
                font-size: 13px;
                color: #00ffcc;
                backdrop-filter: blur(8px);
            }

            /* پنل پایین: دکمه ذخیره موجودی در سمت چپ و دکمه تپ */
            .main-content {
                position: absolute;
                bottom: 30px;
                width: 100%;
                display: flex;
                justify-content: space-around;
                align-items: center;
                z-index: 10;
                padding: 0 20px;
            }

            .save-btn {
                background: linear-gradient(135deg, #f39c12, #d35400);
                border: 2px solid #f1c40f;
                border-radius: 16px;
                padding: 12px 20px;
                font-size: 15px;
                font-weight: bold;
                color: white;
                cursor: pointer;
                box-shadow: 0 8px 25px rgba(243, 156, 18, 0.5);
                transition: transform 0.1s ease;
            }
            .save-btn:active {
                transform: scale(0.95);
            }

            .tap-btn {
                width: 120px;
                height: 120px;
                background: linear-gradient(135deg, #6c5ce7, #00cec9);
                border: none;
                border-radius: 50%;
                font-size: 22px;
                font-weight: bold;
                color: white;
                cursor: pointer;
                box-shadow: 0 10px 30px rgba(108, 92, 231, 0.6);
                transition: transform 0.08s ease;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .tap-btn:active {
                transform: scale(0.92);
            }

            /* افکت پرواز امتیاز هنگام تپ */
            .floating-number {
                position: absolute;
                font-size: 26px;
                font-weight: 900;
                color: #ffd700;
                text-shadow: 0 0 10px rgba(255, 215, 0, 0.9);
                pointer-events: none;
                z-index: 20;
                animation: floatUp 0.6s ease-out forwards;
            }
            @keyframes floatUp {
                0% { opacity: 1; transform: translateY(0) scale(1); }
                100% { opacity: 0; transform: translateY(-70px) scale(1.4); }
            }
        </style>
    </head>
    <body>

        <div class="game-container">
            <div class="overlay"></div>

            <div class="user-box" id="userInfo">بارگذاری...</div>

            <div class="header-top">
                <div class="score-box">
                    <span style="font-size: 20px;">🪙</span>
                    <div class="score-value" id="score">0</div>
                </div>
            </div>

            <div class="main-content">
                <button class="save-btn" id="saveBtn">💾 ذخیره موجودی</button>
                <button class="tap-btn" id="tapButton">TAP!</button>
            </div>
        </div>

        <script>
            const tg = window.Telegram.WebApp;
            tg.expand();

            let score = 0;
            const scoreElement = document.getElementById('score');
            const tapButton = document.getElementById('tapButton');
            const saveBtn = document.getElementById('saveBtn');
            const userInfo = document.getElementById('userInfo');

            if (tg.initDataUnsafe && tg.initDataUnsafe.user) {
                const userName = tg.initDataUnsafe.user.first_name || "بازیکن";
                userInfo.innerText = `سلام، ${userName}`;
            } else {
                userInfo.innerText = "نسخه آزمایشی";
            }

            tapButton.addEventListener('click', (e) => {
                score += 1;
                scoreElement.innerText = score;

                if (tg.HapticFeedback) {
                    tg.HapticFeedback.impactOccurred('medium');
                }

                const rect = tapButton.getBygetBoundingClientRect ? tapButton.getBoundingClientRect() : {left: window.innerWidth/2, top: window.innerHeight/2};
                const x = e.clientX || (rect.left + rect.width / 2);
                const y = e.clientY || rect.top;

                const floatText = document.createElement('div');
                floatText.className = 'floating-number';
                floatText.innerText = '+1';
                floatText.style.left = `${x - 10}px`;
                floatText.style.top = `${y - 30}px`;
                
                document.body.appendChild(floatText);
                setTimeout(() => {
                    floatText.remove();
                }, 600);
            });

            saveBtn.addEventListener('click', () => {
                if (tg.HapticFeedback) {
                    tg.HapticFeedback.notificationOccurred('success');
                }
                alert("موجودی شما با موفقیت ذخیره شد!");
            });
        </script>
    </body>
    </html>
    """
    return html_content

@app.get("/health")
async def health_check():
    return {"status": "online", "project": "NexaTap ($NXTP)", "security": "Active"}


























from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import sqlite3
import os

app = FastAPI()

# --- تنظیمات و راه‌اندازی دیتابیس (SQLite) ---
DB_FILE = "database.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    # جدول کاربران با ساختاری انعطاف‌پذیر برای توسعه‌های آینده
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            username TEXT,
            score INTEGER DEFAULT 0,
            last_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# اجرای تابع ساخت دیتابیس هنگام بالا آمدن سرور
init_db()

# مدل داده برای دریافت درخواست‌های ذخیره امتیاز از فرانت‌اند
class ScoreUpdate(BaseModel):
    user_id: str
    username: str
    score: int


# --- API های سرور ---

@app.post("/api/save_score")
async def save_score(data: ScoreUpdate):
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # بررسی اینکه آیا کاربر قبلاً وجود داشته یا نه (UPSERT)
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
        raise HTTPException(status_code=500, status.strerror(str(e)))


@app.get("/api/get_score/{user_id}")
async def get_score(user_id: str):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT score FROM users WHERE user_id = ?', (user_id,))
    row = cursor.fetchone()
    conn.close()
    
    current_score = row[0] if row else 0
    return {"user_id": user_id, "score": current_score}


# --- فرانت‌اند بازی (HTML/JS) ---
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
            * {
                box-sizing: border-box;
                user-select: none;
                -webkit-user-select: none;
            }
            body, html {
                margin: 0;
                padding: 0;
                width: 100%;
                height: 100%;
                overflow: hidden;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: #0c0c1e;
            }
            .game-container {
                position: relative;
                width: 100%;
                height: 100%;
                background-image: url('https://raw.githubusercontent.com/ghorfeabohosein-png/nexatap-backend/main/character.jpg');
                background-size: cover;
                background-position: center;
                display: flex;
                flex-direction: column;
                justify-content: space-between;
                align-items: center;
            }
            .overlay {
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(12, 12, 30, 0.25);
                z-index: 1;
            }
            .header-top {
                position: absolute;
                top: 20px;
                right: 20px;
                z-index: 10;
            }
            .score-box {
                background: rgba(20, 20, 40, 0.85);
                border: 2px solid #00ffcc;
                border-radius: 20px;
                padding: 8px 18px;
                display: flex;
                align-items: center;
                gap: 10px;
                box-shadow: 0 0 20px rgba(0, 255, 204, 0.4);
                backdrop-filter: blur(8px);
            }
            .score-value {
                font-size: 26px;
                font-weight: 900;
                color: #ffd700;
                text-shadow: 0 0 12px rgba(255, 215, 0, 0.7);
            }
            .user-box {
                position: absolute;
                top: 20px;
                left: 20px;
                z-index: 10;
                background: rgba(20, 20, 40, 0.85);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 15px;
                padding: 8px 14px;
                font-size: 13px;
                color: #00ffcc;
                backdrop-filter: blur(8px);
            }
            .main-content {
                position: absolute;
                bottom: 30px;
                width: 100%;
                display: flex;
                justify-content: space-around;
                align-items: center;
                z-index: 10;
                padding: 0 20px;
            }
            .save-btn {
                background: linear-gradient(135deg, #f39c12, #d35400);
                border: 2px solid #f1c40f;
                border-radius: 16px;
                padding: 12px 20px;
                font-size: 15px;
                font-weight: bold;
                color: white;
                cursor: pointer;
                box-shadow: 0 8px 25px rgba(243, 156, 18, 0.5);
                transition: transform 0.1s ease;
            }
            .save-btn:active {
                transform: scale(0.95);
            }
            .tap-btn {
                width: 120px;
                height: 120px;
                background: linear-gradient(135deg, #6c5ce7, #00cec9);
                border: none;
                border-radius: 50%;
                font-size: 22px;
                font-weight: bold;
                color: white;
                cursor: pointer;
                box-shadow: 0 10px 30px rgba(108, 92, 231, 0.6);
                transition: transform 0.08s ease;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .tap-btn:active {
                transform: scale(0.92);
            }
            .floating-number {
                position: absolute;
                font-size: 26px;
                font-weight: 900;
                color: #ffd700;
                text-shadow: 0 0 10px rgba(255, 215, 0, 0.9);
                pointer-events: none;
                z-index: 20;
                animation: floatUp 0.6s ease-out forwards;
            }
            @keyframes floatUp {
                0% { opacity: 1; transform: translateY(0) scale(1); }
                100% { opacity: 0; transform: translateY(-70px) scale(1.4); }
            }
        </style>
    </head>
    <body>

        <div class="game-container">
            <div class="overlay"></div>

            <div class="user-box" id="userInfo">بارگذاری...</div>

            <div class="header-top">
                <div class="score-box">
                    <span style="font-size: 20px;">🪙</span>
                    <div class="score-value" id="score">0</div>
                </div>
            </div>

            <div class="main-content">
                <button class="save-btn" id="saveBtn">💾 ذخیره موجودی</button>
                <button class="tap-btn" id="tapButton">TAP!</button>
            </div>
        </div>

        <script>
            const tg = window.Telegram.WebApp;
            tg.expand();

            let score = 0;
            let userId = "guest_user";
            let userName = "مهمان";

            const scoreElement = document.getElementById('score');
            const tapButton = document.getElementById('tapButton');
            const saveBtn = document.getElementById('saveBtn');
            const userInfo = document.getElementById('userInfo');

            // تشخیص اطلاعات کاربر از تلگرام
            if (tg.initDataUnsafe && tg.initDataUnsafe.user) {
                userId = String(tg.initDataUnsafe.user.id);
                userName = tg.initDataUnsafe.user.first_name || "بازیکن";
                userInfo.innerText = `سلام، ${userName}`;
                
                // دریافت امتیاز ذخیره شده کاربر از سرور
                fetch(`/api/get_score/${userId}`)
                    .then(response => response.json())
                    .then(data => {
                        score = data.score;
                        scoreElement.innerText = score;
                    })
                    .catch(err => console.log("خطا در دریافت امتیاز:", err));
            } else {
                userInfo.innerText = "نسخه آزمایشی";
            }

            // منطق تپ کردن
            tapButton.addEventListener('click', (e) => {
                score += 1;
                scoreElement.innerText = score;

                if (tg.HapticFeedback) {
                    tg.HapticFeedback.impactOccurred('medium');
                }

                const rect = tapButton.getBoundingClientRect();
                const x = e.clientX || (rect.left + rect.width / 2);
                const y = e.clientY || rect.top;

                const floatText = document.createElement('div');
                floatText.className = 'floating-number';
                floatText.innerText = '+1';
                floatText.style.left = `${x - 10}px`;
                floatText.style.top = `${y - 30}px`;
                
                document.body.appendChild(floatText);
                setTimeout(() => {
                    floatText.remove();
                }, 600);
            });

            // دکمه ذخیره موجودی (ارسال به سرور و دیتابیس)
            saveBtn.addEventListener('click', () => {
                if (tg.HapticFeedback) {
                    tg.HapticFeedback.notificationOccurred('success');
                }

                fetch('/api/save_score', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        user_id: userId,
                        username: userName,
                        score: score
                    })
                })
                .then(response => response.json())
                .then(data => {
                    alert("موجودی شما با موفقیت در دیتابیس سرور ذخیره شد! ✅");
                })
                .catch(error => {
                    alert("خطا در ارتباط با سرور هنگام ذخیره.");
                });
            });
        </script>
    </body>
    </html>
    """
    return html_content

@app.get("/health")
async def health_check():
    return {"status": "online", "project": "NexaTap ($NXTP)", "database": "SQLite Active"}
