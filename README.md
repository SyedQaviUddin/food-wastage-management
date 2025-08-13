# 🍽️ Local Food Wastage Management System

A **Streamlit-based web application** that connects **food providers** and **receivers** to reduce food wastage.  
It uses a **MySQL database** to store and manage providers, receivers, food listings, and claims.  
Includes **analytics**, **CRUD operations**, and **filters** for efficient donation matching.

---

## 🚀 Features
- 📌 **Browse Food Listings** with filters by city, provider type, and food type.
- 📞 View **provider and receiver contact details** in listings/claims.
- ✏️ Full **CRUD operations** (Add, Edit, Delete) for:
  - Providers
  - Receivers
  - Food Listings
- 📊 **Analytics Dashboard** with 15 SQL queries displayed as tables and charts.
- 📈 Visual insights into:
  - Top providers
  - Claim status distribution
  - Listings nearing expiry
  - Quantity distributions
- 🔒 Role-based access (Admin, Provider, Receiver).

---

## 🗂️ Project Structure
📁 food-wastage-management
├── main.py # Streamlit app

├── data_insert.sql # MySQL data to import in workbench

├── queries.sql # MySQL file with all queries

├── providers_clean.csv # Sample data

├── receivers_clean.csv

├── food_listings_clean.csv

├── claims_clean.csv

├── README.md

└── LICENSE


## ⚙️ Installation & Setup
1. **Clone the repository**:
   ```bash
   git clone https://github.com/SyedQaviUddin/food-wastage-management.git
   cd food-wastage-management
Install dependencies:

Copy code
pip install -r requirements.txt
**Setup Database:**

Create a MySQL database named food.

Import data_insert.sql into your MySQL server:


mysql -u root -p food < food_script.sql

**Run the App:**
streamlit run main.py



## 📦 Deployment
To deploy on Streamlit Community Cloud:

Push this project to a public GitHub repository.

Connect GitHub to Streamlit Cloud.

Set main.py as the entry point.

Provide MySQL connection details in secrets.toml or switch to SQLite.


## 📜 License
This project is licensed under the MIT License – see the LICENSE file for details.



## 📧 Contact
For queries or suggestions, reach out at  > sqavi037@gmail.com <
