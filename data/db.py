import sqlite3
from pathlib import Path
from airport import dataAirport as airp
from utils import table_header as header
from utils import table_footer as footer
from utils import table_header_withID as headerID
from utils import gotoxy
from utils import pause
from typing import List, Optional
from time import sleep
import sqlite3
import random
from datetime import datetime, timedelta



class airportDB:
    def __init__(self):
        self.db_path = Path('data/data.db')
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        db_exists = self.db_path.exists()

        self.conn = sqlite3.connect(self.db_path)
        self.create_tables()
        # Create tables if the database did not exist




conn = sqlite3.connect("data/data.db")
cursor = conn.cursor()

# Удаление таблиц, если они уже существуют
cursor.executescript("""
DROP TABLE IF EXISTS flights;
DROP TABLE IF EXISTS aircrafts;
DROP TABLE IF EXISTS airlines;
""")

# Создание таблиц с расширенными связями
cursor.executescript("""
CREATE TABLE IF NOT EXISTS airlines (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS aircrafts (
    id INTEGER PRIMARY KEY,
    type TEXT NOT NULL,
    airline_id INTEGER NOT NULL,
    FOREIGN KEY (airline_id) REFERENCES airlines(id)
);

CREATE TABLE IF NOT EXISTS flights (
    id INTEGER PRIMARY KEY,
    departure_time DATETIME NOT NULL,
    arrival_time DATETIME NOT NULL,
    status TEXT NOT NULL,
    aircraft_id INTEGER NOT NULL,
    flight TEXT NOT NULL,
    departure_from TEXT NOT NULL,
    destination TEXT NOT NULL,
    gate TEXT NOT NULL,
    FOREIGN KEY (aircraft_id) REFERENCES aircrafts(id)
);
""")

# Данные для авиакомпаний и типов самолетов
airlines = ["Aeroflot", "Lufthansa", "Delta", "Emirates", "Qatar Airways"]
aircraft_types = ["Airbus A320", "Boeing 737", "Boeing 777", "Airbus A380", "Embraer E190"]

# Вставка авиакомпаний
for name in airlines:
    cursor.execute("INSERT INTO airlines (name) VALUES (?)", (name,))
conn.commit()

# Получение ID авиакомпаний
cursor.execute("SELECT id, name FROM airlines")
airlines_data = cursor.fetchall()

# Вставка самолетов (по 2 на каждую авиакомпанию)
aircrafts_data = []
for airline_id, name in airlines_data:
    for i in range(2):
        aircraft_type = random.choice(aircraft_types)
        cursor.execute("INSERT INTO aircrafts (type, airline_id) VALUES (?, ?)", (aircraft_type, airline_id))

conn.commit()

# Получение ID самолетов
cursor.execute("SELECT id FROM aircrafts")
aircraft_ids = [row[0] for row in cursor.fetchall()]

# Генерация 50 записей рейсов
statuses = ["Scheduled", "Delayed", "Cancelled", "Departed", "Arrived"]
airports = ["SVO", "JFK", "LHR", "DXB", "DOH", "FRA", "LAX", "HND", "CDG", "SIN"]
now = datetime.now()

for i in range(50):
    sqlite3.register_adapter(datetime, lambda dt: dt.isoformat())
    sqlite3.register_converter("timestamp", lambda  s: datetime.isoformat(s.decode()))
    departure_time = now + timedelta(hours=random.randint(1, 100))
    arrival_time = departure_time + timedelta(hours=random.randint(2, 10))
    status = random.choice(statuses)
    aircraft_id = random.choice(aircraft_ids)
    flight = f"FL{random.randint(1000, 9999)}"
    departure_from = random.choice(airports)
    destination = random.choice([a for a in airports if a != departure_from])
    gate = f"{random.choice('ABCDEF')}{random.randint(1, 30)}"
    cursor.execute("""
        INSERT INTO flights (departure_time, arrival_time, status, aircraft_id, flight, departure_from, destination, gate)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (departure_time, arrival_time, status, aircraft_id, flight, departure_from, destination, gate))

conn.commit()
conn.close()


