from database import DatabaseManager


class CustomerController:

    def __init__(self):
        self.db = DatabaseManager()

    # -----------------------------
    # ثبت مسافر
    # -----------------------------
    def add_customer(self, data):

        customer_id = self.db.add_customer(
            full_name=data["name"],
            phone=data["phone"],
            cottage=data["cottage"],
            check_in=data["entry"],
            check_out=data["exit"],
            description=data["description"],

            # اطلاعات پرداخت
            pos_office=data["pos_office"],
            pos_cafe=data["pos_cafe"],
            pos_market=data["pos_market"],
            cash=data["cash"],
            card_transfer=data["card_transfer"],
            card_transfer_receiver=data["card_transfer_receiver"]
        )

        if data["files"]:
            self.db.save_customer_files(
                customer_id,
                data["files"]
            )

        return customer_id

    # -----------------------------
    # دریافت همه مسافرها
    # -----------------------------
    def get_customers(self):
        return self.db.get_all_customers()

    # -----------------------------
    # جستجوی مسافر
    # -----------------------------
    def search_customers(
            self,
            status,
            full_name,
            phone,
            cottage,
            check_in,
            check_out
    ):

        return self.db.search_customers(
            status,
            full_name,
            phone,
            cottage,
            check_in,
            check_out
        )

    # -----------------------------
    # ویرایش مسافر
    # -----------------------------
    def update_customer(self, customer_id, data):

        self.db.update_customer(

            customer_id,

            data["name"],
            data["phone"],
            data["cottage"],
            data["entry"],
            data["exit"],
            data["description"],
            data["files"],

            # اطلاعات پرداخت
            data["pos_office"],
            data["pos_cafe"],
            data["pos_market"],
            data["cash"],
            data["card_transfer"],
            data["card_transfer_receiver"]
        )

    # -----------------------------
    # حذف مسافر
    # -----------------------------
    def delete_customer(self, customer_id):
        self.db.delete_customer(customer_id)

    # -----------------------------
    # دریافت مدارک مسافر
    # -----------------------------
    def get_customer_files(self, customer_id):
        return self.db.get_customer_files(customer_id)

    # -----------------------------
    # آیا مسافر مدرک دارد؟
    # -----------------------------
    def customer_has_files(self, customer_id):
        return self.db.customer_has_files(customer_id)

    # -----------------------------
    # تعداد مدارک مسافر
    # -----------------------------
    def get_files_count(self, customer_id):
        return len(self.db.get_customer_files(customer_id))

    # -----------------------------
    # وضعیت همه کلبه‌ها
    # -----------------------------
    def get_cottages_status(self):

        from core.date_utils import DateUtils

        customers = self.db.get_all_customers()

        cottages = {}

        # ابتدا همه کلبه‌ها را خالی فرض می‌کنیم
        for i in range(1, 17):
            cottages[str(i)] = {

                "occupied": False,

                "name": "",

                "check_out": ""

            }

        # تاریخ امروز
        today = DateUtils.today()

        for customer in customers:

            cottage = str(
                customer["cottage_number"] or ""
            )

            if cottage not in cottages:
                continue

            check_in = customer["check_in"] or ""
            check_out = customer["check_out"] or ""

            # اگر تاریخ‌ها ناقص باشند، رد می‌شود
            if not check_in or not check_out:
                continue

            # -------------------------------------------------
            # منطق رزرو
            #
            # روز ورود        = رزرو شده
            # بین ورود و خروج = رزرو شده
            # روز خروج        = آزاد
            #
            # یعنی:
            #
            # check_in <= today < check_out
            # -------------------------------------------------

            if (
                    DateUtils.compare(
                        today,
                        check_in
                    ) >= 0
                    and
                    DateUtils.compare(
                        today,
                        check_out
                    ) < 0
            ):
                cottages[cottage] = {

                    "occupied": True,

                    "name": (
                            customer["full_name"] or ""
                    ),

                    "check_out": check_out

                }

        return cottages

    # -----------------------------
    # دریافت اطلاعات کامل یک مسافر
    # -----------------------------
    def get_customer(self, customer_id):

        row = self.db.get_customer_by_id(customer_id)

        if row is None:
            return None

        customer = dict(row)

        customer["files"] = self.db.get_customer_files(customer_id)

        return customer

    # -----------------------------
    # وضعیت کلبه‌ها برای یک بازه
    # -----------------------------
    def get_cottages_status_for_period(
            self,
            new_check_in,
            new_check_out,
            ignore_customer_id=None
    ):

        from core.date_utils import DateUtils

        customers = self.db.get_all_customers()

        cottages = {}

        # ابتدا همه کلبه‌ها آزاد هستند
        for i in range(1, 17):
            cottages[str(i)] = {
                "occupied": False,
                "name": "",
                "check_in": "",
                "check_out": ""
            }

        for customer in customers:

            # -------------------------------------------------
            # اگر در حالت تغییر هستیم، مسافر فعلی را نادیده بگیر
            # -------------------------------------------------

            if (
                    ignore_customer_id is not None
                    and
                    customer["id"] == ignore_customer_id
            ):
                continue

            cottage = str(
                customer["cottage_number"] or ""
            )

            if cottage not in cottages:
                continue

            existing_check_in = (
                    customer["check_in"] or ""
            )

            existing_check_out = (
                    customer["check_out"] or ""
            )

            if (
                    not existing_check_in
                    or
                    not existing_check_out
            ):
                continue

            # -------------------------------------------------
            # بررسی تداخل دو بازه
            # -------------------------------------------------

            no_overlap = (
                    DateUtils.compare(
                        existing_check_out,
                        new_check_in
                    ) <= 0
                    or
                    DateUtils.compare(
                        existing_check_in,
                        new_check_out
                    ) >= 0
            )

            # -------------------------------------------------
            # اگر تداخل وجود داشته باشد
            # -------------------------------------------------

            if not no_overlap:
                cottages[cottage] = {

                    "occupied": True,

                    "name": (
                            customer["full_name"] or ""
                    ),

                    "check_in": existing_check_in,

                    "check_out": existing_check_out
                }

        return cottages

    def get_customers_count(self):

        return self.db.get_customers_count()
