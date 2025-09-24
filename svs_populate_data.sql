
--  =============  2. (RE)POPULATE DATA  ===============

--  Run this query after you have run svs_create_local_db.sql ONCE to create your schema (database)

--  WARNING: THIS WILL ERASE ANY EXTRA DATA YOU HAVE *ADDED* TO THE DATABASE

--  You can run this query any time you want to reset your data back to the default
--  (Data can get messy during testing and you may want to reset back to the initial data)

-- ===== (Re)create tables safely =====

-- DROP (delete) all tables, so we can recreate them again below and insert clean data
DROP TABLE IF EXISTS appointment_services;
DROP TABLE IF EXISTS appointments;
DROP TABLE IF EXISTS services;
DROP TABLE IF EXISTS customers;


-- ==== Tables ====

-- Customers 
CREATE TABLE customers (
  customer_id INT NOT NULL AUTO_INCREMENT,
  first_name VARCHAR(50) NOT NULL,
  family_name VARCHAR(60) NOT NULL,
  email VARCHAR(120),
  phone VARCHAR(30) NOT NULL,
  date_joined DATE NOT NULL,
  PRIMARY KEY (customer_id),
  INDEX idx_customer_name (family_name, first_name)
);

-- Services / Treatments (explicit IDs)
CREATE TABLE services (
  service_id INT NOT NULL AUTO_INCREMENT,
  service_name VARCHAR(120) NOT NULL,
  price DECIMAL(8,2) NOT NULL,
  PRIMARY KEY (service_id),
  UNIQUE KEY uq_service_name (service_name)
);

-- Appointments: link to customers only (no animal_id in this simplified seed)
CREATE TABLE appointments (
  appt_id INT NOT NULL AUTO_INCREMENT,
  customer_id INT NOT NULL,
  appt_datetime DATETIME NOT NULL,
  notes VARCHAR(255) NULL,
  PRIMARY KEY (appt_id),
  CONSTRAINT fk_appt_customer FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  INDEX idx_appt_datetime (appt_datetime)
);

-- Appointment to services (many-to-many; explicit values)
CREATE TABLE appointment_services (
  appt_id INT NOT NULL,
  service_id INT NOT NULL,
  PRIMARY KEY (appt_id, service_id),
  CONSTRAINT fk_as_appt FOREIGN KEY (appt_id) REFERENCES appointments(appt_id)
    ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT fk_as_service FOREIGN KEY (service_id) REFERENCES services(service_id)
    ON DELETE RESTRICT ON UPDATE CASCADE
);

--  ========== Insert data into tables =============

-- Services 
INSERT INTO services (service_id, service_name, price) VALUES
(11,  'Consultation',           65.00),
(12,  'Vaccination',            85.00),
(13,  'Desexing (cat)',        130.00),
(14,  'Desexing (dog small)',  220.00),
(15,  'Dental clean (basic)',  185.00),
(16,  'Microchipping',          45.00),
(17,  'Flea treatment',         28.00),
(18,  'Worm treatment',         22.00),
(19,  'Hoof trim',              40.00),
(20, 'Farm call-out (base)',   95.00);


-- Customers 
INSERT INTO customers (customer_id, first_name, family_name, email, phone, date_joined) VALUES
(101, 'Aria',      'Rangi',        'aria.rangi@xtra.co.nz',                 '021 482 730', '2023-02-14'),
(102, 'Sione',     'Fiso',         'sione_fiso@yahoo.co.nz',                '022 915 644', '2023-03-02'),
(103, 'Priya',     'Patel',        'priya.patel.nz19@gmail.com',            '021 773 190', '2023-05-19'),
(104, 'Li',        'Zhang',        'li.zhang188@outlook.com',               '027 310 452', '2023-07-07'),
(105, 'Hemi',      'Te Aho',       'hemi.t@proton.me',                      '021 980 221', '2023-09-23'),
(106, 'Amelia',    'O''Connor',    NULL,                                     '022 640 556', '2023-10-04'),
(107, 'Tane',      'Ngata',        'tane_n@live.com',                       '021 334 900', '2023-12-18'),
(108, 'Aisha',     'Khan',         'aisha.khan.nz@outlook.co.nz',           '027 555 014', '2024-01-09'),
(109, 'Charlotte', 'Bennett',      'charliebennett83@gmail.com',            '021 909 447', '2024-02-21'),
(110, 'Ravi',      'Singh',        'rsingh1999@gmail.com',                  '022 771 004', '2024-03-30'),
(111, 'Melissa',   'Fa’amatuainu', 'mel.faama@gmail.com',                   '029 112 765', '2024-05-06'),
(112, 'Samuel',    'Brown',        'sammy.b@outlook.com',                   '021 700 238', '2024-06-15'),
(113, 'Yuki',      'Sato',         'yuki_sato@hotmaiI.com',                 '022 564 990', '2024-07-28'),
(114, 'Olivia',    'Brown',        'olivia.brown@uni.canterbury.ac.nz',     '021 220 615', '2024-08-11'),
(115, 'Mateo',     'Garcia',       'mateo.g.indahouse@xtra.co.nz',          '027 446 381', '2024-09-05'),
(116, 'Fatima',    'Hussein',      'fatima.hussein4cats@gmail.com',         '022 998 341', '2024-10-19'),
(117, 'Wiremu',    'Parata',       'w_parata@xtra.co.nz',                   '021 308 774', '2024-12-02'),
(118, 'Chen',      'Wang',         'chen.w.2000@outlook.com',               '029 884 213', '2025-02-08'),
(119, 'Sofia',     'Martinez',     NULL,                                    '021 615 744', '2025-03-27'),
(120, 'Zara',      'Ahmed',        'zara__ahmed@proton.me',                 '022 350 901', '2025-06-04');


