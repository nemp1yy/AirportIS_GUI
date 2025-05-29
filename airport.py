import os
from datetime import datetime
from utils import gotoxy

class dataAirport:
    def __init__(self):
        self.id = 0
        self.departure_time = "n/a"
        self.arrival_time = "n/a"
        self.airport_Status = ["По расписанию", "Задержан", "Отменен"]
        self.status = self.airport_Status[0]
        self.aircraft_type = "n/a"
        self.airline = "n/a"
        self.flight = "n/a"
        self.departure_from = "n/a"
        self.destination = "n/a"
        self.gate = "n/a"

    def input(self, count : int):
        gotoxy(0, 5 + count); print("| ", end = ""); self.flight = input()
        gotoxy(9, 5 + count); print("| ", end = ""); self.airline = input()
        gotoxy(31, 5 + count); print("| ", end = ""); self.departure_from = input()
        gotoxy(50, 5 + count); print("| ", end = ""); self.destination = input()
        gotoxy(70, 5 + count); print("| ", end = ""); self.departure_time = input()
        gotoxy(90, 5 + count); print("| ", end = ""); self.arrival_time = input()
        gotoxy(110, 5 + count); print("| ", end = ""); self.gate = input()

        gotoxy(1, 10 + count)
        var = int(input("""
        Статус:
         1. По расписанию
         2. Задержан
         3. Отменен
         
        Ваш вариант: """))
        self.status = self.airport_Status[var - 1]

        gotoxy(117, 4 + count); print(f"| {self.status} ")
        gotoxy(134, 4 + count); print("| ", end = ""); self.aircraft_type = input();
    
    
    def output(self):
        print(f"| {self.flight:7} | {self.airline:20} | {self.departure_from:17} | {self.destination:18} | {self.departure_time:18} | {self.arrival_time:18} | {self.gate:5} | {self.status:15} | {self.aircraft_type:15} |")

    def getId(self): return int(self.id)
    def getFlight(self): return self.flight
    def getAirline(self): return self.Airline
    def getDeparture_from(self): return self.departure_from
    def getDestination(self): return self.destination
    def getDeparture_time(self): return self.departure_time
    def getArrival_time(self): return self.arrival_time
    def getGate(self): return self.gate
    def getStatus(self): return self.status
    def getAircraft_type(self): return self.aircraft_type

    def setId(self, id : int): self.id = id
    def setFlight(self, flight: str): self.flight = flight
    def setAirline(self, airline: str): self.airline = airline
    def setDeparture_from(self, departure_from : str): self.departure_from = departure_from
    def setDestination(self, destination : str): self.destination = destination
    def setDeparture_time(self, departure_time : datetime): self.departure_time = departure_time
    def setArrival_time(self, arrival_time : datetime): self.arrival_time = arrival_time
    def setGate(self, gate : str): self.gate = gate
    def setStatus(self, status : str): self.status = status
    def setAircraft_type(self, aircraft_type: str): self.aircraft_type = aircraft_type