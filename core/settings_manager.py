from pathlib import Path
import json
import sys


class SettingsManager:

    def __init__(self):

        import os

        app_data = os.environ.get("LOCALAPPDATA")

        if not app_data:
            app_data = str(
                Path.home() / "AppData" / "Local"
            )

        self.data_folder = (
                Path(app_data) / "VIVO"
        )

        self.data_folder.mkdir(
            parents=True,
            exist_ok=True
        )

        self.settings_file = (
                self.data_folder / "settings.json"
        )

        self.default_backup = str(
            self.data_folder / "Backups"
        )

        self.load()


    # --------------------------

    def load(self):

        if not self.settings_file.exists():

            self.settings = {
                "backup_folder": self.default_backup
            }

            self.save()

            return

        try:

            with open(
                self.settings_file,
                "r",
                encoding="utf-8"
            ) as f:

                self.settings = json.load(f)

        except Exception:

            self.settings = {
                "backup_folder": self.default_backup
            }

            self.save()

    # --------------------------

    def save(self):

        self.data_folder.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(
            self.settings_file,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                self.settings,
                f,
                ensure_ascii=False,
                indent=4
            )

    # --------------------------

    def get_backup_folder(self):

        return self.settings.get(
            "backup_folder",
            self.default_backup
        )

    # --------------------------

    def set_backup_folder(self, folder):

        folder = Path(folder)

        folder.mkdir(
            parents=True,
            exist_ok=True
        )

        self.settings["backup_folder"] = str(
            folder
        )

        self.save()