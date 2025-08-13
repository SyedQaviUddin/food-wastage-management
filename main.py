import streamlit as st
import pandas as pd
import mysql.connector
from mysql.connector import Error
import sqlite3
import streamlit as st

@st.cache_resource
def get_conn():
    return sqlite3.connect("food wastage system/food_system.db", check_same_thread=False)

# --- DB connection (cached) ---
#@st.cache_resource
#def get_conn():
 #   return mysql.connector.connect(
  #      host="127.0.0.1",          # or "localhost"
   #     user="root",               # your MySQL username
    #    password="88018035838686$Aa", # your MySQL password
     #   database="food",           
      #  auth_plugin='mysql_native_password' 
   # )

def run_query(query, params=None):
    conn = get_conn()
    cur = conn.cursor(dictionary=True)
    cur.execute(query, params or ())
    rows = cur.fetchall()
    cur.close()
    return pd.DataFrame(rows)

def run_commit(query, params=None):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(query, params or ())
    conn.commit()
    lastrow = cur.lastrowid
    cur.close()
    return lastrow

# Helper to get distinct values for filters
def get_distinct_values(table, column):
    df = run_query(f"SELECT DISTINCT `{column}` FROM `{table}` WHERE `{column}` IS NOT NULL")
    if df.empty:
        return []
    return sorted(df[df.columns[0]].dropna().astype(str).tolist())






def browse_listings():
    st.header("Browse Listings")

    # Filters
    cities = ["All"] + get_distinct_values("Food_Listings", "Location")
    providers = ["All"] + get_distinct_values("Providers", "Name")
    food_types = get_distinct_values("Food_Listings", "Food_Type")
    meal_types = ["All"] + get_distinct_values("Food_Listings", "Meal_Type")

    col1, col2, col3 = st.columns(3)
    with col1:
        city = st.selectbox("City", cities)
    with col2:
        provider = st.selectbox("Provider", providers)
    with col3:
        food_type = st.multiselect("Food Type", options=food_types)

    meal = st.selectbox("Meal Type", meal_types)

    # Build query with parameterized WHERE clauses
    base_q = """
      SELECT f.Food_ID, f.Food_Name, f.Quantity, f.Expiry_Date, f.Meal_Type, f.Food_Type, f.Location,
             p.Provider_ID, p.Name as Provider_Name, p.Contact as Provider_Contact, p.Address as Provider_Address
      FROM Food_Listings f
      JOIN Providers p ON f.Provider_ID = p.Provider_ID
    """
    where = []
    params = []
    if city and city != "All":
        where.append("f.Location = %s"); params.append(city)
    if provider and provider != "All":
        where.append("p.Name = %s"); params.append(provider)
    if food_type:
        where.append("f.Food_Type IN (" + ",".join(["%s"]*len(food_type)) + ")")
        params.extend(food_type)
    if meal and meal != "All":
        where.append("f.Meal_Type = %s"); params.append(meal)

    if where:
        base_q += " WHERE " + " AND ".join(where)
    base_q += " ORDER BY f.Expiry_Date ASC;"

    df = run_query(base_q, tuple(params))
    st.write(f"**{len(df)} listings found**")
    st.dataframe(df)

    # Show contact details inside an expander for each listing or allow selection
    if not df.empty:
        sel = st.selectbox("Select a listing to see details / claim", df['Food_ID'].astype(str).tolist())
        row = df[df['Food_ID']==int(sel)].iloc[0]
        st.subheader(row['Food_Name'])
        st.markdown(f"- **Quantity:** {row['Quantity']}")
        st.markdown(f"- **Expiry Date:** {row['Expiry_Date']}")
        st.markdown(f"- **Provider:** {row['Provider_Name']} (ID: {row['Provider_ID']})")
        with st.expander("Provider contact details"):
            st.markdown(f"**Contact:** {row['Provider_Contact']}")
            st.markdown(f"**Address:** {row['Provider_Address']}")

        # Claim form
        st.write("---")
        with st.form("claim_form"):
            receiver_id = st.text_input("Enter your Receiver ID")
            submit = st.form_submit_button("Submit Claim")
            if submit:
                if not receiver_id:
                    st.error("Please provide your Receiver ID.")
                else:
                    insert_q = "INSERT INTO Claims (Food_ID, Receiver_ID, Status, Timestamp) VALUES (%s,%s,'Pending',NOW());"
                    run_commit(insert_q, (int(sel), int(receiver_id)))
                    st.success("Claim submitted. Provider will be notified.")




