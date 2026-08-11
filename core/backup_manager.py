import shutil
import json
from core.date_utils import DateUtils
from pathlib import Path
from datetime import datetime
from core.settings_manager import SettingsManager

class BackupManager:

    def __init__(self):
        from database import DatabaseManager

        self.database_manager = DatabaseManager()

        self.database = self.database_manager.db_path

        self.settings = SettingsManager()

        self.backup_folder = Path(
            self.settings.get_backup_folder()
        )

        self.backup_folder.mkdir(
            parents=True,
            exist_ok=True
        )


    def create_backup(self):
        now = datetime.now()

        shamsi_date = DateUtils.today()

        current_time = now.strftime("%H:%M:%S")

        filename = now.strftime(
            "VIVO_Backup_%Y-%m-%d_%H-%M-%S.db"
        )

        destination = self.backup_folder / filename

        shutil.copy2(
            self.database,
            destination
        )

        info = {

            "date": shamsi_date,

            "time": current_time,

            "file": filename

        }

        with open(
                self.backup_folder / "last_backup.json",
                "w",
                encoding="utf-8"
        ) as f:
            json.dump(
                info,
                f,
                ensure_ascii=False,
                indent=4
            )

        return destination