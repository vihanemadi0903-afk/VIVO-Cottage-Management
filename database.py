import sqlite3
from pathlib import Path
import os
import shutil
import sys
from core.date_utils import DateUtils


class DatabaseManager:

    def __init__(self):

        # =====================================================
        # مسیر دائمی اطلاعات کاربر
        # =====================================================

        app_data = os.environ.get("LOCALAPPDATA")

        if not app_data:
            app_data = str(Path.home() / "AppData" / "Local")

        self.data_path = Path(app_data) / "VIVO"

        self.data_path.mkdir(
            parents=True,
            exist_ok=True
        )

        # پوشه‌های اطلاعات کاربر
        (self.data_path / "Documents").mkdir(
            parents=True,
            exist_ok=True
        )

        (self.data_path / "Backups").mkdir(
            parents=True,
            exist_ok=True
        )

        (self.data_path / "Settings").mkdir(
            parents=True,
            exist_ok=True
        )

        # =====================================================
        # دیتابیس دائمی
        # =====================================================

        self.db_path = self.data_path / "vivo.db"

        # =====================================================
        # اگر اولین اجرای نسخه نصب‌شده است،
        # دیتابیس اولیه را از فایل همراه برنامه کپی کن
        # =====================================================

        if not self.db_path.exists():

            if getattr(sys, "frozen", False):

                bundled_db = (
                        Path(sys._MEIPASS)
                        / "data"
                        / "vivo.db"
                )

            else:

                bundled_db = (
                        Path(__file__).resolve().parent.parent
                        / "data"
                        / "vivo.db"
                )

            if bundled_db.exists():
                shutil.copy2(
                    bundled_db,
                    self.db_path
                )

        # =====================================================
        # ساخت جدول‌ها
        # =====================================================

        self.create_tables()


    # ----------------------------

    def connect(self):

        conn = sqlite3.connect(self.db_path)

        conn.row_factory = sqlite3.Row

        return conn
    # ----------------------------

    def create_tables(self):

        conn = self.connect()

        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            full_name TEXT,

            phone TEXT,

            cottage_number INTEGER,

            check_in TEXT,

            check_in_value INTEGER,

            check_out TEXT,

            check_out_value INTEGER,

            description TEXT
            
            pos_office INTEGER DEFAULT 0,
            
            pos_cafe INTEGER DEFAULT 0,
            
            pos_market INTEGER DEFAULT 0,
            
            cash INTEGER DEFAULT 0,
            
            card_transfer INTEGER DEFAULT 0,
            
            card_transfer_receiver TEXT DEFAULT 
            
            "")
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS customer_files(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            customer_id INTEGER,

            file_path TEXT,

            FOREIGN KEY(customer_id)
            REFERENCES customers(id)
            ON DELETE CASCADE

        )
        """)

        # -------------------------------------------------
        # ستون‌های جدید سیستم ذخیره داخلی مدارک
        # -------------------------------------------------

        cursor.execute(
            "PRAGMA table_info(customer_files)"
        )

        existing_file_columns = {
            row["name"]
            for row in cursor.fetchall()
        }

        if "file_name" not in existing_file_columns:

            cursor.execute(
                """
                ALTER TABLE customer_files
                ADD COLUMN file_name TEXT
                """
            )

        if "file_data" not in existing_file_columns:

            cursor.execute(
                """
                ALTER TABLE customer_files
                ADD COLUMN file_data BLOB
                """
            )

        columns = [
            ("pos_office", "INTEGER DEFAULT 0"),
            ("pos_cafe", "INTEGER DEFAULT 0"),
            ("pos_market", "INTEGER DEFAULT 0"),
            ("cash", "INTEGER DEFAULT 0"),
            ("card_transfer", "INTEGER DEFAULT 0"),
            ("card_transfer_receiver", "TEXT DEFAULT ''")
        ]

        cursor.execute("PRAGMA table_info(customers)")

        existing = [row["name"] for row in cursor.fetchall()]

        for name, column_type in columns:

            if name not in existing:
                cursor.execute(
                    f"ALTER TABLE customers ADD COLUMN {name} {column_type}"
                )

        conn.commit()
        conn.close()

    def validate_phone(self, phone):

        if phone == "":
            return True

        if len(phone) != 11:
            return False

        return phone.isdigit()

    def is_cottage_available(
            self,
            cottage,
            check_in,
            check_out,
            ignore_customer=None
    ):
        """
        اگر کلبه آزاد باشد True
        اگر رزرو تداخل داشته باشد False
        """

        conn = self.connect()
        cursor = conn.cursor()

        if ignore_customer is None:

            cursor.execute("""
                SELECT check_in, check_out
                FROM customers
                WHERE cottage_number=?
            """, (cottage,))

        else:

            cursor.execute("""
                SELECT check_in, check_out
                FROM customers
                WHERE cottage_number=?
                AND id<>?
            """, (cottage, ignore_customer))

        reservations = cursor.fetchall()

        conn.close()

        for reservation in reservations:

            old_in = reservation["check_in"]
            old_out = reservation["check_out"]

            # اگر رزرو قبلی قبل از رزرو جدید تمام شده
            if DateUtils.compare(old_out, check_in) <= 0:
                continue

            # اگر رزرو جدید قبل از رزرو قبلی تمام می‌شود
            if DateUtils.compare(check_out, old_in) <= 0:
                continue

            # در غیر این صورت تداخل وجود دارد
            return False

        return True

    def add_customer(
            self,
            full_name,
            phone,
            cottage,
            check_in,
            check_out,
            description,
            pos_office=0,
            pos_cafe=0,
            pos_market=0,
            cash=0,
            card_transfer=0,
            card_transfer_receiver=""
    ):

        if not self.validate_phone(phone):
            raise ValueError("شماره تماس نامعتبر است.")

        if check_in != "":
            if not DateUtils.is_valid_date(check_in):
                raise ValueError("تاریخ ورود نامعتبر است.")

        if check_out != "":
            if not DateUtils.is_valid_date(check_out):
                raise ValueError("تاریخ خروج نامعتبر است.")

        if check_in != "" and check_out != "":
            if not DateUtils.is_checkout_after_checkin(
                    check_in,
                    check_out
            ):
                raise ValueError(
                    "تاریخ خروج نمی‌تواند قبل از تاریخ ورود باشد."
                )

        if cottage != "" and check_in != "" and check_out != "":

            if not self.is_cottage_available(
                    cottage,
                    check_in,
                    check_out
            ):
                raise ValueError(
                    "این کلبه در این بازه زمانی رزرو شده است."
                )

        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO customers
            (
                full_name,
                phone,
                cottage_number,
                check_in,
                check_out,
                description,
                pos_office,
                pos_cafe,
                pos_market,
                cash,
                card_transfer,
                card_transfer_receiver
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                full_name,
                phone,
                cottage,
                check_in,
                check_out,
                description,
                pos_office,
                pos_cafe,
                pos_market,
                cash,
                card_transfer,
                card_transfer_receiver
            )
        )

        customer_id = cursor.lastrowid

        conn.commit()
        conn.close()

        return customer_id

    def save_customer_files(self, customer_id, files):

        conn = self.connect()
        cursor = conn.cursor()

        try:

            for file in files:

                if not file:
                    continue

                source_path = Path(file)

                # ---------------------------------------------
                # بررسی وجود فایل اصلی
                # ---------------------------------------------

                if not source_path.exists():
                    continue

                if not source_path.is_file():
                    continue

                # ---------------------------------------------
                # خواندن کامل فایل
                # ---------------------------------------------

                with open(
                        source_path,
                        "rb"
                ) as f:

                    file_data = f.read()

                # ---------------------------------------------
                # نام فایل
                # ---------------------------------------------

                file_name = source_path.name

                # ---------------------------------------------
                # ذخیره خود فایل داخل SQLite
                # ---------------------------------------------

                cursor.execute(
                    """
                    INSERT INTO customer_files
                    (
                        customer_id,
                        file_path,
                        file_name,
                        file_data
                    )
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        customer_id,
                        "",
                        file_name,
                        sqlite3.Binary(file_data)
                    )
                )

            conn.commit()

        except Exception:

            conn.rollback()

            raise

        finally:

            conn.close()

    def delete_customer_files(self, customer_id):

        conn = self.connect()
        cursor = conn.cursor()

        cursor.execute(
            """
            DELETE FROM customer_files
            WHERE customer_id=?
            """,
            (customer_id,)
        )

        conn.commit()
        conn.close()

    def get_all_customers(self):
        conn = self.connect()

        cursor = conn.cursor()

        cursor.execute("""

        SELECT *

        FROM customers

        ORDER BY id DESC

        """)

        rows = cursor.fetchall()

        conn.close()

        return rows

    def update_customer(
            self,
            customer_id,
            full_name,
            phone,
            cottage,
            check_in,
            check_out,
            description,
            files,
            pos_office=0,
            pos_cafe=0,
            pos_market=0,
            cash=0,
            card_transfer=0,
            card_transfer_receiver=""
    ):

        conn = self.connect()
        cursor = conn.cursor()

        # -----------------------------
        # به‌روزرسانی اطلاعات مسافر
        # -----------------------------

        cursor.execute(
            """
            UPDATE customers
            SET
                full_name = ?,
                phone = ?,
                cottage_number = ?,
                check_in = ?,
                check_out = ?,
                description = ?,
                pos_office = ?,
                pos_cafe = ?,
                pos_market = ?,
                cash = ?,
                card_transfer = ?,
                card_transfer_receiver = ?
            WHERE id = ?
            """,
            (
                full_name,
                phone,
                cottage,
                check_in,
                check_out,
                description,
                pos_office,
                pos_cafe,
                pos_market,
                cash,
                card_transfer,
                card_transfer_receiver,
                customer_id
            )
        )

        conn.commit()
        conn.close()

        # -----------------------------
        # به‌روزرسانی مدارک
        # -----------------------------

        self.delete_customer_files(
            customer_id
        )

        if files:
            self.save_customer_files(
                customer_id,
                files
            )


    def delete_customer(self, customer_id):

        conn = self.connect()
        cursor = conn.cursor()

        # حذف مدارک مسافر
        cursor.execute(
            "DELETE FROM customer_files WHERE customer_id=?",
            (customer_id,)
        )

        # حذف خود مسافر
        cursor.execute(
            "DELETE FROM customers WHERE id=?",
            (customer_id,)
        )

        conn.commit()
        conn.close()

    def get_customer_files(self, customer_id):

        conn = self.connect()

        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT file_path
            FROM customer_files
            WHERE customer_id=?
            """,
            (customer_id,)
        )

        rows = cursor.fetchall()

        conn.close()

        return [row["file_path"] for row in rows]

    def get_customer_files_data(self, customer_id):

        conn = self.connect()

        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                id,
                file_name,
                file_data
            FROM customer_files
            WHERE customer_id=?
            ORDER BY id
            """,
            (customer_id,)
        )

        rows = cursor.fetchall()

        conn.close()

        return rows

    def customer_has_files(self, customer_id):

        conn = self.connect()

        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT COUNT(*)
            FROM customer_files
            WHERE customer_id=?
            """,
            (customer_id,)
        )

        count = cursor.fetchone()[0]

        conn.close()

        return count > 0

    # -----------------------------
    # دریافت اطلاعات کامل یک مسافر
    # -----------------------------
    def get_customer_by_id(self, customer_id):

        conn = self.connect()

        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT *
            FROM customers
            WHERE id=?
            """,
            (customer_id,)
        )

        customer = cursor.fetchone()

        conn.close()

        return customer

    def search_customers(
            self,
            status,
            full_name,
            phone,
            cottage,
            check_in,
            check_out
    ):

        conn = self.connect()

        cursor = conn.cursor()

        query = """
            SELECT *
            FROM customers
            WHERE 1=1
        """

        params = []

        # ---------------- نام ----------------

        if full_name:
            query += " AND full_name LIKE ?"

            params.append(f"%{full_name}%")

        # ---------------- تلفن ----------------

        if phone:
            query += " AND phone LIKE ?"

            params.append(f"%{phone}%")

        # ---------------- کلبه ----------------

        if cottage and cottage != "همه":
            query += " AND cottage_number = ?"

            params.append(cottage)

        # ---------------- ورود ----------------

        if check_in:
            query += " AND check_in LIKE ?"

            params.append(f"%{check_in}%")

        # ---------------- خروج ----------------

        if check_out:
            query += " AND check_out LIKE ?"

            params.append(f"%{check_out}%")

        cursor.execute(query, params)

        rows = cursor.fetchall()

        conn.close()

        # ---------------- وضعیت ----------------

        if status == "🟢 کامل":

            rows = [
                row for row in rows
                if self.customer_has_files(row["id"])
            ]

        elif status == "🔴 ناقص":

            rows = [
                row for row in rows
                if not self.customer_has_files(row["id"])
            ]

        return rows

    def get_customers_count(self):

        conn = self.connect()

        cursor = conn.cursor()

        cursor.execute(
            "SELECT COUNT(*) FROM customers"
        )

        count = cursor.fetchone()[0]

        conn.close()

        return count

    def merge_backup(self, backup_path):

        backup_conn = sqlite3.connect(
            backup_path
        )

        backup_conn.row_factory = sqlite3.Row

        backup_cursor = backup_conn.cursor()

        current_conn = self.connect()

        current_cursor = current_conn.cursor()

        try:

            # ==================================================
            # دریافت مسافرهای بکاپ
            # ==================================================

            backup_cursor.execute(
                """
                SELECT *
                FROM customers
                """
            )

            backup_customers = (
                backup_cursor.fetchall()
            )

            # ==================================================
            # بررسی ستون‌های customer_files در بکاپ
            # ==================================================

            backup_cursor.execute(
                "PRAGMA table_info(customer_files)"
            )

            backup_file_columns = {
                row["name"]
                for row in backup_cursor.fetchall()
            }

            has_file_name = (
                    "file_name"
                    in backup_file_columns
            )

            has_file_data = (
                    "file_data"
                    in backup_file_columns
            )

            has_file_path = (
                    "file_path"
                    in backup_file_columns
            )

            # ==================================================
            # شمارنده‌ها
            # ==================================================

            added_customers = 0
            added_files = 0

            # ==================================================
            # اضافه کردن مسافرها
            # ==================================================

            for customer in backup_customers:

                # --------------------------------------------------
                # بررسی اینکه ID وجود دارد
                # --------------------------------------------------

                if "id" not in customer.keys():
                    continue

                # --------------------------------------------------
                # بررسی وجود مسافر مشابه
                # --------------------------------------------------

                current_cursor.execute(
                    """
                    SELECT id
                    FROM customers
                    WHERE
                        full_name = ?
                        AND phone = ?
                        AND cottage_number = ?
                        AND check_in = ?
                        AND check_out = ?
                    LIMIT 1
                    """,
                    (
                        customer["full_name"],
                        customer["phone"],
                        customer["cottage_number"],
                        customer["check_in"],
                        customer["check_out"]
                    )
                )

                existing_customer = (
                    current_cursor.fetchone()
                )

                # --------------------------------------------------
                # اگر مسافر از قبل وجود داشت
                # --------------------------------------------------

                if existing_customer is not None:

                    new_customer_id = (
                        existing_customer["id"]
                    )

                # --------------------------------------------------
                # در غیر این صورت مسافر جدید ایجاد کن
                # --------------------------------------------------

                else:

                    current_cursor.execute(
                        """
                        INSERT INTO customers
                        (
                            full_name,
                            phone,
                            cottage_number,
                            check_in,
                            check_out,
                            description,
                            pos_office,
                            pos_cafe,
                            pos_market,
                            cash,
                            card_transfer,
                            card_transfer_receiver
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            customer["full_name"],
                            customer["phone"],
                            customer["cottage_number"],
                            customer["check_in"],
                            customer["check_out"],
                            customer["description"],
                            customer["pos_office"],
                            customer["pos_cafe"],
                            customer["pos_market"],
                            customer["cash"],
                            customer["card_transfer"],
                            customer["card_transfer_receiver"]
                        )
                    )

                    new_customer_id = (
                        current_cursor.lastrowid
                    )

                    added_customers += 1

                # ==================================================
                # دریافت مدارک این مسافر از بکاپ
                # ==================================================

                old_customer_id = customer["id"]

                backup_cursor.execute(
                    """
                    SELECT *
                    FROM customer_files
                    WHERE customer_id = ?
                    ORDER BY id
                    """,
                    (old_customer_id,)
                )

                backup_files = (
                    backup_cursor.fetchall()
                )

                # ==================================================
                # انتقال مدارک
                # ==================================================

                for backup_file in backup_files:

                    # --------------------------------------------------
                    # مقدارهای پیش‌فرض
                    # --------------------------------------------------

                    file_name = ""

                    file_data = None

                    file_path = ""

                    # --------------------------------------------------
                    # نام فایل
                    # --------------------------------------------------

                    if has_file_name:
                        file_name = (
                                backup_file["file_name"]
                                or ""
                        )

                    # --------------------------------------------------
                    # اطلاعات فایل
                    # --------------------------------------------------

                    if has_file_data:
                        file_data = (
                            backup_file["file_data"]
                        )

                    # --------------------------------------------------
                    # مسیر قدیمی
                    # --------------------------------------------------

                    if has_file_path:
                        file_path = (
                                backup_file["file_path"]
                                or ""
                        )

                    # --------------------------------------------------
                    # جلوگیری از مدرک تکراری
                    # --------------------------------------------------

                    if file_data:

                        current_cursor.execute(
                            """
                            SELECT id
                            FROM customer_files
                            WHERE
                                customer_id = ?
                                AND file_name = ?
                                AND file_data = ?
                            LIMIT 1
                            """,
                            (
                                new_customer_id,
                                file_name,
                                file_data
                            )
                        )

                    else:

                        current_cursor.execute(
                            """
                            SELECT id
                            FROM customer_files
                            WHERE
                                customer_id = ?
                                AND file_path = ?
                            LIMIT 1
                            """,
                            (
                                new_customer_id,
                                file_path
                            )
                        )

                    existing_file = (
                        current_cursor.fetchone()
                    )

                    if existing_file is not None:
                        continue

                    # ==================================================
                    # انتقال مدرک دارای BLOB
                    # ==================================================

                    if file_data:

                        current_cursor.execute(
                            """
                            INSERT INTO customer_files
                            (
                                customer_id,
                                file_path,
                                file_name,
                                file_data
                            )
                            VALUES (?, ?, ?, ?)
                            """,
                            (
                                new_customer_id,
                                file_path,
                                file_name,
                                sqlite3.Binary(
                                    bytes(file_data)
                                )
                            )
                        )

                        added_files += 1

                    # ==================================================
                    # انتقال مدرک قدیمی بدون BLOB
                    # ==================================================

                    else:

                        current_cursor.execute(
                            """
                            INSERT INTO customer_files
                            (
                                customer_id,
                                file_path,
                                file_name,
                                file_data
                            )
                            VALUES (?, ?, ?, ?)
                            """,
                            (
                                new_customer_id,
                                file_path,
                                file_name,
                                None
                            )
                        )

                        added_files += 1

            # ==================================================
            # ثبت نهایی
            # ==================================================

            current_conn.commit()

            # ==================================================
            # نتیجه موفقیت
            # ==================================================

            return {
                "success": True,
                "customers": added_customers,
                "files": added_files
            }

        except Exception:

            current_conn.rollback()

            raise

        finally:

            backup_conn.close()

            current_conn.close()


