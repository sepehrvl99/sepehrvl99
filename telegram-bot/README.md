```markdown
# Telegram Keyword Alert Bot (Aiogram v3)

## پیش‌نیازها
- Python 3.8+
- Telegram Bot Token (از BotFather)
- SMTP Email Account (برای ارسال هشدار ایمیلی)

## نصب
1. ساخت و فعال‌سازی محیط مجازی:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
2. نصب وابستگی‌ها:
   ```bash
   pip install -r requirements.txt
   ```
3. ویرایش `config.ini` با اطلاعات توکن و SMTP خود.

## استفاده
- اجرای بات:
  ```bash
  python bot.py
  ```

### دستورات
- `/start` یا `/register`: ثبت نام برای دریافت هشدارها
- `/addgroup <group_id>`: افزودن گروه برای مانیتور کردن
- `/addkeyword <keyword>`: افزودن کلیدواژه برای پیگیری
- `/list`: نمایش گروه‌ها و کلیدواژه‌های فعال

## نحوه عملکرد
بات پیام‌های متنی گروه‌های مشخص‌شده را بررسی می‌کند. در صورت یافتن هر یک از کلیدواژه‌ها، یک پیام تلگرامی و یک ایمیل هشدار ارسال می‌شود.
