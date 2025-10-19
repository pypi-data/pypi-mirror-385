# antispam_core/config.py
"""
📦 فایل تنظیمات سراسری پروژه
تمام مقادیر پیکربندی (configurations) و مسیرهای پروژه در این فایل متمرکز هستند.
"""

import os, asyncio
from typing import Dict
from pyrogram import Client
from pytz import timezone

# ============================================================
# 🧠 تنظیمات اسپم و پیام‌ها
# ============================================================
spam_config = {
    "spamTarget": "",       # هدف ارسال (chat_id یا username)
    "TimeSleep": 5.0,       # فاصله بین هر ارسال
    "caption": "",          # کپشن پایانی (اختیاری)
    "run": False,           # وضعیت اجرا
    "useridMen": 1,         # شناسه کاربر برای منشن
    "textMen": "",          # متن منشن
    "is_menshen": False,     # فعال یا غیرفعال بودن منشن
    "BATCH_SIZE":1
}
# ============================================================
# 🔐 اطلاعات ورود و مسیرها
# ============================================================
login: Dict = {}

# مسیرهای مربوط به اکانت‌ها
ACCOUNTS_FOLDER = "acc"
ACCOUNTS_DATA_FOLDER = "acc_data"

# اطمینان از وجود پوشه‌ها
os.makedirs(ACCOUNTS_FOLDER, exist_ok=True)
os.makedirs(ACCOUNTS_DATA_FOLDER, exist_ok=True)

# ============================================================
# 🌍 منطقه زمانی
# ============================================================
TEHRAN_TZ = timezone("Asia/Tehran")

# ============================================================
# 🤖 مدیریت کلاینت‌ها
# ============================================================
client_pool: Dict[str, Client] = {}
client_locks: Dict[str, asyncio.Lock] = {}

# ============================================================
# 👑 مالک / ادمین اصلی
# ============================================================
OWNER_ID: list[int] = []

def set_owner_ids(ids: list[int]):
    """
    تنظیم آی‌دی مالک (Owner IDs)
    در فایل main.py مقداردهی می‌شود تا برای هر کاربر جداگانه شخصی‌سازی شود.
    """
    global OWNER_ID
    OWNER_ID = ids
