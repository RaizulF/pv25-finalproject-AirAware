from get_aqi_api import get_aqi_data
from PyQt5.QtCore import QObject, QThread, pyqtSignal

# Contoh pemakaian di class AQIWorker:
class AQIWorker(QObject):
    dataFetched = pyqtSignal(str, dict)
    finished = pyqtSignal()

    def __init__(self, city_list):
        super().__init__()
        self.city_list = city_list

    def run(self):
        for city in self.city_list:
            data = get_aqi_data(city)  # <- memanggil fungsi dari utils.py
            if data:
                self.dataFetched.emit(city, data)
        self.finished.emit()
