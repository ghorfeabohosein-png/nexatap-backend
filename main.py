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
            /* پس‌زمینه گرافیکی با استفاده از تصویر اصلی کاراکتر و سکه‌های نئونی */
            .game-container {
                position: relative;
                width: 100%;
                height: 100%;
                background-image: url('https://raw.githubusercontent.com/ghorfeabohosein-png/nexatap-backend/main/character.jpg'); /* در صورت نیاز لینک عکس رو اینجا تنظیم می‌کنیم */
                background-size: cover;
                background-position: center;
                display: flex;
                flex-direction: column;
                justify-content: space-between;
                align-items: center;
            }
            
            /* لایه تاریک‌کننده ملایم روی تصویر برای خوانایی بهتر متن‌ها */
            .overlay {
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(12, 12, 30, 0.4);
                z-index: 1;
            }

            /* بخش بالای صفحه: امتیاز در بالا سمت راست */
            .header-top {
                position: absolute;
                top: 20px;
                right: 20px;
                z-index: 10;
                display: flex;
                flex-direction: column;
                align-items: flex-end;
            }
            .score-box {
                background: rgba(20, 20, 40, 0.85);
                border: 2px solid #00ffcc;
                border-radius: 20px;
                padding: 8px 18px;
                display: flex;
                align-items: center;
                gap: 8px;
                box-shadow: 0 0 15px rgba(0, 255, 204, 0.4);
                backdrop-filter: blur(5px);
            }
            .score-label {
                font-size: 11px;
                color: #a29bfe;
                font-weight: bold;
                letter-spacing: 1px;
            }
            .score-value {
                font-size: 24px;
                font-weight: 900;
                color: #ffd700;
                text-shadow: 0 0 10px rgba(255, 215, 0, 0.6);
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
                font-size: 12px;
                color: #00ffcc;
                backdrop-filter: blur(5px);
            }

            /* ناحیه تعاملی برای تپ کردن روی کل صفحه یا مرکز */
            .click-area {
                position: absolute;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                z-index: 5;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
            }

            /* دکمه نامرئی یا افکت کلیک وسط صفحه روی کاراکتر */
            .tap-target {
                width: 220px;
                height: 280px;
                border-radius: 50%;
                background: transparent;
                outline: none;
                border: none;
                cursor: pointer;
            }

            /* افکت پرواز عدد هنگام تپ */
            .floating-number {
                position: absolute;
                font-size: 28px;
                font-weight: 900;
                color: #ffd700;
                text-shadow: 0 0 10px rgba(255, 215, 0, 0.8);
                pointer-events: none;
                z-index: 20;
                animation: floatUp 0.6s ease-out forwards;
            }
            @keyframes floatUp {
                0% { opacity: 1; transform: translateY(0) scale(1); }
                100% { opacity: 0; transform: translateY(-80px) scale(1.4); }
            }
        </style>
    </head>
    <body>

        <div class="game-container">
            <div class="overlay"></div>

            <!-- اطلاعات کاربر در بالا سمت چپ -->
            <div class="user-box" id="userInfo">بارگذاری...</div>

            <!-- امتیاز در بالا سمت راست -->
            <div class="header-top">
                <div class="score-box">
                    <span style="font-size: 18px;">🪙</span>
                    <div>
                        <div class="score-label">SCORE</div>
                        <div class="score-value" id="score">0</div>
                    </div>
                </div>
            </div>

            <!-- ناحیه کلیک روی کاراکتر -->
            <div class="click-area" id="clickArea">
                <div class="tap-target"></div>
            </div>
        </div>

        <script>
            const tg = window.Telegram.WebApp;
            tg.expand();

            let score = 0;
            const scoreElement = document.getElementById('score');
            const userInfo = document.getElementById('userInfo');
            const clickArea = document.getElementById('clickArea');

            // تنظیم نام کاربر از تلگرام
            if (tg.initDataUnsafe && tg.initDataUnsafe.user) {
                const userName = tg.initDataUnsafe.user.first_name || "بازیکن";
                userInfo.innerText = `سلام، ${userName}`;
            } else {
                userInfo.innerText = "نسخه وب";
            }

            // منطق تپ روی صفحه و کاراکتر
            clickArea.addEventListener('click', (e) => {
                score += 1;
                scoreElement.innerText = score;

                // لرزش گوشی
                if (tg.HapticFeedback) {
                    tg.HapticFeedback.impactOccurred('medium');
                }

                // ایجاد عدد شناور در محل کلیک
                const x = e.clientX;
                const y = e.clientY;

                const floatText = document.createElement('div');
                floatText.className = 'floating-number';
                floatText.innerText = '+1';
                floatText.style.left = `${x - 15}px`;
                floatText.style.top = `${y - 20}px`;
                
                document.body.appendChild(floatText);
                setTimeout(() => {
                    floatText.remove();
                }, 600);
            });
        </script>
    </body>
    </html>
    """
    return html_content

@app.get("/health")
async def health_check():
    return {"status": "online", "project": "NexaTap ($NXTP)", "security": "Active"}
