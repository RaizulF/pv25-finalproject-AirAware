import sqlite3
DB_NAME = "aqi_data.db"

class DatabaseManager:
    def __init__(self):
        self.conn = sqlite3.connect(DB_NAME)
    
    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                city TEXT,
                co REAL,
                no2 REAL,
                o3 REAL,
                so2 REAL,
                pm25 REAL,
                pm10 REAL,
                overall_aqi INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.commit()
    
    def insert_history(self, city, data):
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO history (city, co, no2, o3, so2, pm25, pm10, overall_aqi)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            city,
            data["CO"]["aqi"],
            data["NO2"]["aqi"],
            data["O3"]["aqi"],
            data["SO2"]["aqi"],
            data["PM2.5"]["aqi"],
            data["PM10"]["aqi"],
            data["overall_aqi"]
        ))
        self.conn.commit()

    def fetch_all_history(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT city, co, no2, o3, so2, pm25, pm10, overall_aqi, timestamp
            FROM history
            ORDER BY id DESC
        """)
        return cursor.fetchall()

    def close(self):
        self.conn.close()

    def delete_history(self, city, timestamp):
        self.conn.execute("DELETE FROM history WHERE city = ? AND timestamp = ?", (city, timestamp))
        self.conn.commit()
