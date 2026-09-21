import random
import time

class Passenger:
    def __init__(self, name, age, phone):
        self.name, self.age, self.phone = name, age, phone

class Train:
    def __init__(self):
        self.seats = {
            "Sleeper": {i: "Available" for i in range(1, 6)},
            "AC 3-Tier": {i: "Available" for i in range(1, 4)},
            "AC 2-Tier": {i: "Available" for i in range(1, 3)},
            "First Class": {1: "Available"}
        }

    def available_seat(self, cls):
        for s in self.seats[cls]:
            if self.seats[cls][s] == "Available":
                return s
        return None

class Ticket:
    def __init__(self, pnr, passenger, cls, seat, fare, status="Confirmed"):
        self.pnr, self.passenger = pnr, passenger
        self.cls, self.seat, self.fare = cls, seat, fare
        self.status, self.book_time = status, time.time()

class ReservationSystem:
    def __init__(self):
        self.train = Train()
        self.passengers, self.tickets = [], {}
        self.waiting, self.cancelled = [], []
        self.load()

    def generate_pnr(self):
        while True:
            p = random.randint(10000, 99999)
            if p not in self.tickets:
                return p

    def calculate_fare(self, cls, age):
        fare = {"Sleeper":500, "AC 3-Tier":900,
                "AC 2-Tier":1300, "First Class":2000}[cls]
        if age < 12:
            fare *= .5
        elif age >= 60:
            fare *= .8
        return fare

    def duplicate(self, name, phone):
        for t in list(self.tickets.values()) + self.waiting:
            if t.passenger.name.lower() == name.lower() and t.passenger.phone == phone:
                return True
        return False

    def book(self):
        print("\n--- BOOK TICKET ---")
        name = input("Name: ")
        try:
            age = int(input("Age: "))
            if age <= 0: raise ValueError
        except ValueError:
            print("Invalid age"); return
        phone = input("Phone: ")

        if self.duplicate(name, phone):
            print("Duplicate active booking!"); return

        print("1.Sleeper 2.AC 3-Tier 3.AC 2-Tier 4.First Class")
        classes = {"1":"Sleeper", "2":"AC 3-Tier",
                   "3":"AC 2-Tier", "4":"First Class"}
        ch = input("Class: ")
        if ch not in classes:
            print("Invalid class"); return

        cls = classes[ch]
        p = Passenger(name, age, phone)
        seat = self.train.available_seat(cls)
        status = "Confirmed" if seat else "Waiting"
        t = Ticket(self.generate_pnr(), p, cls, seat or 0,
                   self.calculate_fare(cls, age), status)

        self.passengers.append(p)
        if seat:
            self.train.seats[cls][seat] = "Occupied"
            self.tickets[t.pnr] = t
            print("Confirmed! PNR:", t.pnr, "Seat:", seat)
        else:
            self.waiting.append(t)
            print("Full. Added to waiting list. PNR:", t.pnr)

        self.save()

    def cancel(self):
        try:
            pnr = int(input("Enter PNR: "))
        except ValueError:
            print("Invalid PNR"); return

        if pnr not in self.tickets:
            print("Invalid PNR"); return

        t = self.tickets.pop(pnr)
        self.train.seats[t.cls][t.seat] = "Available"

        days = int(input("Days before journey: "))
        if days >= 7:
            rate = .10
        elif days >= 3:
            rate = .20
        elif days >= 1:
            rate = .30
        else:
            rate = .50

        charge = t.fare * rate
        print("Cancellation charge:", charge)
        print("Refund:", t.fare - charge)

        t.status = "Cancelled"
        t.cancel_time = time.ctime()
        self.cancelled.append(t)

        for w in self.waiting:
            if w.cls == t.cls:
                seat = self.train.available_seat(w.cls)
                w.seat, w.status = seat, "Confirmed"
                self.train.seats[w.cls][seat] = "Occupied"
                self.tickets[w.pnr] = w
                self.waiting.remove(w)
                print("Waiting passenger promoted:", w.passenger.name)
                break

        self.save()

    def search_pnr(self):
        try:
            pnr = int(input("Enter PNR: "))
        except ValueError:
            print("Invalid PNR"); return

        all_tickets = list(self.tickets.values()) + self.waiting + self.cancelled
        for t in all_tickets:
            if t.pnr == pnr:
                print(t.pnr, t.passenger.name, t.cls,
                      t.seat or "Waiting", t.status)
                return
        print("PNR not found")

    def search_passenger(self):
        name = input("Enter name: ").lower()
        all_tickets = list(self.tickets.values()) + self.waiting + self.cancelled
        found = False

        for t in all_tickets:
            if name in t.passenger.name.lower():
                print(t.pnr, t.passenger.name, t.cls,
                      t.seat or "Waiting", t.status)
                found = True

        if not found:
            print("Passenger not found")

    def availability(self):
        for cls, seats in self.train.seats.items():
            print(cls, ":", list(seats.values()).count("Available"),
                  "available")

    def show_waiting(self):
        if not self.waiting:
            print("Waiting list is empty"); return

        for i, t in enumerate(self.waiting, 1):
            print(i, t.passenger.name, t.cls, t.pnr)

    def save(self):
        f = open("railway_data.txt", "w")
        for t in list(self.tickets.values()) + self.waiting + self.cancelled:
            f.write(f"{t.pnr}|{t.passenger.name}|{t.passenger.age}|"
                    f"{t.passenger.phone}|{t.cls}|{t.seat}|{t.fare}|"
                    f"{t.status}\n")
        f.close()

    def load(self):
        try:
            f = open("railway_data.txt", "r")
            for line in f:
                d = line.strip().split("|")
                if len(d) != 8: continue

                p = Passenger(d[1], int(d[2]), d[3])
                t = Ticket(int(d[0]), p, d[4], int(d[5]),
                           float(d[6]), d[7])

                if t.status == "Confirmed":
                    self.tickets[t.pnr] = t
                    self.train.seats[t.cls][t.seat] = "Occupied"
                elif t.status == "Waiting":
                    self.waiting.append(t)
                else:
                    self.cancelled.append(t)
            f.close()
        except FileNotFoundError:
            pass

    def menu(self):
        while True:
            print("\n1.Book 2.Cancel 3.PNR Search 4.Passenger Search")
            print("5.Seat Availability 6.Waiting List 7.Exit")
            ch = input("Choice: ")

            if ch == "1": self.book()
            elif ch == "2": self.cancel()
            elif ch == "3": self.search_pnr()
            elif ch == "4": self.search_passenger()
            elif ch == "5": self.availability()
            elif ch == "6": self.show_waiting()
            elif ch == "7":
                self.save()
                print("Thank you!")
                break
            else:
                print("Invalid menu choice")

if __name__ == "__main__":
    ReservationSystem().menu()
