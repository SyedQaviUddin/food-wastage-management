import mysql.connector
import pandas as pd
import numpy as np
from datetime import datetime

# ---- Connect to Clever Cloud MySQL ----
conn = mysql.connector.connect(
    host="bnjglsog2qvis4hjcfac-mysql.services.clever-cloud.com",
    user="uvycyi0crn7fp9tj",
    password="fWicr2n6qnSpyUOxijXd",
    database="bnjglsog2qvis4hjcfac",
    port=3306,
    auth_plugin="mysql_native_password"
)
cursor = conn.cursor()

# ---- Utility: Convert timestamp columns to MySQL-friendly strings ----
def convert_timestamps(df):
    for col in df.columns:
        if "time" in col.lower() or "date" in col.lower():
            df[col] = df[col].apply(lambda x: convert_datetime_value(x))
    return df

def convert_datetime_value(val):
    if pd.isnull(val):
        return None
    try:
        # Handle integers (nano / milli / seconds)
        if isinstance(val, (np.int64, int)):
            if val > 1e14:   # nanoseconds
                return datetime.fromtimestamp(val / 1e9).strftime("%Y-%m-%d %H:%M:%S")
            elif val > 1e11: # milliseconds
                return datetime.fromtimestamp(val / 1e3).strftime("%Y-%m-%d %H:%M:%S")
            elif val > 1e9:  # seconds
                return datetime.fromtimestamp(val).strftime("%Y-%m-%d %H:%M:%S")
        elif isinstance(val, pd.Timestamp):
            return val.strftime("%Y-%m-%d %H:%M:%S")
        elif isinstance(val, str):
            # Try parsing string to normalize
            try:
                return pd.to_datetime(val).strftime("%Y-%m-%d %H:%M:%S")
            except:
                return val
    except:
        return None
    return val

# ---- DB Setup ----
cursor.execute("SET NAMES utf8mb4;")
cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")

# Drop in dependency order (child → parent)
cursor.execute("DROP TABLE IF EXISTS `Claims`;")
cursor.execute("DROP TABLE IF EXISTS `Food_Listings`;")
cursor.execute("DROP TABLE IF EXISTS `Providers`;")
cursor.execute("DROP TABLE IF EXISTS `Receivers`;")

# Create tables
cursor.execute("""
CREATE TABLE `Providers` (
  `Provider_ID` INT PRIMARY KEY,
  `Name` VARCHAR(255) NOT NULL,
  `Type` VARCHAR(100),
  `Address` TEXT,
  `City` VARCHAR(100),
  `Contact` VARCHAR(50)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
""")

cursor.execute("""
CREATE TABLE `Receivers` (
  `Receiver_ID` INT PRIMARY KEY,
  `Name` VARCHAR(255) NOT NULL,
  `Type` VARCHAR(100),
  `Address` TEXT,
  `City` VARCHAR(100),
  `Contact` VARCHAR(50)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
""")

cursor.execute("""
CREATE TABLE `Food_Listings` (
  `Food_ID` INT PRIMARY KEY,
  `Food_Name` VARCHAR(120),
  `Quantity` INT,
  `Expiry_Date` DATE,
  `Provider_ID` INT,
  `Provider_Type` VARCHAR(100),
  `Location` VARCHAR(120),
  `Food_Type` VARCHAR(80),
  `Meal_Type` VARCHAR(80),
  INDEX `idx_provider` (`Provider_ID`),
  INDEX `idx_location` (`Location`),
  CONSTRAINT `fk_food_provider`
    FOREIGN KEY (`Provider_ID`) REFERENCES `Providers`(`Provider_ID`)
    ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
""")

cursor.execute("""
CREATE TABLE `Claims` (
  `Claim_ID` INT PRIMARY KEY,
  `Food_ID` INT,
  `Receiver_ID` INT,
  `Status` ENUM('Pending','Cancelled','Completed') DEFAULT 'Pending',
  `Timestamp` DATETIME,
  INDEX `idx_food` (`Food_ID`),
  INDEX `idx_receiver` (`Receiver_ID`),
  CONSTRAINT `fk_claim_food`
    FOREIGN KEY (`Food_ID`) REFERENCES `Food_Listings`(`Food_ID`)
    ON DELETE RESTRICT ON UPDATE CASCADE,
  CONSTRAINT `fk_claim_receiver`
    FOREIGN KEY (`Receiver_ID`) REFERENCES `Receivers`(`Receiver_ID`)
    ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
""")

# ---- Insert helper ----
def insert_df(df, table):
    df = df.where(pd.notnull(df), None)  # NaN → None
    df = convert_timestamps(df)          # Convert date/time
    df = df.astype(object)                # Ensure Python types
    
    # Convert numpy to native Python types for MySQL
    for col in df.columns:
        df[col] = df[col].apply(lambda x:
                                int(x) if isinstance(x, (np.int64, np.int32)) else
                                float(x) if isinstance(x, (np.float64, np.float32)) else x)
    
    cols = ", ".join([f"`{col}`" for col in df.columns])
    placeholders = ", ".join(["%s"] * len(df.columns))
    sql = f"INSERT INTO `{table}` ({cols}) VALUES ({placeholders})"
    cursor.executemany(sql, df.to_records(index=False).tolist())
    print(f"✅ Inserted {cursor.rowcount} rows into `{table}`")

# ---- Load and clean CSVs ----
prov = pd.read_csv("providers_clean.csv").dropna(subset=["Provider_ID"]).drop_duplicates(subset=["Provider_ID"])
recv = pd.read_csv("receivers_clean.csv").dropna(subset=["Receiver_ID"]).drop_duplicates(subset=["Receiver_ID"])

food = pd.read_csv("food_listings_clean.csv")
food["Food_ID"] = pd.to_numeric(food["Food_ID"], errors="coerce").astype("Int64")
food["Quantity"] = pd.to_numeric(food["Quantity"], errors="coerce").astype("Int64")
food["Provider_ID"] = pd.to_numeric(food["Provider_ID"], errors="coerce").astype("Int64")
food["Expiry_Date"] = pd.to_datetime(food["Expiry_Date"], errors="coerce").dt.date
food = food.dropna(subset=["Food_ID", "Provider_ID"]).drop_duplicates(subset=["Food_ID"])

claims = pd.read_csv("claims_clean.csv")
claims["Claim_ID"] = pd.to_numeric(claims["Claim_ID"], errors="coerce").astype("Int64")
claims["Food_ID"] = pd.to_numeric(claims["Food_ID"], errors="coerce").astype("Int64")
claims["Receiver_ID"] = pd.to_numeric(claims["Receiver_ID"], errors="coerce").astype("Int64")
claims = claims.dropna(subset=["Claim_ID", "Food_ID", "Receiver_ID"]).drop_duplicates(subset=["Claim_ID"])

# ---- Insert in safe order ----
insert_df(prov, "Providers")
insert_df(recv, "Receivers")
insert_df(food, "Food_Listings")
insert_df(claims, "Claims")

cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
conn.commit()
cursor.close()
conn.close()

print("🎉 All CSV data loaded successfully into Clever Cloud MySQL!")
