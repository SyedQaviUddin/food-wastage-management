


-- open this file in mysql workbench and run the code to create the database and tables
-- then run the queries in the queries.sql file to get the results

-- ensure that you have imported data_insert.sql file to populate the tables with data



create database food;
use food;
-- create_tables.sql
CREATE TABLE Providers (
  Provider_ID INTEGER PRIMARY KEY,
  Name TEXT NOT NULL,
  Type TEXT,
  Address TEXT,
  City TEXT,
  Contact TEXT
);

CREATE TABLE Receivers (
  Receiver_ID INTEGER PRIMARY KEY,
  Name TEXT NOT NULL,
  Type TEXT,
  City TEXT,
  Contact TEXT
);

CREATE TABLE Food_Listings (
  Food_ID INTEGER PRIMARY KEY,
  Food_Name TEXT,
  Quantity INTEGER NOT NULL,
  Expiry_Date DATE,
  Provider_ID INTEGER,
  Provider_Type TEXT,
  Location TEXT,
  Food_Type TEXT,
  Meal_Type TEXT,
  FOREIGN KEY (Provider_ID) REFERENCES Providers(Provider_ID)
);

CREATE TABLE Claims (
  Claim_ID INTEGER PRIMARY KEY,
  Food_ID INTEGER,
  Receiver_ID INTEGER,
  Status TEXT,             -- Pending, Completed, Cancelled
  Timestamp DATETIME,
  FOREIGN KEY (Food_ID) REFERENCES Food_Listings(Food_ID),
  FOREIGN KEY (Receiver_ID) REFERENCES Receivers(Receiver_ID)
);
-- Add indexes for frequent queries:
CREATE INDEX idx_food_location ON Food_Listings(Location);
CREATE INDEX idx_claim_status ON Claims(Status);




-- quries--


-- how many providers and recivers are there in each city--
SELECT city, COUNT(DISTINCT Provider_ID) AS provider_count
FROM Providers GROUP BY city;

SELECT city, COUNT(DISTINCT Receiver_ID) AS receiver_count
FROM Receivers GROUP BY city;
-- most of the providers and recivers are 1 from each city--


-- which type of provider contribute the most food--
SELECT p.Type AS provider_type, SUM(f.Quantity) AS total_qty
FROM Providers p JOIN Food_Listings f ON p.Provider_ID = f.Provider_ID
GROUP BY p.Type ORDER BY total_qty DESC LIMIT 1;
-- the provider contribute the most food is restaurent with total quantity of 6923--

-- provider contact details in specific citys--
SELECT Name, Contact,city FROM Providers WHERE City = 'New Jessica';
-- gonzales-cochran -- --+1-600-220-0480

-- which reciver has claimed the most food--
SELECT r.Receiver_ID, r.Name, COUNT(c.Claim_ID) AS num_claims
FROM Receivers r JOIN Claims c ON r.Receiver_ID = c.Receiver_ID
GROUP BY r.Receiver_ID ORDER BY num_claims DESC LIMIT 10;
-- 742-- -- matthew webb-- --5--

-- total quantity of food available--
SELECT SUM(Quantity) AS total_available FROM Food_Listings;
-- the total quantity is 25794--

-- City with the highest number of food listings--
SELECT Location AS city, COUNT(Food_ID) AS listings
FROM Food_Listings GROUP BY Location ORDER BY listings DESC LIMIT 1;
 -- New Carol-- -- 6--
 
 -- Most commonly available food types--
 SELECT Food_Type, COUNT(*) AS freq FROM Food_Listings
GROUP BY Food_Type ORDER BY freq DESC LIMIT 10;

-- How many claims per food item--
SELECT f.Food_ID, f.Food_Name, COUNT(c.Claim_ID) AS claim_count
FROM Food_Listings f LEFT JOIN Claims c ON f.Food_ID = c.Food_ID
GROUP BY f.Food_ID ORDER BY claim_count DESC;
-- 463--soup--5--
-- 463--chicken--5--
-- 548--fish--5--

-- Provider with highest number of successful (completed) claims--
SELECT p.Provider_ID, p.Name, COUNT(c.Claim_ID) AS completed_claims
FROM Providers p
JOIN Food_Listings f ON p.Provider_ID = f.Provider_ID
JOIN Claims c ON f.Food_ID = c.Food_ID
WHERE c.Status = 'Completed'
GROUP BY p.Provider_ID ORDER BY completed_claims DESC LIMIT 1;
-- 709--barry group--5--

-- Percentage of claim statuses (completed/pending/cancelled)--
SELECT Status,
       COUNT(*) * 100.0 / (SELECT COUNT(*) FROM Claims) AS percent
FROM Claims GROUP BY Status;
-- Pending	32.5--Cancelled	33.6--Completed	33.9--

-- Average quantity of food claimed per receiver--
SELECT c.Receiver_ID, r.Name, AVG(f.Quantity) AS avg_quantity
FROM Claims c
JOIN Food_Listings f ON c.Food_ID = f.Food_ID
JOIN Receivers r ON c.Receiver_ID = r.Receiver_ID
GROUP BY c.Receiver_ID ORDER BY avg_quantity DESC;
-- 739	Nancy Jones	50.0000--
-- 282	Lisa Pitts	50.0000--
-- 616	Christopher Wright	50.0000--

-- Most claimed meal type--
SELECT f.Meal_Type, COUNT(c.Claim_ID) AS times_claimed
FROM Food_Listings f JOIN Claims c ON f.Food_ID = c.Food_ID
GROUP BY f.Meal_Type ORDER BY times_claimed DESC;
-- Breakfast--278--

-- Total quantity donated by each provider--
SELECT p.Provider_ID, p.Name, SUM(f.Quantity) AS total_donated
FROM Providers p JOIN Food_Listings f ON p.Provider_ID = f.Provider_ID
GROUP BY p.Provider_ID ORDER BY total_donated DESC;
-- 709--Barry Group--179--
-- 306--Evans, Wright and Mitchell--158--

-- Food listings nearing expiry (in next 2 days)--
SELECT * FROM Food_Listings
WHERE date(Expiry_Date) <= date('now', '+2 day') AND date(Expiry_Date) >= date('now');

-- Top locations for donations (rank by quantity)--
SELECT Location, SUM(Quantity) AS total_qty
FROM Food_Listings GROUP BY Location ORDER BY total_qty DESC LIMIT 10;
-- South Kathryn--179--
-- Jonathanstad--169--
-- New Carol--167--