def admin_food_listings():
    st.header("Food Listings — Add / Edit / Delete")

    # --- Add new listing ---
    with st.expander("Add new listing"):
        with st.form("add_food"):
            name = st.text_input("Food Name")
            qty = st.number_input("Quantity", min_value=1, value=1)
            expiry = st.date_input("Expiry Date")
            provider_id = st.selectbox("Provider", get_distinct_values("Providers", "Provider_ID"))
            provider_type = st.text_input("Provider Type")
            location = st.text_input("Location")
            food_type = st.text_input("Food Type")
            meal_type = st.text_input("Meal Type")
            submit_add = st.form_submit_button("Add Listing")
            if submit_add:
                q = """INSERT INTO Food_Listings
                       (Food_Name, Quantity, Expiry_Date, Provider_ID, Provider_Type, Location, Food_Type, Meal_Type)
                       VALUES (%s,%s,%s,%s,%s,%s,%s,%s);"""
                run_commit(q, (name, int(qty), expiry.strftime("%Y-%m-%d"), int(provider_id), provider_type, location, food_type, meal_type))
                st.success("Listing added.")

    # --- Edit existing listing ---
    st.write("---")
    df = run_query("SELECT Food_ID, Food_Name FROM Food_Listings ORDER BY Food_ID DESC;")
    if not df.empty:
        chosen = st.selectbox("Choose listing to edit", df['Food_ID'].astype(str).tolist())
        if chosen:
            rec = run_query("SELECT * FROM Food_Listings WHERE Food_ID=%s", (int(chosen),)).iloc[0]
            with st.form("edit_food"):
                name = st.text_input("Food Name", value=rec['Food_Name'])
                qty = st.number_input("Quantity", min_value=0, value=int(rec['Quantity']))
                # convert rec['Expiry_Date'] to date if string etc.
                expiry = st.date_input("Expiry Date", value=pd.to_datetime(rec['Expiry_Date']).date() if rec['Expiry_Date'] else None)
                provider_id = st.text_input("Provider_ID", value=str(rec['Provider_ID']))
                provider_type = st.text_input("Provider Type", value=rec.get('Provider_Type',''))
                location = st.text_input("Location", value=rec.get('Location',''))
                food_type = st.text_input("Food Type", value=rec.get('Food_Type',''))
                meal_type = st.text_input("Meal Type", value=rec.get('Meal_Type',''))
                submit_edit = st.form_submit_button("Save changes")
                if submit_edit:
                    upd_q = """
                      UPDATE Food_Listings SET Food_Name=%s, Quantity=%s, Expiry_Date=%s,
                          Provider_ID=%s, Provider_Type=%s, Location=%s, Food_Type=%s, Meal_Type=%s
                      WHERE Food_ID=%s;
                    """
                    run_commit(upd_q, (name, int(qty), expiry.strftime("%Y-%m-%d"), int(provider_id), provider_type, location, food_type, meal_type, int(chosen)))
                    st.success("Listing updated.")

    # --- Delete listing ---
    st.write("---")
    del_id = st.number_input("Enter Food_ID to delete", min_value=0, value=0)
    if st.button("Delete listing"):
        if del_id > 0:
            run_commit("DELETE FROM Food_Listings WHERE Food_ID=%s", (int(del_id),))
            st.success(f"Deleted listing {del_id}.")




