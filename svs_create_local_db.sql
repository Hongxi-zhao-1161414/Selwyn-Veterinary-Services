
--  =============  1. CREATE DATABASE (ONCE ONLY)  ===============

--  Run me once to create an empty 'svs' schema (database) on your local computer

--  (In PythonAnywhere, this won't work: create the database through the PythonAnywhere web page UI 
--     according to instructions in class.)

DROP DATABASE IF EXISTS svs;
CREATE DATABASE svs;
USE svs;

--  REMEMBER:  Press 🔄 in the top right of the Schema sidebar to see the new schema (database)


--  =======  NEXT STEP:  2. Run svs_populate_data.sql to (re)populate your data  =================

