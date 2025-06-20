import sys
import csv
import requests as req
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QFileDialog, QMainWindow, QApplication, QMessageBox, QLabel, QStatusBar, QTableWidgetItem
from PyQt5.QtCore import  QThread
from PyQt5.QtGui import QColor, QBrush, QPixmap, QIcon
from io import BytesIO
from ui_main_ui import Ui_MainWindow
from get_aqi_api import get_aqi_data
from AQIWorker import AQIWorker
from listCity import get_city_list
from database import DatabaseManager
from desc_UI import MainDesc
from style import btn_styles

def get_aqi_color(aqi, as_hex=False):
    if aqi <= 50: color = QColor("green")
    elif aqi <= 100: color = QColor("yellow")
    elif aqi <= 150: color = QColor("orange")
    elif aqi <= 200: color = QColor("red")
    elif aqi <= 300: color = QColor("purple")
    else: color = QColor("maroon")
    return color.name() if as_hex else color

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self) 

        self.ui.btnSearch.setStyleSheet(btn_styles["btnSearch"])
        self.ui.btnSaveAs.setStyleSheet(btn_styles["btnSaveAs"])
        self.ui.btnDelete.setStyleSheet(btn_styles["btnDelete"])

        self.ui.btnSearch.setIcon(self.load_icon_from_url("https://img.icons8.com/ios-filled/50/search--v1.png"))
        self.ui.btnSaveAs.setIcon(self.load_icon_from_url("https://img.icons8.com/ios-filled/50/save-as.png"))
        self.ui.btnDelete.setIcon(self.load_icon_from_url("https://img.icons8.com/ios-filled/50/delete-forever.png"))

        self.db = DatabaseManager()
        self.db.create_table()

        self.setWindowTitle("AirAware - Aplikasi Pemantauan Kualitas Udara")
        self.setFixedSize(1086, 807)

        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        identitas = QLabel("Nama: Raizul Furkon | NIM: F1D022024")
        identitas.setStyleSheet("font-family: 'Nunito ExtraBold'; font-size: 15px; color: #000000;")
        self.statusBar.addPermanentWidget(identitas)

        self.page_2_loadeded = False
        self.connect_btn()

    def connect_btn(self):
        self.ui.btn_page_1.clicked.connect(self.page_1)
        self.ui.btn_page_2.clicked.connect(self.page_2)
        self.ui.btn_page_3.clicked.connect(self.page_3)
        self.ui.btnSearch.clicked.connect(self.search_city_aqi)
        self.ui.actionExit.triggered.connect(self.closeWindow)
        self.ui.actionRefresh.triggered.connect(self.refresh_program)
        self.ui.btnDelete.clicked.connect(self.delete_selected_history)
        self.ui.actionExport_to_CSV.triggered.connect(self.export_to_csv_via_menu)
        self.ui.actionExport_to_PDF.triggered.connect(self.export_to_pdf_via_menu)
        self.ui.btnSaveAs.clicked.connect(self.save_as)
        self.ui.actionAbout.triggered.connect(self.show_description)

    # button methods
    def page_1(self):
        self.ui.stackedWidget.setCurrentIndex(0)
    def page_2(self):
        self.ui.stackedWidget.setCurrentIndex(1)
        if not self.page_2_loadeded:
            self.load_all_city()
            self.page_2_loadeded = True
    def page_3(self):
        self.ui.stackedWidget.setCurrentIndex(2)
        self.load_history()
    def closeWindow(self):
        reply = QMessageBox.question(
            self,
            "Konfirmasi Keluar",
            "Apakah Anda yakin ingin keluar?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.close()
    def refresh_program(self):
        #page 1
        self.ui.searchBox.clear()
        self.ui.labelPlace.setText("-")
        self.ui.status_aqi.setText("-")
        self.ui.overall_aqi_value.setText("-")
        self.ui.co_cons.setText("-")
        self.ui.co_aqi.setText("-")
        self.ui.no2_cons.setText("-")
        self.ui.no2_aqi.setText("-")
        self.ui.o3_cons.setText("-")
        self.ui.o3_aqi.setText("-")
        self.ui.so_cons.setText("-")
        self.ui.so2_aqi.setText("-")
        self.ui.pm25_cons.setText("-")
        self.ui.pm25_aqi.setText("-")
        self.ui.pm10_cons.setText("-")
        self.ui.pm10_aqi.setText("-")
        #page 2
        self.ui.tableWidget.setRowCount(0)
        self.page_2_loadeded = False
    def show_description(self):
        self.descWindow = MainDesc()
        self.descWindow.show()

    def load_icon_from_url(self, url):
        try:
            response = req.get(url)
            image_data = BytesIO(response.content)
            pixmap = QPixmap()
            pixmap.loadFromData(image_data.read())
            return QIcon(pixmap)
        except Exception as e:
            print("Gagal memuat ikon:", e)
            return QIcon()

    def search_city_aqi(self):
        city = self.ui.searchBox.text()
        if not city:
            QMessageBox.warning(
                self,
                "Input Kosong",
                "Silakan masukkan nama kota terlebih dahulu."
            )
            return

        data = get_aqi_data(city)
        if data:
            self.ui.labelPlace.setText(city.capitalize())
            
            self.ui.co_cons.setText(str(data['CO']['concentration']))
            self.ui.co_aqi.setText(str(data['CO']['aqi']))
            self.ui.co_aqi.setStyleSheet(f"color: {get_aqi_color(data['CO']['aqi'], as_hex=True)}")
            
            self.ui.no2_cons.setText(str(data['NO2']['concentration']))
            self.ui.no2_aqi.setText(str(data['NO2']['aqi']))
            self.ui.no2_aqi.setStyleSheet(f"color: {get_aqi_color(data['NO2']['aqi'], as_hex=True)}")

            self.ui.o3_cons.setText(str(data['O3']['concentration']))
            self.ui.o3_aqi.setText(str(data['O3']['aqi']))
            self.ui.o3_aqi.setStyleSheet(f"color: {get_aqi_color(data['O3']['aqi'], as_hex=True)}")
            
            self.ui.so_cons.setText(str(data['SO2']['concentration']))
            self.ui.so2_aqi.setText(str(data['SO2']['aqi']))
            self.ui.so2_aqi.setStyleSheet(f"color: {get_aqi_color(data['SO2']['aqi'], as_hex=True)}")
            
            self.ui.pm25_cons.setText(str(data['PM2.5']['concentration']))
            self.ui.pm25_aqi.setText(str(data['PM2.5']['aqi']))
            self.ui.pm25_aqi.setStyleSheet(f"color: {get_aqi_color(data['PM2.5']['aqi'], as_hex=True)}")

            self.ui.pm10_cons.setText(str(data['PM10']['concentration']))
            self.ui.pm10_aqi.setText(str(data['PM10']['aqi']))
            self.ui.pm10_aqi.setStyleSheet(f"color: {get_aqi_color(data['PM10']['aqi'], as_hex=True)}")

            overall_aqi = data['overall_aqi']
            self.ui.overall_aqi_value.setText(str(overall_aqi))
            self.ui.overall_aqi_value.setStyleSheet(f"color: {get_aqi_color(overall_aqi, as_hex=True)}")

            if overall_aqi <= 50:
                status = "Good"
            elif overall_aqi <= 100:
                status = "Moderate"
            elif overall_aqi <= 150:
                status = "Unhealthy for Sensitive Groups"
            elif overall_aqi <= 200:
                status = "Unhealthy"
            elif overall_aqi <= 300:
                status = "Very Unhealthy"
            else:
                status = "Hazardous"
            self.ui.status_aqi.setText(status)
            self.ui.status_aqi.setStyleSheet(f"color: {get_aqi_color(overall_aqi, as_hex=True)}")
            self.db.insert_history(city, data)
        else:
            QMessageBox.warning(
                self,
                "Kota Tidak Ditemukan",
                f"Kota '{city}' tidak ditemukan atau tidak tersedia dalam data AQI."
            )
            self.ui.labelPlace.setText("-")
            self.ui.status_aqi.setText("-")
            self.ui.overall_aqi_value.setText("-")
            self.ui.co_cons.setText("-")
            self.ui.co_aqi.setText("-")
            self.ui.no2_cons.setText("-")
            self.ui.no2_aqi.setText("-")
            self.ui.o3_cons.setText("-")
            self.ui.o3_aqi.setText("-")
            self.ui.so_cons.setText("-")
            self.ui.so2_aqi.setText("-")
            self.ui.pm25_cons.setText("-")
            self.ui.pm25_aqi.setText("-")
            self.ui.pm10_cons.setText("-")
            self.ui.pm10_aqi.setText("-")
    
    def load_all_city(self):
        self.city_list = get_city_list()
        self.worker_thread = QThread()
        self.worker = AQIWorker(self.city_list)
        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.started.connect(self.worker.run)
        self.worker.dataFetched.connect(self.add_row_to_table)
        self.worker.finished.connect(self.worker_thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker_thread.finished.connect(self.worker_thread.deleteLater)
        self.worker_thread.start()

    def add_row_to_table(self, city, data):
        row = self.ui.tableWidget.rowCount()
        self.ui.tableWidget.insertRow(row)
       
        def add_item(col, val):
            item = QTableWidgetItem(str(val))
            item.setForeground(QBrush(get_aqi_color(float(val))))
            self.ui.tableWidget.setItem(row, col, item)
        
        self.ui.tableWidget.setItem(row, 0, QTableWidgetItem(city.capitalize()))
        add_item(1, data['CO']['aqi'])
        add_item(2, data['NO2']['aqi'])
        add_item(3, data['O3']['aqi'])
        add_item(4, data['SO2']['aqi'])
        add_item(5, data['PM2.5']['aqi'])
        add_item(6, data['PM10']['aqi'])
        add_item(7, data['overall_aqi'])
    
    def load_history(self):
        rows = self.db.fetch_all_history()
        self.ui.tableHistory.setRowCount(0)

        for row_num, row_data in enumerate(rows):
            self.ui.tableHistory.insertRow(row_num)
            for col_num, col_data in enumerate(row_data):
                item = QTableWidgetItem(str(col_data))

                if 1 <= col_num <= 7:
                    try:
                        aqi_val = float(col_data)
                        item.setForeground(QBrush(get_aqi_color(aqi_val)))
                    except ValueError:
                        pass 

                self.ui.tableHistory.setItem(row_num, col_num, item)

    def delete_selected_history(self):
        selected_row = self.ui.tableHistory.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Tidak Ada Data", "Silakan pilih salah satu data yang ingin dihapus.")
            return

        city_item = self.ui.tableHistory.item(selected_row, 0)
        timestamp_item = self.ui.tableHistory.item(selected_row, 8)  

        if not city_item or not timestamp_item:
            QMessageBox.warning(self, "Data Tidak Lengkap", "Data yang dipilih tidak valid.")
            return

        city = city_item.text()
        timestamp = timestamp_item.text()

        confirm = QMessageBox.question(
            self,
            "Konfirmasi Hapus",
            f"Apakah Anda yakin ingin menghapus data riwayat untuk kota '{city}' pada '{timestamp}'?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            self.db.delete_history(city, timestamp)
            self.ui.tableHistory.removeRow(selected_row)
            QMessageBox.information(self, "Sukses", "Data berhasil dihapus.")

    def export_to_csv(self, path_csv):
        try:
            with open(path_csv, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)

                headers = []
                for i in range(self.ui.tableHistory.columnCount()):
                    header_item = self.ui.tableHistory.horizontalHeaderItem(i)
                    headers.append(header_item.text() if header_item else f"Kolom {i+1}")
                writer.writerow(headers)

                for row in range(self.ui.tableHistory.rowCount()):
                    row_data = []
                    for col in range(self.ui.tableHistory.columnCount()):
                        item = self.ui.tableHistory.item(row, col)
                        row_data.append(item.text() if item else "")
                    writer.writerow(row_data)

            QMessageBox.information(self, "Sukses", f"Data berhasil diekspor ke CSV:\n{path_csv}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal mengekspor CSV:\n{str(e)}")

    def export_to_pdf(self, path_pdf):
        try:
            c = canvas.Canvas(path_pdf, pagesize=A4)
            _, height = A4
            y = height - 50

            headers = []
            for i in range(self.ui.tableHistory.columnCount()):
                item = self.ui.tableHistory.horizontalHeaderItem(i)
                headers.append(item.text() if item else f"Kolom {i+1}")

            x = 40
            for i, header in enumerate(headers):
                c.drawString(x + i * 65, y, header)
            y -= 20

            for row in range(self.ui.tableHistory.rowCount()):
                for col in range(self.ui.tableHistory.columnCount()):
                    item = self.ui.tableHistory.item(row, col)
                    if item:
                        c.drawString(x + col * 65, y, item.text())
                y -= 20
                if y < 50:
                    c.showPage()
                    y = height - 50

            c.save()
            QMessageBox.information(self, "Berhasil", f"Data berhasil diekspor ke PDF.\n{path_pdf}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal mengekspor PDF:\n{str(e)}")

    def save_as(self):
        path, selected_filter = QFileDialog.getSaveFileName(
            self,
            "Simpan Sebagai",
            "",
            "PDF Files (*.pdf);;CSV Files (*.csv)"
        )

        if path:
            if selected_filter == "CSV Files (*.csv)" or path.endswith(".csv"):
                self.export_to_csv(path)
            elif selected_filter == "PDF Files (*.pdf)" or path.endswith(".pdf"):
                self.export_to_pdf(path)
            else:
                QMessageBox.warning(self, "Format Tidak Didukung", "Hanya mendukung file PDF atau CSV.")

    def export_to_csv_via_menu(self):
        path_csv, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Simpan CSV", "", "CSV Files (*.csv)")
        if path_csv:
            self.export_to_csv(path_csv)

    def export_to_pdf_via_menu(self):
        path_pdf, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Simpan PDF", "", "PDF Files (*.pdf)")
        if path_pdf:
            self.export_to_pdf(path_pdf)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec_())