ANALYTICS_QUERIES = {
    "Provider count per city": "SELECT City, COUNT(*) AS provider_count FROM Providers GROUP BY City ORDER BY provider_count DESC;",
    "Receiver count per city": "SELECT City, COUNT(*) AS receiver_count FROM Receivers GROUP BY City;",
    "Most contributing provider type": """SELECT p.Type AS provider_type, SUM(f.Quantity) AS total_qty
                                         FROM Providers p JOIN Food_Listings f ON p.Provider_ID=f.Provider_ID
                                         GROUP BY p.Type ORDER BY total_qty DESC LIMIT 10;""",
    "Total available food quantity": "SELECT SUM(Quantity) AS total_available FROM Food_Listings;",
    "City with most listings": "SELECT Location AS city, COUNT(*) AS listings FROM Food_Listings GROUP BY Location ORDER BY listings DESC LIMIT 10;",
    "Most common food types": "SELECT Food_Type, COUNT(*) AS freq FROM Food_Listings GROUP BY Food_Type ORDER BY freq DESC LIMIT 10;",
    "Claims per food item": "SELECT f.Food_ID, f.Food_Name, COUNT(c.Claim_ID) AS claim_count FROM Food_Listings f LEFT JOIN Claims c ON f.Food_ID=c.Food_ID GROUP BY f.Food_ID ORDER BY claim_count DESC LIMIT 20;",
    "Provider with most completed claims": "SELECT p.Provider_ID, p.Name, COUNT(c.Claim_ID) AS completed_claims FROM Providers p JOIN Food_Listings f ON p.Provider_ID=f.Provider_ID JOIN Claims c ON f.Food_ID=c.Food_ID WHERE c.Status='Completed' GROUP BY p.Provider_ID ORDER BY completed_claims DESC LIMIT 10;",
    "Claim status percent": "SELECT Status, COUNT(*)*100.0/(SELECT COUNT(*) FROM Claims) AS percent FROM Claims GROUP BY Status;",
    "Avg quantity claimed per receiver": "SELECT c.Receiver_ID, r.Name, AVG(f.Quantity) AS avg_quantity FROM Claims c JOIN Food_Listings f ON c.Food_ID=f.Food_ID JOIN Receivers r ON c.Receiver_ID=r.Receiver_ID GROUP BY c.Receiver_ID ORDER BY avg_quantity DESC LIMIT 20;",
    "Most claimed meal type": "SELECT f.Meal_Type, COUNT(c.Claim_ID) AS times_claimed FROM Food_Listings f JOIN Claims c ON f.Food_ID=c.Food_ID GROUP BY f.Meal_Type ORDER BY times_claimed DESC;",
    "Total quantity donated by provider": "SELECT p.Provider_ID, p.Name, SUM(f.Quantity) AS total_donated FROM Providers p JOIN Food_Listings f ON p.Provider_ID=f.Provider_ID GROUP BY p.Provider_ID ORDER BY total_donated DESC LIMIT 20;",
    "Listings near expiry (next 2 days)": "SELECT * FROM Food_Listings WHERE Expiry_Date BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 2 DAY) ORDER BY Expiry_Date ASC;",
    "Top locations by quantity": "SELECT Location, SUM(Quantity) AS total_qty FROM Food_Listings GROUP BY Location ORDER BY total_qty DESC LIMIT 10;",
    "Receivers with most claims": "SELECT r.Receiver_ID, r.Name, COUNT(c.Claim_ID) AS num_claims FROM Receivers r JOIN Claims c ON r.Receiver_ID=c.Receiver_ID GROUP BY r.Receiver_ID ORDER BY num_claims DESC LIMIT 20;"
}

def analytics_page():
    st.header("Analytics")
    for title, q in ANALYTICS_QUERIES.items():
        with st.expander(title):
            df = run_query(q)
            st.write(df)
            # If small & suitable, show bar chart for first numeric column vs label column
            if not df.empty and df.shape[1] >= 2:
                # heuristics: if second column numeric show bar_chart
                col2 = df.columns[1]
                if pd.api.types.is_numeric_dtype(df[col2]):
                    try:
                        chart_df = df.set_index(df.columns[0])[col2]
                        st.bar_chart(chart_df)
                    except Exception:
                        pass






def provider_portal():
    st.header("Provider Portal — manage your listings")
    provider_id = st.text_input("Provider ID")
    contact = st.text_input("Provider Contact (for verification)")

    if st.button("Login as Provider"):
        df = run_query("SELECT * FROM Providers WHERE Provider_ID=%s AND Contact=%s", (provider_id, contact))
        if df.empty:
            st.error("Invalid Provider ID or contact.")
            return
        st.success(f"Logged in as {df.iloc[0]['Name']}")
        st.session_state['provider_id'] = int(provider_id)

    if st.session_state.get('provider_id'):
        pid = st.session_state['provider_id']
        st.subheader("Your Listings")
        my_listings = run_query("SELECT * FROM Food_Listings WHERE Provider_ID=%s", (pid,))
        st.dataframe(my_listings)
        # select listing to edit/delete
        if not my_listings.empty:
            sel = st.selectbox("Select your Food_ID to edit/delete", my_listings['Food_ID'].astype(str).tolist())
            rec = my_listings[my_listings['Food_ID'] == int(sel)].iloc[0]
            with st.form("provider_edit"):
                name = st.text_input("Food Name", value=rec['Food_Name'])
                qty = st.number_input("Quantity", value=int(rec['Quantity']), min_value=0)
                expiry = st.date_input("Expiry Date", value=pd.to_datetime(rec['Expiry_Date']).date() if rec['Expiry_Date'] else None)
                submit = st.form_submit_button("Save")
                if submit:
                    run_commit("""UPDATE Food_Listings SET Food_Name=%s, Quantity=%s, Expiry_Date=%s WHERE Food_ID=%s""",
                               (name, int(qty), expiry.strftime("%Y-%m-%d"), int(sel)))
                    st.success("Updated listing.")
            if st.button("Delete selected listing"):
                run_commit("DELETE FROM Food_Listings WHERE Food_ID=%s", (int(sel),))
                st.success("Listing deleted.")




