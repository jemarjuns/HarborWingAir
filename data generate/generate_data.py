import random
from datetime import datetime, timedelta
from faker import Faker
import mysql.connector

# Initialize Faker with fixed seed for reproducibility
fake = Faker()
Faker.seed(42)
random.seed(42)

# Database Connection Details
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "your_password",
    "database": "harborwing_air",
}


def seed_database():
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    print("Seeding database...")

    # 1. Calendar Dates (spanning 2026-01-01 to 2026-03-31)
    start_date = datetime(2026, 1, 1).date()
    calendar_dates = [start_date + timedelta(days=i) for i in range(90)]
    for d in calendar_dates:
        is_bus = d.weekday() < 5
        cursor.execute(
            "INSERT INTO calendar_date (calendar_date, day_of_month, is_business_day) VALUES (%s, %s, %s)",
            (d, d.day, is_bus),
        )

    # 2. Airports (50 regional airports/codes)
    airport_codes = []
    for i in range(50):
        code = f"A{i+1:02d}"
        airport_codes.append(code)
        cursor.execute(
            "INSERT INTO airport (airport_code, airport_name, location, other_details) VALUES (%s, %s, %s, %s)",
            (
                code,
                f"{fake.city()} Regional Airport",
                fake.city(),
                "Coastal hub",
            ),
        )

    # 3. Booking Agents (50 records)
    agent_ids = []
    for _ in range(50):
        cursor.execute(
            "INSERT INTO booking_agent (agent_name, additional_details) VALUES (%s, %s)",
            (fake.company(), fake.job()),
        )
        agent_ids.append(cursor.lastrowid)

    # 4. Passengers (50 records)
    passenger_ids = []
    for _ in range(50):
        cursor.execute(
            """INSERT INTO passenger 
            (first_name, second_name, last_name, phone_number, email_address, address_line1, city, state_province_county, country)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (
                fake.first_name(),
                fake.first_name() if random.random() > 0.5 else None,
                fake.last_name(),
                fake.phone_number()[:25],
                fake.unique.email(),
                fake.street_address(),
                fake.city(),
                fake.state(),
                fake.country(),
            ),
        )
        passenger_ids.append(cursor.lastrowid)

    # 5. Flight Schedules (50 records)
    flight_numbers = []
    for i in range(1, 51):
        f_num = f"HW{i:03d}"
        flight_numbers.append(f_num)
        orig, dest = random.sample(airport_codes, 2)
        dep = fake.date_time_between(
            start_date=datetime(2026, 1, 1), end_date=datetime(2026, 2, 1)
        )
        arr = dep + timedelta(hours=random.randint(1, 4))
        cursor.execute(
            """INSERT INTO flight_schedule 
            (flight_number, airline_code, usual_aircraft_type_code, origin_airport, destination_airport, scheduled_departure_time, scheduled_arrival_time)
            VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (f_num, "HW", "ATR72", orig, dest, dep, arr),
        )

    # 6. Flight Legs (50 records)
    leg_ids = []
    for f_num in flight_numbers:
        cursor.execute(
            "SELECT origin_airport, destination_airport, scheduled_departure_time FROM flight_schedule WHERE flight_number = %s",
            (f_num,),
        )
        orig, dest, dep = cursor.fetchone()
        act_dep = dep + timedelta(minutes=random.randint(-10, 30))
        act_arr = act_dep + timedelta(hours=2)
        cursor.execute(
            """INSERT INTO flight_leg 
            (flight_number, origin_airport, destination_airport, actual_departure_time, actual_arrival_time)
            VALUES (%s, %s, %s, %s, %s)""",
            (f_num, orig, dest, act_dep, act_arr),
        )
        leg_ids.append(cursor.lastrowid)

    # 7. Flight Costs (50 records)
    for i, f_num in enumerate(flight_numbers):
        v_from = calendar_dates[i % 30]
        v_to = calendar_dates[(i % 30) + 30]
        cursor.execute(
            """INSERT INTO flight_cost 
            (flight_number, aircraft_type_code, valid_from_date, valid_to_date, cost_amount)
            VALUES (%s, %s, %s, %s, %s)""",
            (
                f_num,
                "ATR72",
                v_from,
                v_to,
                round(random.uniform(150.0, 500.0), 2),
            ),
        )

    # 8. Reservations (50 records, direct & agent-assisted)
    reservation_ids = []
    for _ in range(50):
        agent = random.choice(agent_ids) if random.random() > 0.4 else None
        cursor.execute(
            """INSERT INTO reservation 
            (main_passenger_id, booking_agent_id, reservation_status_code, ticket_type_code, travel_class_code, number_in_party)
            VALUES (%s, %s, %s, %s, %s, %s)""",
            (
                random.choice(passenger_ids),
                agent,
                "CONFIRMED",
                "E-TICKET",
                "ECONOMY",
                random.randint(1, 4),
            ),
        )
        reservation_ids.append(cursor.lastrowid)

    # 9. Payments (50 records)
    payment_ids = []
    for _ in range(50):
        cursor.execute(
            """INSERT INTO payment (payment_status_code, payment_date, payment_amount)
            VALUES (%s, %s, %s)""",
            (
                "COMPLETED",
                fake.date_time_this_year(),
                round(random.uniform(100.0, 1200.0), 2),
            ),
        )
        payment_ids.append(cursor.lastrowid)

    # 10. Reservation-Payment Links (at least 50 relationships)
    res_pay_pairs = set()
    while len(res_pay_pairs) < 55:
        r_id = random.choice(reservation_ids)
        p_id = random.choice(payment_ids)
        res_pay_pairs.add((r_id, p_id))

    for r_id, p_id in res_pay_pairs:
        cursor.execute(
            "INSERT INTO reservation_payment_link (reservation_id, payment_id) VALUES (%s, %s)",
            (r_id, p_id),
        )

    # 11. Reservation-Leg Links (at least 50 relationships)
    res_leg_pairs = set()
    while len(res_leg_pairs) < 55:
        r_id = random.choice(reservation_ids)
        l_id = random.choice(leg_ids)
        res_leg_pairs.add((r_id, l_id))

    for r_id, l_id in res_leg_pairs:
        cursor.execute(
            "INSERT INTO reservation_leg_link (reservation_id, leg_id) VALUES (%s, %s)",
            (r_id, l_id),
        )

    conn.commit()
    cursor.close()
    conn.close()
    print("Database seeding completed successfully!")


if __name__ == "__main__":
    seed_database()