-- Row Count Verification Query for All 11 Core Tables

USE harborwing_air;

SELECT 'booking_agent' AS table_name, COUNT(*) AS total_rows FROM booking_agent
UNION ALL SELECT 'passenger', COUNT(*) FROM passenger
UNION ALL SELECT 'airport', COUNT(*) FROM airport
UNION ALL SELECT 'calendar_date', COUNT(*) FROM calendar_date
UNION ALL SELECT 'flight_schedule', COUNT(*) FROM flight_schedule
UNION ALL SELECT 'reservation', COUNT(*) FROM reservation
UNION ALL SELECT 'payment', COUNT(*) FROM payment
UNION ALL SELECT 'flight_leg', COUNT(*) FROM flight_leg
UNION ALL SELECT 'flight_cost', COUNT(*) FROM flight_cost
UNION ALL SELECT 'reservation_payment_link', COUNT(*) FROM reservation_payment_link
UNION ALL SELECT 'reservation_leg_link', COUNT(*) FROM reservation_leg_link;