# Anime Bot Sara — Render Web Service

## Funksiyalar
- Admin panel faqat `ADMIN_IDS` dagi Telegram foydalanuvchilariga ko‘rinadi.
- Admin anime qo‘shadi: nomi, unikal kodi, janri, yili, tili, tavsifi va poster.
- Admin videolarni ketma-ket yuboradi; bot avtomatik qism raqamini beradi. Tugatish: `/done`.
- Foydalanuvchi kod yozmasdan `📚 Anime katalogi` tugmasi orqali animelarni ko‘radi; sahifalash mavjud.
- Kanal postida anime ma’lumotlari va `▶️ Animeni ko‘rish` deep-link tugmasi bo‘ladi.
- Anime ko‘rish va qism yuborishdan oldin majburiy obuna tekshiriladi.
- Admin post kanallari va majburiy obuna kanallarini boshqaradi.
- Webhook + HTTP health endpoint: `/health`.

## Render Web Service sozlamalari
Repository ichida loyiha `anime_work/` papkasida bo‘lsa:
- Root Directory: `anime_work`

Agar `anime_work` ichidagi fayllarni repository rootiga joylagan bo‘lsangiz, Root Directory bo‘sh qolsin.

- Runtime: Python 3
- Build Command: `pip install -r requirements.txt`
- Start Command: `python main.py`
- Health Check Path: `/health`

## Environment Variables
- `BOT_TOKEN` — BotFather tokeni.
- `ADMIN_IDS` — admin Telegram ID raqamlari, vergul bilan ajratiladi.
- `DATABASE_PATH` — masalan `anime_bot.db` (doimiy saqlash uchun persistent disk yoki tashqi DB kerak).
- `WEBHOOK_SECRET` — ixtiyoriy, Telegram webhook uchun maxfiy belgi; bo‘sh bo‘lsa token asosida yaratiladi.

Render Web Service `RENDER_EXTERNAL_URL` va `PORT` qiymatlarini avtomatik beradi. Bot webhook URL ni avtomatik o‘rnatadi.

## Muhim
- Bot majburiy obuna kanallarida administrator bo‘lishi kerak, aks holda a’zolikni tekshira olmaydi.
- Kanalga post yuborish uchun botga post yuborish huquqi berilsin.
- Bepul Web Service uxlab qolishi mumkin; SQLite fayli doimiy saqlanishi kafolatlanmaydi. Ma’lumotlarni yo‘qotmaslik uchun persistent disk yoki tashqi PostgreSQL ishlating.
- Faqat tarqatish huquqiga ega bo‘lgan videolarni joylang.
