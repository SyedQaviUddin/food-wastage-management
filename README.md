## 🍽️ Local Food Wastage Management System
A Streamlit-based web application that connects food providers and receivers to reduce food wastage.
It uses a SQLite database (food_system.db) to store and manage providers, receivers, food listings, and claims.
Includes analytics, CRUD operations, and filters for efficient donation matching — all without requiring a MySQL server.

# 🚀 Features
📌 Browse Food Listings with filters by city, provider type, and food type.

📞 View provider and receiver contact details in listings/claims.

✏️ Full CRUD operations (Add, Edit, Delete) for:

Providers

Receivers

Food Listings

## 📊 Analytics Dashboard with 15 SQL queries displayed as tables and charts.

# 📈 Visual insights into:

Top providers

Claim status distribution

Listings nearing expiry

Quantity distributions

# 🔒 Role-based access (Admin, Provider, Receiver).

# 💾 Uses SQLite for easy deployment (no external DB setup needed).

## 🗂️ Project Structure

📁 food-wastage-management

├── main.py                 # Streamlit app (SQLite version)

├── food_system.db          # SQLite database file

├── providers_clean.csv     # Sample data

├── receivers_clean.csv

├── food_listings_clean.csv

├── claims_clean.csv

├── README.md

└── LICENSE

## ⚙️ Installation & Setup

1️⃣ Clone the repository

git clone https://github.com/SyedQaviUddin/food-wastage-management.git
cd food-wastage-management

2️⃣ Install dependencies

pip install -r requirements.txt

3️⃣ Create & Populate SQLite Database
Run the script to create food_system.db and insert data from CSVs:

python load_csv_to_sqlite.py
4️⃣ Run the App

streamlit run main.py
## 📦 Deployment
Deploy on Streamlit Community Cloud:

Push this project to a public GitHub repository.

Connect GitHub to Streamlit Cloud.

Set main.py as the entry point.

Make sure food_system.db is included in the repo (or generate it on startup from CSVs).

📜 License
This project is licensed under the MIT License – see the LICENSE file for details.

📧 Contact
For queries or suggestions, reach out at sqavi037@gmail.com
