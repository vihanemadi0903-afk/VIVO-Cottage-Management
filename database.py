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


    def save_customer_files(
            self,
            customer_id,
            files
    ):
        conn = self.connect()

        cursor = conn.cursor()

        for file in files:
            cursor.execute(
                """
                INSERT INTO customer_files
                (
                    customer_id,
                    file_path
                )
                VALUES(?,?)
                """,
                (
                    customer_id,
                    file
                )
            )

        conn.commit()

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
        """
        اطلاعات یک دیتابیس بکاپ را به دیتابیس فعلی VIVO اضافه می‌کند.

        نکات مهم:
        - اطلاعات فعلی حذف نمی‌شوند.
        - IDهای دیتابیس بکاپ مستقیماً وارد دیتابیس فعلی نمی‌شوند.
        - اطلاعات پرداخت نیز منتقل می‌شوند.
        - مدارک هر مسافر با customer_id جدید منتقل می‌شوند.
        - در صورت خطا، تغییرات این عملیات Rollback می‌شوند.
        - بکاپ قدیمی‌تر که بعضی ستون‌های جدید را نداشته باشد،
          تا حد ممکن با مقدار پیش‌فرض سازگار می‌شود.
        """

        backup_path = Path(backup_path)

        if not backup_path.exists():
            raise FileNotFoundError(
                "فایل بکاپ پیدا نشد."
            )

        if backup_path.suffix.lower() != ".db":
            raise ValueError(
                "فایل انتخاب شده یک دیتابیس SQLite معتبر نیست."
            )

        # -------------------------------------------------
        # اتصال به دیتابیس بکاپ
        # -------------------------------------------------

        backup_conn = None
        current_conn = None

        try:

            backup_conn = sqlite3.connect(
                str(backup_path)
            )

            backup_conn.row_factory = sqlite3.Row

            backup_cursor = backup_conn.cursor()

            # -------------------------------------------------
            # بررسی وجود جدول customers
            # -------------------------------------------------

            backup_cursor.execute(
                """
                SELECT name
                FROM sqlite_master
                WHERE type='table'
                AND name='customers'
                """
            )

            if backup_cursor.fetchone() is None:
                raise ValueError(
                    "فایل انتخاب شده دیتابیس VIVO معتبر نیست."
                )

            # -------------------------------------------------
            # بررسی وجود جدول مدارک
            # -------------------------------------------------

            backup_cursor.execute(
                """
                SELECT name
                FROM sqlite_master
                WHERE type='table'
                AND name='customer_files'
                """
            )

            has_files_table = (
                    backup_cursor.fetchone()
                    is not None
            )

            # -------------------------------------------------
            # دریافت ستون‌های موجود در بکاپ
            # -------------------------------------------------

            backup_cursor.execute(
                "PRAGMA table_info(customers)"
            )

            backup_columns = {
                row["name"]
                for row in backup_cursor.fetchall()
            }

            # -------------------------------------------------
            # اتصال به دیتابیس فعلی
            # -------------------------------------------------

            current_conn = self.connect()

            current_cursor = current_conn.cursor()

            # -------------------------------------------------
            # بررسی جدول فعلی
            # -------------------------------------------------

            current_cursor.execute(
                """
                SELECT name
                FROM sqlite_master
                WHERE type='table'
                AND name='customers'
                """
            )

            if current_cursor.fetchone() is None:
                raise ValueError(
                    "جدول customers در دیتابیس فعلی وجود ندارد."
                )

            # -------------------------------------------------
            # ستون‌های دیتابیس فعلی
            # -------------------------------------------------

            current_cursor.execute(
                "PRAGMA table_info(customers)"
            )

            current_columns = [
                row["name"]
                for row in current_cursor.fetchall()
            ]

            # -------------------------------------------------
            # ستون‌هایی که واقعاً می‌توانیم منتقل کنیم
            # -------------------------------------------------

            excluded_columns = {
                "id"
            }

            columns_to_copy = [
                column
                for column in current_columns
                if column not in excluded_columns
                   and column in backup_columns
            ]

            if not columns_to_copy:
                raise ValueError(
                    "هیچ اطلاعات قابل انتقالی از بکاپ پیدا نشد."
                )

            # -------------------------------------------------
            # دریافت تمام مسافرهای بکاپ
            # -------------------------------------------------

            backup_cursor.execute(
                """
                SELECT *
                FROM customers
                ORDER BY id
                """
            )

            customers = backup_cursor.fetchall()

            imported_customers = 0
            imported_files = 0

            # -------------------------------------------------
            # انتقال مسافرها
            # -------------------------------------------------

            for customer in customers:

                values = []

                for column in columns_to_copy:

                    value = customer[column]

                    # اگر بعضی ستون‌های جدید در بکاپ قدیمی
                    # مقدار NULL داشته باشند
                    if value is None:

                        if column in {
                            "pos_office",
                            "pos_cafe",
                            "pos_market",
                            "cash",
                            "card_transfer"
                        }:
                            value = 0

                        elif column in {
                            "full_name",
                            "phone",
                            "cottage_number",
                            "check_in",
                            "check_in_value",
                            "check_out",
                            "check_out_value",
                            "description",
                            "card_transfer_receiver"
                        }:
                            value = ""

                    values.append(value)

                placeholders = ", ".join(
                    ["?"] * len(columns_to_copy)
                )

                columns_sql = ", ".join(
                    f'"{column}"'
                    for column in columns_to_copy
                )

                current_cursor.execute(
                    f"""
                    INSERT INTO customers
                    ({columns_sql})
                    VALUES ({placeholders})
                    """,
                    values
                )

                # ID جدید مسافر در دیتابیس فعلی
                new_customer_id = (
                    current_cursor.lastrowid
                )

                imported_customers += 1

                # -------------------------------------------------
                # انتقال مدارک همین مسافر
                # -------------------------------------------------

                if (
                        has_files_table
                        and "id" in backup_columns
                ):

                    backup_customer_id = customer["id"]

                    backup_cursor.execute(
                        """
                        SELECT file_path
                        FROM customer_files
                        WHERE customer_id=?
                        """,
                        (
                            backup_customer_id,
                        )
                    )

                    files = backup_cursor.fetchall()

                    for file_row in files:

                        file_path = file_row["file_path"]

                        if not file_path:
                            continue

                        # اطمینان از وجود جدول فعلی مدارک
                        current_cursor.execute(
                            """
                            INSERT INTO customer_files
                            (
                                customer_id,
                                file_path
                            )
                            VALUES (?, ?)
                            """,
                            (
                                new_customer_id,
                                file_path
                            )
                        )

                        imported_files += 1

            # -------------------------------------------------
            # ثبت نهایی
            # -------------------------------------------------

            current_conn.commit()

            return {
                "customers": imported_customers,
                "files": imported_files
            }

        except sqlite3.DatabaseError as e:

            if current_conn is not None:
                current_conn.rollback()

            raise ValueError(
                f"خطا در خواندن یا ادغام دیتابیس بکاپ:\n{e}"
            )

        except Exception:

            if current_conn is not None:
                current_conn.rollback()

            raise

        finally:

            if backup_conn is not None:
                backup_conn.close()

            if current_conn is not None:
                current_conn.close()


