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
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>NexaTap - نکست‌تپ</title>
        <script src="https://telegram.org/js/telegram-web-app.js"></script>
        <style>
            * {
                box-sizing: border-box;
                user-select: none;
                -webkit-user-select: none;
            }
            body {
                background: radial-gradient(circle at center, #1b1b3a 0%, #0f0f1a 100%);
                color: #ffffff;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 0;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: space-between;
                height: 100vh;
                overflow: hidden;
            }
            .header {
                margin-top: 20px;
                text-align: center;
            }
            .user-welcome {
                font-size: 14px;
                color: #00ffcc;
                margin-bottom: 5px;
            }
            .token-title {
                font-size: 18px;
                font-weight: bold;
                color: #a29bfe;
                letter-spacing: 1px;
            }
            .score-container {
                display: flex;
                align-items: center;
                gap: 10px;
                background: rgba(255, 255, 255, 0.05);
                padding: 10px 25px;
                border-radius: 30px;
                border: 1px solid rgba(255, 255, 255, 0.1);
                box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
                backdrop-filter: blur(4px);
                margin: 10px 0;
            }
            .score-icon {
                font-size: 28px;
            }
            .score {
                font-size: 36px;
                font-weight: 800;
                color: #ffd700;
                text-shadow: 0 0 10px rgba(255, 215, 0, 0.5);
            }
            /* بخش کاراکتر و دکمه تپ */
            .game-area {
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                flex-grow: 1;
                position: relative;
            }
            .character-container {
                width: 140px;
                height: 140px;
                background: radial-gradient(circle, rgba(0,255,204,0.2) 0%, rgba(108,92,231,0) 70%);
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                margin-bottom: 20px;
                animation: float 3s ease-in-out infinite;
            }
            .character-avatar {
                font-size: 70px;
                filter: drop-shadow(0 0 15px rgba(0, 255, 204, 0.6));
            }
            @keyframes float {
                0% { transform: translateY(0px); }
                50% { transform: translateY(-10px); }
                100% { transform: translateY(0px); }
            }
            .tap-btn {
                background: linear-gradient(135deg, #6c5ce7, #00cec9);
                border: none;
                border-radius: 50%;
                width: 170px;
                height: 170px;
                font-size: 26px;
                font-weight: bold;
                color: #fff;
                cursor: pointer;
                box-shadow: 0 15px 30px rgba(108, 92, 231, 0.4), inset 0 4px 6px rgba(255, 255, 255, 0.3);
                transition: transform 0.08s ease, box-shadow 0.08s ease;
                outline: none;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .tap-btn:active {
                transform: scale(0.93);
                box-shadow: 0 5px 15px rgba(108, 92, 231, 0.3);
            }
            .footer {
                margin-bottom: 25px;
                font-size: 12px;
                color: #636e72;
                letter-spacing: 0.5px;
            }
            /* افکت پرواز امتیاز روی صفحه هنگام کلیک */
            .floating-number {
                position: absolute;
                font-size: 20px;
                font-weight: bold;
                color: #00ffcc;
                pointer-events: none;
                animation: fadeUp 0.6s ease-out forwards;
            }
            @keyframes fadeUp {
                0% { opacity: 1; transform: translateY(0) scale(1); }
                100% { opacity: 0; transform: translateY(-60px) scale(1.3); }
            }
        </style>
    </head>
    <body>

        <div class="header">
            <div class="user-welcome" id="userInfo">در حال بارگذاری...</div>
            <div class="token-title">NEXATAP ($NXTP)</div>
        </div>

        <div class="game-area">
            <!-- کاراکتر بازی -->
            <div class="character-container">
                <div class="character-avatar" id="charEmoji">🦊</div>
            </div>

            <div class="score-container">
                <span class="score-icon">🪙</span>
                <span class="score" id="score">0</span>
            </div>

            <button class="tap-btn" id="tapButton">TAP!</button>
        </div>

        <div class="footer">
            Secured by Telegram WebApp & Render
        </div>

        <script>
            const tg = window.Telegram.WebApp;
            tg.expand();

            let score = 0;
            const scoreElement = document.getElementById('score');
            const tapButton = document.getElementById('tapButton');
            const userInfo = document.getElementById('userInfo');
            const gameArea = document.querySelector('.game-area');

            // تشخیص کاربر
            if (tg.initDataUnsafe && tg.initDataUnsafe.user) {
                const userName = tg.initDataUnsafe.user.first_name || "کاربر عزیز";
                userInfo.innerText = `خوش آمدید، ${userName}`;
            } else {
                userInfo.innerText = "نسخه آزمایشی وب";
            }

            // منطق تپ کردن با افکت پرواز امتیاز
            tapButton.addEventListener('click', (e) => {
                score += 1;
                scoreElement.innerText = score;

                // لرزش گوشی
                if (tg.HapticFeedback) {
                    tg.HapticFeedback.impactOccurred('medium');
                }

                // ساخت عدد شناور روی صفحه
                const rect = tapButton.getBoundingClientRect();
                const x = e.clientX || (rect.left + rect.width / 2);
                const y = e.clientY || (rect.top + rect.height / 2);

                const floatText = document.createElement('div');
                floatText.className = 'floating-number';
                floatText.innerText = '+1';
                floatText.style.left = `${x - 10}px`;
                floatText.style.top = `${y - 40}px`;
                
                gameArea.appendChild(floatText);
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
