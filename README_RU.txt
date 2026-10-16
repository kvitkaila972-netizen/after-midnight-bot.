ПОДГОТОВКА К РАЗМЕЩЕНИЮ НА RENDER С ТЕЛЕФОНА

1. Создайте Telegram-бота через @BotFather командой /newbot и скопируйте токен.
2. Создайте аккаунт GitHub в браузере.
3. Создайте новый репозиторий (New repository), например after-midnight-bot, поставьте Public и Create repository.
4. Через Add file -> Upload files загрузите файлы и папку проекта. Если мобильный GitHub не позволяет загрузить папки, загружайте файлы по одному и создайте stories/story_data.py в нужной папке через Add file -> Create new file.
5. Создайте сервис на Render из этого репозитория: https://render.com/
6. Если Render предлагает выбрать Blueprint, можно использовать render.yaml. Если создаёте Web Service вручную, укажите:
   Build Command: pip install -r requirements.txt
   Start Command: python bot.py
7. В Environment добавьте:
   BOT_TOKEN = токен от BotFather
   PUBLIC_URL = публичный HTTPS-адрес сервиса Render, например https://имя-сервиса.onrender.com
   Важно: PUBLIC_URL без слеша в конце.
8. Нажмите Deploy.
9. После успешного деплоя откройте Telegram и отправьте боту /start.

ПРИМЕЧАНИЯ:
- Это версия webhook для хостинга, а не локальный polling.
- Бесплатные инстансы могут засыпать и иметь ограничения; проверьте текущие условия Render. Для гарантированной работы 24/7 может понадобиться платный тариф или другой хостинг.
- Никогда не загружайте токен в GitHub. Вводите его только в Environment на Render.
