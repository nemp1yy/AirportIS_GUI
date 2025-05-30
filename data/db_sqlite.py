import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
import random


class create_db:
    def __init__(self):
        super().__init__()
        self.db_path = Path('data/airport.db')
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        db_exists = self.db_path.exists()

        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

        if not db_exists:
            print("База данных не была найдена.")
            print("\nСоздаем новую...")

            self.create_tables()
            self.create_main_table()
            self.add_demonstration_data()
            self.add_bulk_data()  # Добавляем массовые данные вместо тестового рейса
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
        # Расширенные данные для справочных таблиц
        self.cursor.executescript("""
        INSERT INTO airlines (name, country) VALUES
        ('Аэрофлот', 'Россия'),
        ('S7 Airlines', 'Россия'),
        ('Уральские авиалинии', 'Россия'),
        ('Победа', 'Россия'),
        ('Turkish Airlines', 'Турция'),
        ('Lufthansa', 'Германия'),
        ('Emirates', 'ОАЭ'),
        ('Qatar Airways', 'Катар'),
        ('Air France', 'Франция'),
        ('British Airways', 'Великобритания'),
        ('Singapore Airlines', 'Сингапур'),
        ('Cathay Pacific', 'Гонконг'),
        ('Japan Airlines', 'Япония'),
        ('Korean Air', 'Южная Корея'),
        ('Air China', 'Китай');

        INSERT INTO aircraft_types (model, manufacturer, capacity) VALUES
        ('А320', 'Airbus', 180),
        ('А321', 'Airbus', 220),
        ('А350', 'Airbus', 350),
        ('B737', 'Boeing', 160),
        ('B747', 'Boeing', 410),
        ('B777', 'Boeing', 396),
        ('B787', 'Boeing', 290),
        ('SSJ-100', 'Sukhoi', 98),
        ('МС-21', 'Иркут', 211),
        ('Ил-96', 'Ильюшин', 300),
        ('Embraer 190', 'Embraer', 114),
        ('CRJ-200', 'Bombardier', 50);

        INSERT INTO airports (name, city, country, code) VALUES
        ('Шереметьево', 'Москва', 'Россия', 'SVO'),
        ('Домодедово', 'Москва', 'Россия', 'DME'),
        ('Пулково', 'Санкт-Петербург', 'Россия', 'LED'),
        ('Кольцово', 'Екатеринбург', 'Россия', 'SVX'),
        ('Толмачёво', 'Новосибирск', 'Россия', 'OVB'),
        ('Сочи', 'Сочи', 'Россия', 'AER'),
        ('Внуково', 'Москва', 'Россия', 'VKO'),
        ('Хитроу', 'Лондон', 'Великобритания', 'LHR'),
        ('Шарль де Голль', 'Париж', 'Франция', 'CDG'),
        ('Франкфурт', 'Франкфурт-на-Майне', 'Германия', 'FRA'),
        ('Дубай', 'Дубай', 'ОАЭ', 'DXB'),
        ('Ататюрк', 'Стамбул', 'Турция', 'IST'),
        ('Джон Кеннеди', 'Нью-Йорк', 'США', 'JFK'),
        ('Пекин Столичный', 'Пекин', 'Китай', 'PEK'),
        ('Ханэда', 'Токио', 'Япония', 'HND'),
        ('Инчхон', 'Сеул', 'Южная Корея', 'ICN'),
        ('Чанги', 'Сингапур', 'Сингапур', 'SIN'),
        ('Кингсфорд Смит', 'Сидней', 'Австралия', 'SYD');

        INSERT INTO statuses (name) VALUES
        ('По расписанию'),
        ('Задержан'),
        ('Отменён'),
        ('Вылетел'),
        ('Приземлился'),
        ('Регистрация'),
        ('Посадка'),
        ('Завершён');
        """)

    def add_bulk_data(self):
        # Генерация 50 случайных рейсов
        base_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

        for i in range(1, 51):
            flight_number = f"{random.choice(['SU', 'S7', 'U6', 'DP', 'TK', 'LH', 'EK', 'QR', 'AF', 'BA'])}{random.randint(100, 999)}"
            airline_id = random.randint(1, 15)
            aircraft_type_id = random.randint(1, 12)

            # Гарантируем, что аэропорты отправления и назначения разные
            departure_airport, arrival_airport = random.sample(range(1, 18), 2)

            # Время отправления - случайное в течение 30 дней
            departure_time = base_date + timedelta(days=random.randint(0, 30),
                                                   hours=random.randint(0, 23),
                                                   minutes=random.choice([0, 15, 30, 45]))

            # Время прибытия - через 1-12 часов после отправления
            flight_duration = timedelta(hours=random.randint(1, 12))
            arrival_time = departure_time + flight_duration

            status_id = random.randint(1, 8)
            gate = f"{random.choice(['A', 'B', 'C', 'D', 'E'])}{random.randint(1, 50)}"

            self.cursor.execute("""
            INSERT INTO flights (
                flight_number, airline_id, aircraft_type_id,
                departure_airport_id, arrival_airport_id,
                departure_time, arrival_time, status_id, gate
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                flight_number, airline_id, aircraft_type_id,
                departure_airport, arrival_airport,
                departure_time.strftime('%Y-%m-%d %H:%M'),
                arrival_time.strftime('%Y-%m-%d %H:%M'),
                status_id, gate
            ))

        print("Добавлено 50 случайных рейсов в базу данных")