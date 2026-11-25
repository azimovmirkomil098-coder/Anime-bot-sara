# Anime Bot Sara 🇺🇿

O‘zbek tilidagi Telegram anime katalogi va ko‘p kanalli post boshqaruv boti.

## Imkoniyatlar
- Anime qidirish (Jikan API / MyAnimeList ma’lumotlari)
- Anime haqida tavsif, janr, yil, reyting va poster
- Sevimlilar ro‘yxati
- Anime kodlari orqali katalogdan topish va qismlarni ko‘rish
- Admin panel orqali anime va qismlar qo‘shish
- Bir nechta Telegram kanalini qo‘shish/o‘chirish
- Matn, rasm yoki video bilan post tayyorlash, preview va tanlangan kanallarga yuborish
- SQLite ma’lumotlar bazasi

> Bot anime epizodlarini noqonuniy tarqatmaydi. Katalogga kontentni faqat uni tarqatish huquqiga ega adminlar qo‘shishi kerak.

## O‘rnatish
1. Python 3.10+ o‘rnating.
2. `pip install -r requirements.txt`
3. `.env.example` faylidan `.env` nusxa yarating.
4. `.env` ichida `BOT_TOKEN` va `ADMIN_IDS` ni to‘ldiring.
5. Botni har bir kanalga administrator qilib qo‘shing (post yuborish huquqi bilan).
6. `python main.py`

## Admin sozlamalari
- `ADMIN_IDS`: Telegram numeric ID'lari, vergul bilan ajrating. Masalan: `123456789,987654321`
- Botda `/admin` yoki **🛠 Admin panel** tugmasi orqali admin panelni oching.
- Kanal qo‘shish: kanal username (`@kanal`) yoki `-100...` ko‘rinishidagi ID yuboring.
- Bot kanal admini bo‘lishi kerak.
- Katalogga anime qo‘shing, keyin anime kodini tanlab qism media faylini yuklang.

## Render
Render'da **Web Service** yarating va repository'ni ulang. `render.yaml` konfiguratsiyasi Web Service va `/health` sog‘liq tekshiruv endpointini belgilaydi. Environment Variables bo‘limida `BOT_TOKEN` va `ADMIN_IDS` kiriting. Persistent Disk yoqilgan bo‘lishi kerak, aks holda SQLite ma’lumotlari deploy vaqtida yo‘qolishi mumkin.

## Eslatma
Jikan API uchinchi tomon xizmati; vaqtinchalik cheklov yoki uzilishlar bo‘lishi mumkin. Bot tokenini hech qachon GitHub'ga yuklamang.
