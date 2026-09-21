import random
import time

class Customer:
    def __init__(self, name, phone, id_proof):
        self.name, self.phone, self.id_proof = name, phone, id_proof

class Room:
    def __init__(self, number, room_type, rate):
        self.number, self.room_type, self.rate = number, room_type, rate
        self.status = "Available"

class Reservation:
    def __init__(self, booking_id, customer, room, days, status="Reserved"):
        self.booking_id = booking_id
        self.customer = customer
        self.room = room
        self.days = days
        self.status = status
        self.reserve_time = time.time()
        self.checkin_time = None
        self.checkout_time = None
        self.bill = 0.0

class Hotel:
    def __init__(self):
        self.rooms = []
        self.reservations = {}
        self.customers = []
        self.cancelled = []
        self.history = []
        self.setup_rooms()
        self.load()

    def setup_rooms(self):
        rooms_data = [
            (101, "Single", 1000), (102, "Single", 1000),
            (103, "Single", 1000),
            (201, "Double", 1800), (202, "Double", 1800),
            (203, "Double", 1800),
            (301, "Deluxe", 3000), (302, "Deluxe", 3000),
            (401, "Suite", 5000)
        ]
        for num, rtype, rate in rooms_data:
            self.rooms.append(Room(num, rtype, rate))

    def generate_booking_id(self):
        while True:
            bid = "BK" + str(random.randint(1000, 9999))
            if bid not in self.reservations:
                return bid

    def find_available_room(self, room_type):
        for r in self.rooms:
            if r.room_type == room_type and r.status == "Available":
                return r
        return None

    def get_room_by_number(self, number):
        for r in self.rooms:
            if r.number == number:
                return r
        return None

    def calculate_bill(self, rate, days, weekend_days):
        bill = rate * days
        bill += weekend_days * 500
        if days > 5:
            bill *= 0.90
        return bill

    def add_customer(self):
        print("\n--- ADD CUSTOMER ---")
        name = input("Customer Name: ")
        phone = input("Phone: ")
        id_proof = input("ID Proof (Aadhar/PAN/Passport): ")

        if not name or not phone:
            print("Name and phone are required!")
            return None

        c = Customer(name, phone, id_proof)
        self.customers.append(c)
        print("Customer added:", name)
        return c

    def book_room(self):
        print("\n--- BOOK ROOM ---")

        if not self.customers:
            print("No customers registered. Add a customer first.")
            return

        print("Registered customers:")
        for i, c in enumerate(self.customers, 1):
            print(f"  {i}. {c.name} ({c.phone})")

        user_input = input("Enter option number (1, 2...) or phone: ").strip()
        customer = None

        # 1. Check if user typed option number (e.g., 1, 2)
        if user_input.isdigit():
            val = int(user_input)
            if 1 <= val <= len(self.customers):
                customer = self.customers[val - 1]

        # 2. Check if user typed phone number or name
        if not customer:
            for c in self.customers:
                if c.phone == user_input or c.name.lower() == user_input.lower():
                    customer = c
                    break

        if not customer:
            print("Customer not found! Invalid selection.")
            return

        print("Room Types: 1.Single(Rs.1000) 2.Double(Rs.1800) "
              "3.Deluxe(Rs.3000) 4.Suite(Rs.5000)")
        types = {"1": "Single", "2": "Double",
                 "3": "Deluxe", "4": "Suite"}
        ch = input("Select type: ")
        if ch not in types:
            print("Invalid room type")
            return

        room_type = types[ch]
        room = self.find_available_room(room_type)
        if not room:
            print("No", room_type, "rooms available!")
            return

        try:
            days = int(input("Number of days: "))
            if days <= 0:
                raise ValueError
        except ValueError:
            print("Invalid number of days")
            return

        try:
            weekend_days = int(input("Weekend days included (0 if none): "))
            if weekend_days < 0 or weekend_days > days:
                raise ValueError
        except ValueError:
            print("Invalid weekend days")
            return

        bid = self.generate_booking_id()
        bill = self.calculate_bill(room.rate, days, weekend_days)

        res = Reservation(bid, customer, room, days)
        res.bill = bill
        room.status = "Reserved"

        self.reservations[bid] = res
        self.save()

        print("\nBooking Confirmed!")
        print("Booking ID:", bid)
        print("Room:", room.number, "(", room.room_type, ")")
        print("Days:", days, "| Weekend days:", weekend_days)
        print("Total Bill: Rs.", bill)

    def check_in(self):
        print("\n--- CHECK IN ---")
        bid = input("Enter Booking ID: ").strip().upper()
        if not bid.startswith("BK") and bid.isdigit():
            bid = "BK" + bid

        if bid not in self.reservations:
            print("Booking not found")
            return

        res = self.reservations[bid]
        if res.status != "Reserved":
            print("Cannot check in. Current status:", res.status)
            return

        res.status = "Checked-In"
        res.checkin_time = time.time()
        res.room.status = "Checked-In"

        print("Checked in successfully!")
        print("Guest:", res.customer.name)
        print("Room:", res.room.number)
        print("Check-in time:", time.ctime(res.checkin_time))
        self.save()

    def check_out(self):
        print("\n--- CHECK OUT ---")
        bid = input("Enter Booking ID: ").strip().upper()
        if not bid.startswith("BK") and bid.isdigit():
            bid = "BK" + bid

        if bid not in self.reservations:
            print("Booking not found")
            return

        res = self.reservations[bid]
        if res.status != "Checked-In":
            print("Guest not checked in. Status:", res.status)
            return

        res.checkout_time = time.time()
        res.status = "Checked-Out"
        res.room.status = "Available"

        final_bill = res.bill

        if res.checkin_time:
            hours_stayed = (res.checkout_time - res.checkin_time) / 3600
            allowed_hours = res.days * 24
            if hours_stayed > allowed_hours:
                extra_hours = hours_stayed - allowed_hours
                late_charge = (extra_hours / 24) * res.room.rate * 0.5
                final_bill += late_charge
                print("Late checkout! Extra hours:", round(extra_hours, 1))
                print("Late charge: Rs.", round(late_charge, 2))

        print("\nChecked out successfully!")
        print("Guest:", res.customer.name)
        print("Room:", res.room.number)
        print("Checkout time:", time.ctime(res.checkout_time))
        print("Final Bill: Rs.", round(final_bill, 2))

        self.history.append(res)
        del self.reservations[bid]
        self.save()

    def cancel_booking(self):
        print("\n--- CANCEL BOOKING ---")
        bid = input("Enter Booking ID: ").strip().upper()
        if not bid.startswith("BK") and bid.isdigit():
            bid = "BK" + bid

        if bid not in self.reservations:
            print("Booking not found")
            return

        res = self.reservations[bid]
        if res.status == "Checked-In":
            print("Cannot cancel. Guest already checked in.")
            return

        elapsed = time.time() - res.reserve_time
        hours = elapsed / 3600

        if hours < 1:
            rate = 0.10
        elif hours < 24:
            rate = 0.25
        else:
            rate = 0.50

        charge = res.bill * rate
        refund = res.bill - charge

        res.status = "Cancelled"
        res.room.status = "Available"

        print("Cancelled!")
        print("Cancellation charge: Rs.", round(charge, 2))
        print("Refund: Rs.", round(refund, 2))

        self.cancelled.append(res)
        del self.reservations[bid]
        self.save()

    def search_booking(self):
        print("\n--- SEARCH BOOKING ---")
        bid = input("Enter Booking ID: ").strip().upper()
        if not bid.startswith("BK") and bid.isdigit():
            bid = "BK" + bid

        all_bookings = (list(self.reservations.values())
                        + self.cancelled + self.history)

        for res in all_bookings:
            if res.booking_id == bid:
                print("Booking ID:", res.booking_id)
                print("Guest:", res.customer.name, "|",
                      res.customer.phone)
                print("Room:", res.room.number, "(",
                      res.room.room_type, ")")
                print("Days:", res.days, "| Bill: Rs.", res.bill)
                print("Status:", res.status)
                if res.checkin_time:
                    print("Check-in:", time.ctime(res.checkin_time))
                if res.checkout_time:
                    print("Check-out:", time.ctime(res.checkout_time))
                return

        print("Booking not found")

    def view_rooms(self):
        print("\n--- ROOM STATUS ---")
        for r in self.rooms:
            print(f"  Room {r.number} | {r.room_type:<8} | "
                  f"Rs.{r.rate:<5} | {r.status}")

    def view_history(self):
        print("\n--- BOOKING HISTORY ---")
        all_bookings = (list(self.reservations.values())
                        + self.cancelled + self.history)

        if not all_bookings:
            print("No bookings yet")
            return

        for res in all_bookings:
            print(f"  {res.booking_id} | {res.customer.name:<15} | "
                  f"Room {res.room.number} | {res.status}")

    def save(self):
        try:
            f = open("hotel_data.txt", "w")
            for c in self.customers:
                f.write(f"CUST|{c.name}|{c.phone}|{c.id_proof}\n")

            all_res = (list(self.reservations.values())
                       + self.cancelled + self.history)
            for res in all_res:
                f.write(f"RES|{res.booking_id}|{res.customer.name}|"
                        f"{res.customer.phone}|{res.room.number}|"
                        f"{res.days}|{res.bill}|{res.status}|"
                        f"{res.reserve_time}|"
                        f"{res.checkin_time or ''}|"
                        f"{res.checkout_time or ''}\n")
            f.close()
        except IOError:
            print("Error saving data")

    def load(self):
        try:
            f = open("hotel_data.txt", "r")
            for line in f:
                d = line.strip().split("|")
                if d[0] == "CUST" and len(d) == 4:
                    c = Customer(d[1], d[2], d[3])
                    self.customers.append(c)

                elif d[0] == "RES" and len(d) == 11:
                    cust = None
                    for c in self.customers:
                        if c.name == d[2] and c.phone == d[3]:
                            cust = c
                            break
                    if not cust:
                        cust = Customer(d[2], d[3], "")

                    room = self.get_room_by_number(int(d[4]))
                    if not room:
                        continue

                    res = Reservation(d[1], cust, room, int(d[5]),
                                      d[7])
                    res.bill = float(d[6])
                    res.reserve_time = float(d[8])
                    res.checkin_time = (float(d[9])
                                        if d[9] else None)
                    res.checkout_time = (float(d[10])
                                         if d[10] else None)

                    if res.status == "Reserved":
                        self.reservations[res.booking_id] = res
                        room.status = "Reserved"
                    elif res.status == "Checked-In":
                        self.reservations[res.booking_id] = res
                        room.status = "Checked-In"
                    elif res.status == "Cancelled":
                        self.cancelled.append(res)
                    else:
                        self.history.append(res)
            f.close()
        except FileNotFoundError:
            pass

    def menu(self):
        while True:
            print("\n========== HOTEL RESERVATION SYSTEM ==========")
            print("1.Add Customer  2.Book Room   3.Check In")
            print("4.Check Out     5.Cancel      6.Search Booking")
            print("7.Room Status   8.History     9.Exit")
            print("=" * 47)
            ch = input("Choice: ")

            if ch == "1": self.add_customer()
            elif ch == "2": self.book_room()
            elif ch == "3": self.check_in()
            elif ch == "4": self.check_out()
            elif ch == "5": self.cancel_booking()
            elif ch == "6": self.search_booking()
            elif ch == "7": self.view_rooms()
            elif ch == "8": self.view_history()
            elif ch == "9":
                self.save()
                print("Thank you!")
                break
            else:
                print("Invalid choice")

if __name__ == "__main__":
    Hotel().menu()
