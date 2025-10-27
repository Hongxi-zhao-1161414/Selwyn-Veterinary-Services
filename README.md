# SVS (Veterinary Service Management System) Project README

This document provides an overview of the SVS project, including key design decisions, image sources, and answers to database-related questions. The project is a Flask-based web application for managing veterinary service customers, appointments, and service records.

## 1. Design Decisions

Below are key design decisions made during the development of the SVS application, including rationale and alternative options considered:

### 1.1 Modular Route Organization by Function
- **Decision**: Routes are grouped into four functional categories: *Basic Routes* (home, service list), *Customer Routes* (list, search, add, edit), *Appointment Routes* (list, new, customer-specific summary), and *Report Routes* (service summary).  
- **Considered Alternatives**: A single "all-routes" file or grouping by technical type (e.g., GET-only routes, POST-only routes).  
- **Rationale**: Functional grouping aligns with user workflows (e.g., "managing customers" or "scheduling appointments") and simplifies maintenance. New developers can quickly locate routes related to a specific feature, reducing onboarding time.


### 1.2 MySQL Connection Pooling (Instead of Per-Request Connections)
- **Decision**: The `db.py` module uses `MySQLConnectionPool` to create a reusable pool of database connections, initialized once via `init_db()`. Connections are retrieved with `get_db()` and released via `close_db()` on request teardown.  
- **Considered Alternatives**: Creating a new database connection for every HTTP request.  
- **Rationale**: Connection pooling reduces overhead from repeated connection/disconnection cycles (critical for high-traffic scenarios) and ensures efficient resource usage. Without pooling, each request would incur latency from establishing a new MySQL connection.


### 1.3 GET/POST Method Separation for Form Workflows
- **Decision**: Form-based routes (e.g., `add_customer`, `edit_customer`, `new_appointment`) use **GET** to display empty/ pre-filled forms and **POST** to process form submissions.  
- **Considered Alternatives**: Mixed-method handling (e.g., a single route that checks request type internally) or using non-standard HTTP methods.  
- **Rationale**: Complies with HTTP semantics (GET for "retrieve data," POST for "submit data") and improves security (avoids accidental form resubmissions via browser refresh). It also simplifies debugging by separating "display logic" from "data processing logic."


### 1.4 Date Format Conversion for User Experience & Frontend Compatibility
- **Decision**: Date fields are converted between two formats:  
  - **Display Format**: `dd/mm/yyyy` (New Zealand standard) for user-facing pages (e.g., customer list).  
  - **Input Format**: `YYYY-MM-DD` for HTML `<input type="date">` components (e.g., edit customer form), as this is the only format supported by most browsers.  
- **Considered Alternatives**: Using a single format (e.g., `YYYY-MM-DD` for both display and input) or relying on frontend JavaScript for conversion.  
- **Rationale**: Prioritizes user familiarity (NZ date format) while ensuring compatibility with native HTML form elements. Avoids JavaScript dependencies for basic date handling, reducing frontend complexity.


### 1.5 Decimal Type for Currency Calculations (Avoid Floating-Point Errors)
- **Decision**: Appointment total costs and service prices use Python’s `Decimal` type (instead of `float`) for calculations in the `_process_appointment_data()` helper function.  
- **Considered Alternatives**: Using `float` for simplicity or calculating totals directly in SQL.  
- **Rationale**: `Decimal` eliminates floating-point precision errors (e.g., `0.1 + 0.2 = 0.30000000000000004`), which is critical for financial data like service prices and appointment totals. SQL `SUM()` could work, but grouping appointments with multiple services (in `_process_appointment_data()`) requires client-side aggregation.


### 1.6 Transactional Integrity for Appointment Creation
- **Decision**: When creating a new appointment (`new_appointment` route), the application disables auto-commit, inserts a record into `appointments`, then inserts related records into `appointment_services`, and commits only if both steps succeed (rolls back on failure).  
- **Considered Alternatives**: Auto-committing each insert separately.  
- **Rationale**: Ensures data consistency. Without transactions, a failure after inserting the appointment (but before inserting services) would leave orphaned appointments with no associated services, breaking reports and appointment summaries.


### 1.7 Flash Messages for User Feedback
- **Decision**: Every user action (e.g., adding a customer, searching for appointments, database errors) triggers a `flash` message (success/info/warning/danger) to inform the user of results.  
- **Considered Alternatives**: Silent failures, redirects without feedback, or inline error messages in templates.  
- **Rationale**: Improves usability by reducing ambiguity. For example, a user knows if a customer was added successfully or if a search returned no results, instead of guessing why a page looks unchanged.


