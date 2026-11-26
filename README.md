# Anime Bot Sara — Render Web Service

## Funksiyalar
- Admin panel faqat `ADMIN_IDS` dagi Telegram foydalanuvchilariga ko‘rinadi.
- Admin anime qo‘shadi: nomi, unikal kodi, janri, yili, tili, tavsifi va poster.
- Admin videolarni ketma-ket yuboradi; bot avtomatik qism raqamini beradi. Tugatish: `/done`.
- Foydalanuvchi `📚 Anime katalogi` tugmasi orqali animelarni ko‘radi; sahifalash mavjud.
- Kanal postida anime ma’lumotlari va `▶️ Animeni ko‘rish` deep-link tugmasi bo‘ladi.
- Anime ko‘rish va qism yuborishdan oldin majburiy obuna tekshiriladi.
- Admin post kanallari va majburiy obuna kanallarini boshqaradi.
- Istalgan asosiy menyu tugmasi bosilganda avvalgi kiritish jarayoni bekor qilinadi; `/cancel` ham joriy jarayonni bekor qiladi.
- Webhook va HTTP health endpoint: `/health`.

## Render Web Service sozlamalari
Agar loyiha `anime_work/` papkasida bo‘lsa:
- Root Directory: `anime_work`

Agar loyiha fayllari repository rootida bo‘lsa, Root Directory bo‘sh qolsin.

- Runtime: Python 3
- Build Command: `pip install -r requirements.txt`
- Start Command: `python main.py`
- Health Check Path: `/health`

## Environment Variables
- `BOT_TOKEN` — BotFather tokeni.
- `ADMIN_IDS` — admin Telegram ID raqamlari, vergul bilan ajratiladi.
- `DATABASE_PATH` — masalan `anime_bot.db`; doimiy saqlash uchun persistent disk yoki tashqi DB kerak.
- `WEBHOOK_SECRET` — Telegram webhook uchun maxfiy belgi; `render.yaml` uni avtomatik yaratadi.

Render Web Service `RENDER_EXTERNAL_URL` va `PORT` qiymatlarini avtomatik beradi. Bot webhook URL ni avtomatik o‘rnatadi.

## Muhim
- Majburiy obuna kanallarida bot administrator bo‘lishi kerak, aks holda a’zolikni tekshira olmaydi.
- Kanalga post yuborish uchun botga post yuborish huquqi berilsin.
- Bepul Web Service uxlab qolishi mumkin; SQLite fayli doimiy saqlanishi kafolatlanmaydi.
- Faqat tarqatish huquqiga ega bo‘lgan videolarni joylang.
