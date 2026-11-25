# Anime Bot Sara

## Render Web Service sozlamalari

- Service type: **Web Service**
- Runtime: **Python 3**
- Root Directory: `anime_work` (agar GitHub repozitoriyingiz ichida shu papka bo‘lsa; agar fayllar repozitoriy ildizida turgan bo‘lsa, bo‘sh qoldiring)
- Build Command: `pip install -r requirements.txt`
- Start Command: `python main.py`
- Health Check Path: `/health`

Render `RENDER_EXTERNAL_URL` va `PORT` qiymatlarini avtomatik beradi. Bot Telegram bilan long polling emas, **webhook** orqali ishlaydi.

## Environment Variables

- `BOT_TOKEN` — BotFather tokeni. Maxfiy saqlang; GitHub'ga joylamang.
- `ADMIN_IDS` — admin Telegram ID raqamlari, vergul bilan ajrating: `123456789,987654321`.
- `DATABASE_PATH` — `anime_bot.db` (standart). Render bepul Web Service fayl tizimi doimiy emas; restart/deploydan keyin SQLite ma’lumotlari yo‘qolishi mumkin. Doimiy saqlash uchun persistent disk yoki tashqi PostgreSQL kerak.
- `WEBHOOK_SECRET` — ixtiyoriy, Telegram webhook so‘rovlarini tekshirish siri. Render Blueprint orqali yaratilsa, avtomatik qiymat beriladi. Dashboard'da qo‘lda yaratilgan bo‘lsa, bu o‘zgaruvchini o‘zingiz ham kiritishingiz mumkin; kiritilmasa token asosida barqaror qiymat hosil qilinadi.

## Eslatma

- Bot webhook ishlashi uchun Render Web Service ommaviy HTTPS manziliga ega bo‘lishi kerak.
- Bot majburiy obuna kanallarida admin bo‘lishi kerak.
- `handlers/__pycache__` kabi Python cache fayllarini GitHub'ga yuklash shart emas.
