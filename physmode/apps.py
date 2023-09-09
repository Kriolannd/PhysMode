from django.apps import AppConfig
from django_eventstream import send_event
import os

from physmode.modelling.modelling_process import ModellingProcess


class PhysmodeConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "physmode"

    mp = None

    def ready(self):
        self.mp = ModellingProcess.build_from_file(f"{os.path.dirname(__file__)}/modelling/F3.txt")

        def log_values(values):
            with open(f"{os.path.dirname(__file__)}/modelling/F4.txt", "a") as log:
                log.write(str(values) + "\n")

        # mp.add_callback(log_values)
        self.mp.add_callback(print)
        self.mp.add_callback(lambda res: send_event("test", "message", res))

        self.mp.start()
