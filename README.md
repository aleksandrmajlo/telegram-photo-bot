##    Local

  1 - ngrok http 8080

  2 - set Webhook Telegram

  curl -F "url=https://telegram-photo-bot-9gnb.onrender.com/webhook" https://api.telegram.org/bot7811367207:AAH39vjyrr3mqz1dvBmgr25WBf9GpGat8LI/setWebhook

  3 -  cd  /Volumes/Hrad/Python/Bot

        python3  bot.py   

##   Render.com

	•	Environment: Python
	•	Build Command: pip install -r requirements.txt
	•	Start Command: python bot.py или gunicorn bot:app

1 - set Webhook Telegram

     curl -F "url=https://telegram-photo-bot-9gnb.onrender.com/webhook" https://api.telegram.org/bot7811367207:AAH39vjyrr3mqz1dvBmgr25WBf9GpGat8LI/setWebhook

2 - git commit
     
      git add .
      git commit -m "Add all"
      git push origin main