-- Appointments 
INSERT INTO appointments (appt_id, customer_id, appt_datetime, notes) VALUES
(2235, 101, '2024-11-18 10:30:00', 'Annual consultation'),
(2236, 101, '2025-02-12 09:00:00', 'Vaccination due'),
(2237, 102, '2025-03-22 11:15:00', 'Microchip request'),
(2238, 103, '2025-01-20 15:45:00', 'General check'),
(2239, 103, '2025-10-02 10:00:00', 'Follow-up'),
(2240, 104, '2025-04-07 09:30:00', 'Consult'),
(2241, 105, '2025-05-12 14:30:00', 'Check-up'),
(2242, 106, '2024-10-09 16:30:00', 'Dental review'),
(2243, 106, '2025-06-01 12:00:00', 'Wellness check'),
(2244, 107, '2025-07-19 08:45:00', 'Hoof/trim enquiry'),
(2245, 108, '2025-02-28 13:30:00', 'Vacc + microchip'),
(2246, 109, '2025-01-05 09:00:00', 'Flea & worm'),
(2247, 109, '2025-10-10 11:00:00', 'Vaccination'),
(2248, 110, '2024-09-02 10:00:00', 'General consult'),
(2249, 110, '2025-03-01 15:00:00', 'Dental clean'),
(2250, 111, '2024-12-14 11:30:00', 'Dental clean'),
(2251, 111, '2025-06-22 09:15:00', 'Wellness'),
(2252, 112, '2025-04-12 16:45:00', 'Vaccination'),
(2253, 113, '2024-11-01 14:10:00', 'Ear check'),
(2254, 113, '2025-05-05 10:20:00', 'Consultation'),
(2255, 114, '2025-02-10 12:30:00', 'Vaccination'),
(2256, 115, '2025-01-18 13:50:00', 'Injury check'),
(2257, 115, '2025-08-30 09:40:00', 'Follow-up'),
(2258, 116, '2025-07-01 11:10:00', 'General check'),
(2259, 117, '2024-08-22 10:30:00', 'Vaccination'),
(2260, 117, '2025-02-15 14:00:00', 'Dental'),
(2261, 118, '2025-03-20 09:20:00', 'Consultation'),
(2262, 119, '2025-06-03 15:30:00', 'Farm call-out'),
(2263, 120, '2025-01-25 10:00:00', 'Wellness check'),
(2264, 120, '2025-09-12 16:00:00', 'Vaccination'),
(2265, 104, '2025-08-05 16:00:00', 'Flea treatment'),
(2266, 105, '2025-09-20 10:15:00', 'Vaccination'),
(2267, 108, '2025-03-03 10:30:00', 'Worm treatment'),
(2268, 112, '2025-05-18 14:45:00', 'Microchip + vacc'),
(2269, 118, '2025-08-22 09:00:00', 'Consult + dental'),
(2270, 114, '2024-10-28 11:05:00', 'Hoof trim + consult');


-- Appointment services
INSERT INTO appointment_services (appt_id, service_id) VALUES
(2235,  11), (2235,  12),
(2236,  12),
(2237,  16),
(2238,  11), (2238,  16),
(2239,  12),
(2240,  11), (2240,  12),
(2241,  11), (2241,  12),
(2242,  15),
(2243,  11), (2243,  17),
(2244,  19),
(2245,  12), (2245,  16), (2245,  11),
(2246,  17), (2246,  18),
(2247,  12),
(2248,  11), (2248,  12),
(2249,  15),
(2250,  15),
(2251,  11),
(2252,  12),
(2253,  11),
(2254,  11),
(2255,  12),
(2256,  11),
(2257,  11), (2257,  17),
(2258,  11), (2258,  18),
(2259,  12),
(2260,  15),
(2261,  11),
(2262,  11), (2262, 20), (2262,  19), (2262,  18),
(2263,  11),
(2264,  12),
(2265,  17),
(2266,  12),
(2267,  18),
(2268,  16), (2268,  12), (2268,  11),
(2269,  11), (2269,  15), (2269,  12),
(2270,  19), (2270,  11);

-- End of data insert
