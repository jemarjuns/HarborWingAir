-- Example Operational and Analytical Queries for HarborWing Air

USE harborwing_air;

-- Query 1: Viewing a reservation with its main passenger, agent, payments, and flight legs
SELECT 
    r.reservation_id,
    CONCAT(p.first_name, ' ', p.last_name) AS main_passenger_name,
    p.email_address AS passenger_email,
    COALESCE(ba.agent_name, 'Direct Booking') AS booking_agent,
    r.reservation_status_code,
    r.travel_class_code,
    r.number_in_party,
    GROUP_CONCAT(DISTINCT pay.payment_id) AS linked_payment_ids,
    GROUP_CONCAT(DISTINCT leg.leg_id) AS linked_leg_ids
FROM reservation r
JOIN passenger p ON r.main_passenger_id = p.passenger_id
LEFT JOIN booking_agent ba ON r.booking_agent_id = ba.agent_id
LEFT JOIN reservation_payment_link rpl ON r.reservation_id = rpl.reservation_id
LEFT JOIN payment pay ON rpl.payment_id = pay.payment_id
LEFT JOIN reservation_leg_link rll ON r.reservation_id = rll.reservation_id
LEFT JOIN flight_leg leg ON rll.leg_id = leg.leg_id
WHERE r.reservation_id = 1
GROUP BY r.reservation_id, p.first_name, p.last_name, p.email_address, ba.agent_name, r.reservation_status_code, r.travel_class_code, r.number_in_party;

-- Query 2: Finding reservations using a particular flight leg
SELECT 
    rll.leg_id,
    r.reservation_id,
    CONCAT(p.first_name, ' ', p.last_name) AS main_passenger,
    r.number_in_party,
    r.reservation_status_code
FROM reservation_leg_link rll
JOIN reservation r ON rll.reservation_id = r.reservation_id
JOIN passenger p ON r.main_passenger_id = p.passenger_id
WHERE rll.leg_id = 5;

-- Query 3: Finding payments linked to a specific reservation
SELECT 
    rpl.reservation_id,
    p.payment_id,
    p.payment_date,
    p.payment_amount,
    p.payment_status_code
FROM reservation_payment_link rpl
JOIN payment p ON rpl.payment_id = p.payment_id
WHERE rpl.reservation_id = 1;

-- Query 4: Finding a flight cost for a flight, aircraft type, and date
SELECT 
    flight_number,
    aircraft_type_code,
    cost_amount,
    valid_from_date,
    valid_to_date
FROM flight_cost
WHERE flight_number = 'HW001'
  AND aircraft_type_code = 'ATR72'
  AND '2026-01-15' BETWEEN valid_from_date AND valid_to_date;