### 1.8 Immutable "Date Joined" for Customers
- **Decision**: The `date_joined` field for customers is set once during creation and cannot be modified via the `edit_customer` route.  
- **Considered Alternatives**: Allowing users to edit `date_joined` (e.g., to correct data entry mistakes).  
- **Rationale**: `date_joined` is a historical record (tracks when a customer first registered) and should remain immutable to maintain data integrity. If corrections are needed, they can be handled via admin-only database tools (avoiding accidental changes in the web app).


### 1.9 Appointment Time Validation (Future + Non-Sunday)
- **Decision**: The `new_appointment` route validates that the selected time is: (1) in the future, and (2) not a Sunday (via `appt_datetime.weekday() == 6`).  
- **Considered Alternatives**: No validation (letting users schedule past/Sunday appointments) or server-side validation only.  
- **Rationale**: Aligns with business rules (e.g., the clinic is closed on Sundays and does not schedule retro-active appointments). Validating on the server (instead of only frontend) prevents bypassing rules via browser dev tools.


### 1.10 Helper Function for Appointment Data Processing
- **Decision**: A reusable `_process_appointment_data()` function groups raw database rows (from joined `appointments`, `customers`, and `services` tables) by `appt_id`, calculates totals, and formats dates.  
- **Considered Alternatives**: Processing data directly in the `appointment_list` and `customer_appointment_summary` routes (duplicating code) or using SQL subqueries to aggregate data.  
- **Rationale**: Reduces code duplication (both routes use the same logic) and simplifies maintenance. SQL aggregation would require complex subqueries to group services by appointment, making the query harder to debug.



## 2. Database Questions

### 2.1 Table Creation: SQL for `customers` Table
The following SQL from `svs_populate_data.sql` creates the `customers` table with all fields, constraints, and indexes:
```sql
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
```


### 2.2 Table Relationships: Linking `appointments` and `services`
The relationship between `appointments` and `services` is established via the `appointment_services` junction table, defined by the following lines in `svs_populate_data.sql`:
```sql
-- Primary key (composite to enforce unique appointment-service pairs)
PRIMARY KEY (appt_id, service_id),
-- Foreign key to appointments (deletes/updates cascade)
CONSTRAINT fk_as_appt FOREIGN KEY (appt_id) REFERENCES appointments(appt_id)
  ON DELETE CASCADE ON UPDATE CASCADE,
-- Foreign key to services (prevents deletion of used services)
CONSTRAINT fk_as_service FOREIGN KEY (service_id) REFERENCES services(service_id)
  ON DELETE RESTRICT ON UPDATE CASCADE
```


### 2.3 New Table Design: `animals` Table
The following SQL creates an `animals` table to track customers’ pets, with a foreign key to `customers` and required fields:
```sql
CREATE TABLE animals (
  animal_id INT NOT NULL AUTO_INCREMENT,
  customer_id INT NOT NULL, -- Links to the animal's owner (existing customer)
  animal_name VARCHAR(50) NOT NULL, -- Name of the animal (e.g., "Max")
  species VARCHAR(40) NOT NULL, -- e.g., "Dog", "Cat", "Horse"
  sex ENUM('Male', 'Female', 'Unknown') NOT NULL, -- Standardized sex values
  date_of_birth DATE, -- Optional (some owners may not know DOB)
  PRIMARY KEY (animal_id),
  -- Foreign key to customers (prevents deleting customers with animals)
  CONSTRAINT fk_animal_customer FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  -- Index for faster queries by customer (e.g., "get all animals for customer 101")
  INDEX idx_animal_customer (customer_id)
);
```


### 2.4 Data Insertion: Add a Fictional Animal
The following SQL inserts a cat named "Luna" owned by Aria Rangi (customer_id = 101, from the existing `customers` table):
```sql
INSERT INTO animals (customer_id, animal_name, species, sex, date_of_birth)
VALUES (101, 'Luna', 'Cat', 'Female', '2022-05-15');
```


### 2.5 Data Model: Linking Appointments to Animals vs. Customers
An appointment should be **linked to an animal** (not just the customer) for the following reasons:  
Veterinary services are inherently animal-specific (e.g., a vaccination or dental clean is performed on a pet, not a customer). Linking appointments to animals allows the system to track individual pet health histories (e.g., "Luna had a vaccination in 2024"), which is critical for clinical care (e.g., reminding owners of upcoming boosters).  

If appointments were only linked to customers, the system could not distinguish between multiple pets (e.g., a customer with two dogs would have appointments without clarity on which dog was treated). This would break core workflows like generating pet-specific reports or maintaining accurate medical records.  

While the current model links appointments to customers, adding an `animal_id` foreign key to the `appointments` table would make the system more useful for veterinary staff and align with real-world clinic operations.