def admin_providers():
    st.header("Providers — Add / Edit / Delete")

    # --- Add new provider ---
    with st.expander("Add new provider"):
        with st.form("add_provider"):
            name = st.text_input("Provider Name")
            ptype = st.text_input("Type")  # Restaurant, Grocery Store, etc.
            address = st.text_area("Address")
            city = st.text_input("City")
            contact = st.text_input("Contact")
            submit_add = st.form_submit_button("Add Provider")
            if submit_add:
                q = """INSERT INTO Providers (Name, Type, Address, City, Contact)
                       VALUES (%s, %s, %s, %s, %s);"""
                run_commit(q, (name, ptype, address, city, contact))
                st.success("Provider added.")

    # --- Edit existing provider ---
    st.write("---")
    df = run_query("SELECT Provider_ID, Name FROM Providers ORDER BY Provider_ID DESC;")
    if not df.empty:
        chosen = st.selectbox("Choose provider to edit", df['Provider_ID'].astype(str).tolist())
        if chosen:
            rec = run_query("SELECT * FROM Providers WHERE Provider_ID=%s", (int(chosen),)).iloc[0]
            with st.form("edit_provider"):
                name = st.text_input("Provider Name", value=rec['Name'])
                ptype = st.text_input("Type", value=rec['Type'])
                address = st.text_area("Address", value=rec['Address'])
                city = st.text_input("City", value=rec['City'])
                contact = st.text_input("Contact", value=rec['Contact'])
                submit_edit = st.form_submit_button("Save changes")
                if submit_edit:
                    upd_q = """UPDATE Providers 
                               SET Name=%s, Type=%s, Address=%s, City=%s, Contact=%s
                               WHERE Provider_ID=%s;"""
                    run_commit(upd_q, (name, ptype, address, city, contact, int(chosen)))
                    st.success("Provider updated.")

    # --- Delete provider ---
    st.write("---")
    del_id = st.number_input("Enter Provider_ID to delete", min_value=0, value=0)
    if st.button("Delete provider"):
        if del_id > 0:
            run_commit("DELETE FROM Providers WHERE Provider_ID=%s", (int(del_id),))
            st.success(f"Deleted provider {del_id}.")






def admin_receivers():
    st.header("Receivers — Add / Edit / Delete")

    # --- Add new receiver ---
    with st.expander("Add new receiver"):
        with st.form("add_receiver"):
            name = st.text_input("Receiver Name")
            rtype = st.text_input("Type")  # NGO, Individual, etc.
            city = st.text_input("City")
            contact = st.text_input("Contact")
            submit_add = st.form_submit_button("Add Receiver")
            if submit_add:
                q = """INSERT INTO Receivers (Name, Type, City, Contact)
                       VALUES (%s, %s, %s, %s);"""
                run_commit(q, (name, rtype, city, contact))
                st.success("Receiver added.")

    # --- Edit existing receiver ---
    st.write("---")
    df = run_query("SELECT Receiver_ID, Name FROM Receivers ORDER BY Receiver_ID DESC;")
    if not df.empty:
        chosen = st.selectbox("Choose receiver to edit", df['Receiver_ID'].astype(str).tolist())
        if chosen:
            rec = run_query("SELECT * FROM Receivers WHERE Receiver_ID=%s", (int(chosen),)).iloc[0]
            with st.form("edit_receiver"):
                name = st.text_input("Receiver Name", value=rec['Name'])
                rtype = st.text_input("Type", value=rec['Type'])
                city = st.text_input("City", value=rec['City'])
                contact = st.text_input("Contact", value=rec['Contact'])
                submit_edit = st.form_submit_button("Save changes")
                if submit_edit:
                    upd_q = """UPDATE Receivers 
                               SET Name=%s, Type=%s, City=%s, Contact=%s
                               WHERE Receiver_ID=%s;"""
                    run_commit(upd_q, (name, rtype, city, contact, int(chosen)))
                    st.success("Receiver updated.")

    # --- Delete receiver ---
    st.write("---")
    del_id = st.number_input("Enter Receiver_ID to delete", min_value=0, value=0)
    if st.button("Delete receiver"):
        if del_id > 0:
            run_commit("DELETE FROM Receivers WHERE Receiver_ID=%s", (int(del_id),))
            st.success(f"Deleted receiver {del_id}.")


# Main application logic
st.set_page_config(page_title="Local Food Wastage System", layout="wide")
st.title(" Food Wastage Management System")




PAGES = {
    "Home": lambda: st.subheader("Welcome to Local Food Wastage System " "\n"
    "Use the sidebar to navigate through the system."
    ""),
   
    "Browse Listings": browse_listings,
    "Provider Portal": provider_portal,
    "Receiver Portal": lambda: admin_receivers(),
    "Admin - Providers": lambda: admin_providers(),   # implement admin_providers similar to admin_food_listings
    "Admin - Listings": admin_food_listings,
    "Analytics": analytics_page
}

choice = st.sidebar.selectbox("Menu", list(PAGES.keys()))
PAGES[choice]()

