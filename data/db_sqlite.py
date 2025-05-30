import sqlite3
from pathlib import Path

class create_db:
    def __init__(self):
        self.db_path = Path('data.db')
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        db_exists = self.db_path.exists()

        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

        if not db_exists:
            print("База данных не была найдена. ")
            print("\n\nСоздаем новую...");

            self.create_tables()
            self.add_demonstration_data()
            self.add_test_flight()
            self.conn.commit()
            self.conn.close()

            print("База данных успешно создана.")
        else:
            print("База данных была успешно загружена")


        def create_tables(self):
            # Создание справочных таблиц
            self.cursor.executescript("""
            CREATE TABLE airlines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                country TEXT
            );
        
        
            CREATE TABLE aircraft_types (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model TEXT NOT NULL UNIQUE,
                manufacturer TEXT,
                capacity INTEGER
            );
            
            CREATE TABLE airports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                city TEXT,
                country TEXT,
                code TEXT UNIQUE
            );
            
            CREATE TABLE statuses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            );
            """)

# Создание основной таблицы

        def create_main_table(self):
            self.cursor.execute("""
            CREATE TABLE flights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                flight_number TEXT NOT NULL,
                airline_id INTEGER,
                aircraft_type_id INTEGER,
                departure_airport_id INTEGER,
                arrival_airport_id INTEGER,
                departure_time DATETIME,
                arrival_time DATETIME,
                status_id INTEGER,
                gate TEXT,
                FOREIGN KEY (airline_id) REFERENCES airlines(id),
                FOREIGN KEY (aircraft_type_id) REFERENCES aircraft_types(id),
                FOREIGN KEY (departure_airport_id) REFERENCES airports(id),
                FOREIGN KEY (arrival_airport_id) REFERENCES airports(id),
                FOREIGN KEY (status_id) REFERENCES statuses(id)
            );
            """)


        def add_demonstration_data(self):
            # Вставка демонстрационных данных
            self.cursor.executescript("""
            INSERT INTO airlines (name, country) VALUES
            ('Aeroflot', 'Russia'),
            ('Lufthansa', 'Germany');
            
            INSERT INTO aircraft_types (model, manufacturer, capacity) VALUES
            ('A320', 'Airbus', 180),
            ('B737', 'Boeing', 160);
            
            INSERT INTO airports (name, city, country, code) VALUES
            ('Sheremetyevo International Airport', 'Moscow', 'Russia', 'SVO'),
            ('Frankfurt Airport', 'Frankfurt', 'Germany', 'FRA');
            
            INSERT INTO statuses (name) VALUES
            ('On Time'),
            ('Delayed'),
            ('Cancelled');
            """)

            # Вставка тестового рейса

        def add_test_flight(self):
            self.cursor.execute("""
            INSERT INTO flights (
                flight_number, airline_id, aircraft_type_id,
                departure_airport_id, arrival_airport_id,
                departure_time, arrival_time, status_id, gate
            )
            VALUES (
                'SU123', 1, 1, 1, 2,
                '2025-06-01 08:00', '2025-06-01 11:00', 1, 'A12'
            );
            """)


