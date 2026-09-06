from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def read_root():
    # یک صفحه HTML مدرن و ریسپانسیو با قابلیت تشخیص زبان کاربر
    html_content = """
    <!DOCTYPE html>
    <html lang="fa" dir="rtl">
    کلیک کنید تا امتیاز بگیرید ($NXTP)
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>NexaTap Mini App</title>
        <script src="https://telegram.org/js/telegram-web-app.js"></script>
        <style>
            body {
                background: linear-gradient(135deg, #1a1a2e, #16213e);
                color: #ffffff;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 0;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                height: 100vh;
                overflow: hidden;
            }
            .container {
                text-align: center;
            }
            h1 {
                font-size: 24px;
                margin-bottom: 5px;
                color: #00ffcc;
            }
            .score {
                font-size: 48px;
                font-weight: bold;
                margin: 20px 0;
                color: #ffd700;
            }
            .tap-btn {
                background: radial-gradient(circle, #00ffcc, #0088cc);
                border: none;
                border-radius: 50%;
                width: 180px;
                height: 180px;
                font-size: 24px;
                font-weight: bold;
                color: #fff;
                cursor: pointer;
                box-shadow: 0 10px 25px rgba(0, 255, 204, 0.4);
                transition: transform 0.1s ease, box-shadow 0.1s ease;
                outline: none;
            }
            .tap-btn:active {
                transform: scale(0.92);
                box-shadow: 0 5px 15px rgba(0, 255, 204, 0.2);
            }
            .user-info {
                margin-top: 20px;
                font-size: 14px;
                color: #aaa;
            }
        </style>
    </head>
    <body>

        <div class="container">
            <h1 id="title-text">NexaTap ($NXTP)</h1>
            <div class="score" id="score">0</div>
            <button class="tap-btn" id="tapButton">TAP!</button>
            <div class="user-info" id="userInfo">Connecting...</div>
        </div>

        <script>
            // راه‌اندازی تلگرام وب‌اپ
            const tg = window.Telegram.WebApp;
            tg.expand();

            let score = 0;
            const scoreElement = document.getElementById('score');
            const tapButton = document.getElementById('tapButton');
            const titleText = document.getElementById('title-text');
            const userInfo = document.getElementById('userInfo');

            // تشخیص زبان کاربر از تلگرام یا مرورگر
            let userLang = 'en';
            if (tg.initDataUnsafe && tg.initDataUnsafe.user) {
                const langCode = tg.initDataUnsafe.user.language_code;
                if (langCode === 'fa' || langCode === 'tg') {
                    userLang = 'fa';
                }
                const userName = tg.initDataUnsafe.user.first_name || "User";
                userInfo.innerText = userLang === 'fa' ? `خوش آمدید، ${userName}!` : `Welcome, ${userName}!`;
            } else {
                userInfo.innerText = "Web Mode";
            }

            // تنظیم متن‌ها بر اساس زبان
            if (userLang === 'fa') {
                document.documentElement.setAttribute('dir', 'rtl');
                titleText.innerText = "تپ‌توارن نکست‌تپ ($NXTP)";
                tapButton.innerText = "بزن رویش!";
            } else {
                document.documentElement.setAttribute('dir', 'ltr');
                titleText.innerText = "NexaTap ($NXTP)";
                tapButton.innerText = "TAP!";
            }

            // منطق تپ کردن
            tapButton.addEventListener('click', () => {
                score += 1;
                scoreElement.innerText = score;
                
                // لرزش گوشی هنگام کلیک (اگر در تلگرام باشد)
                if (tg.HapticFeedback) {
                    tg.HapticFeedback.impactOccurred('light');
                }
            });
        </script>
    </body>
    </html>
    """
    return html_content

@app.get("/health")
async def health_check():
    return {"status": "online", "project": "NexaTap ($NXTP)", "security": "Active"}
