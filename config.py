"""
---------------------------------------------------------
برنامه مدیریتی VIVO
Config File
---------------------------------------------------------
"""

from pathlib import Path

# پوشه اصلی پروژه
BASE_DIR = Path(__file__).resolve().parent

# دیتابیس
DATABASE_PATH = BASE_DIR / "database" / "vivo_old.db"

# پوشه ذخیره مدارک
IMAGES_PATH = BASE_DIR / "images"

# پوشه آیکون ها
ICONS_PATH = BASE_DIR / "icons"

# لوگوی برنامه
APP_ICON = ICONS_PATH / "logo.ico"

# نام برنامه
APP_NAME = "برنامه مدیریتی VIVO"

# تعداد کلبه ها
TOTAL_COTTAGES = 16

# رمز پیش فرض مدیر
DEFAULT_PASSWORD = "123456"

# فرمت تاریخ
DATE_FORMAT = "%Y/%m/%d"

# فرمت شماره موبایل
PHONE_LENGTH = 11