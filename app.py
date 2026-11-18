
import base64
import streamlit as st
import csv
import os
from datetime import date

APP_DIR = os.path.dirname(os.path.abspath(__file__))
LOGO = os.path.join(APP_DIR, "christ_logo.png")
BACKGROUND_IMAGE = os.path.join(APP_DIR, "campus_background.png")

with open(BACKGROUND_IMAGE, "rb") as image_file:
    BACKGROUND_BASE64 = base64.b64encode(image_file.read()).decode("ascii")

# -------------------------------
# PAGE CONFIGURATION
# -------------------------------

st.set_page_config(
    page_title="CHRIST EcoSmart",
    page_icon=LOGO,
    layout="wide"
)

st.markdown(
    f"""
    <style>
    div[data-testid="stAppViewContainer"] {{
        background-image:
            linear-gradient(rgba(7, 22, 14, 0.88), rgba(7, 22, 14, 0.88)),
            url("data:image/png;base64,{BACKGROUND_BASE64}");
        background-position: right center;
        background-size: contain;
        background-repeat: no-repeat;
        background-color: #0b140e;
        background-attachment: fixed;
    }}
    section[data-testid="stSidebar"] {{
        background-color: rgba(18, 35, 25, 0.9);
    }}
    header[data-testid="stHeader"] {{
        background-color: transparent;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

FILE = "waste_records.csv"

LOCATIONS = [
    "Food Court",
    "Block I",
    "Block II",
    "Block III",
    "Central Block",
    "Auditorium",
    "Library",
    "Basketball Court"
]

CATEGORIES = [
    "Wet Waste",
    "Dry Waste",
    "Plastic",
    "Paper",
    "E-waste"
]

# -------------------------------
# CSV FILE MANAGEMENT
# -------------------------------

def create_file():
    if not os.path.exists(FILE):
        with open(FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "Date", "Location", "Category",
                "Quantity", "Status"
            ])


def load_data():
    create_file()

    with open(FILE, "r") as f:
        reader = csv.DictReader(f)
        return list(reader)


def save_data(record):
    create_file()

    record_values = {
        "Date": str(record["Date"]),
        "Location": str(record["Location"]),
        "Category": str(record["Category"]),
        "Quantity": str(record["Quantity"]),
        "Status": str(record["Status"])
    }

    with open(FILE, "r", newline="") as f:
        if record_values in csv.DictReader(f):
            return False

    with open(FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            record_values["Date"],
            record_values["Location"],
            record_values["Category"],
            record_values["Quantity"],
            record_values["Status"]
        ])
    return True


# -------------------------------
# LOAD WASTE RECORDS
# -------------------------------

records = load_data()

# -------------------------------
# SIDEBAR
# -------------------------------

st.sidebar.image(LOGO, use_container_width=True)
st.sidebar.title("CHRIST EcoSmart")
st.sidebar.write("Campus Waste Management")

page = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "Add Waste", "Reports", "About"]
)

st.sidebar.markdown("---")
st.sidebar.caption("CHRIST University | Bengaluru")

_, logo_column = st.columns([8, 1])
with logo_column:
    st.image(LOGO, width=180)

# -------------------------------
# DASHBOARD
# -------------------------------

if page == "Dashboard":

    st.markdown("""
    <style>
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(76, 175, 80, 0.18), rgba(201, 162, 39, 0.10));
        border: 1px solid rgba(76, 175, 80, 0.45);
        border-radius: 12px;
        padding: 10px 8px;
    }
    div[data-testid="stMetricValue"] > div {
        font-size: 1.35rem;
    }
    </style>
    """, unsafe_allow_html=True)

    st.title("CHRIST EcoSmart")
    st.subheader("Campus Waste Management Dashboard")

    total_waste = 0
    collected = 0
    pending = 0

    for r in records:
        quantity = float(r["Quantity"])
        total_waste += quantity

        if r["Status"] == "Collected":
            collected += quantity
        else:
            pending += quantity

    # Dashboard metrics

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Waste", f"{total_waste:.1f} kg")
    col2.metric("Collected", f"{collected:.1f} kg")
    col3.metric("Pending", f"{pending:.1f} kg")
    col4.metric("Locations", len(LOCATIONS))

    st.markdown("---")

    if records:

        # Location-wise waste calculation

        location_waste = {}

        for location in LOCATIONS:
            location_waste[location] = 0

        for r in records:
            location = r["Location"]
            quantity = float(r["Quantity"])

            if location in location_waste:
                location_waste[location] += quantity

        # Category-wise waste calculation

        category_waste = {}

        for category in CATEGORIES:
            category_waste[category] = 0

        for r in records:
            category = r["Category"]
            quantity = float(r["Quantity"])

            if category in category_waste:
                category_waste[category] += quantity

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Waste by Location")

            st.bar_chart({
                "Location": list(location_waste.keys()),
                "Waste (kg)": list(location_waste.values())
            }, x="Location", y="Waste (kg)", color="#4CAF50")

        with col2:
            st.subheader("Waste Category Distribution")

            st.bar_chart({
                "Category": list(category_waste.keys()),
                "Waste (kg)": list(category_waste.values())
            }, x="Category", y="Waste (kg)", color="#4CAF50")

        # Highest waste generating location

        highest_location = max(
            location_waste,
            key=location_waste.get
        )

        st.markdown("---")
        st.subheader("Highest Waste Generating Location")

        st.success(
            f"{highest_location} - "
            f"{location_waste[highest_location]:.1f} kg"
        )

        # Recent records

        st.markdown("---")
        st.subheader("Recent Waste Records")

        recent = records[-5:][::-1]

        st.dataframe(
            recent,
            use_container_width=True,
            hide_index=True
        )

    else:
        st.info("No waste records available. Please add waste records.")

# -------------------------------
# ADD WASTE
# -------------------------------

elif page == "Add Waste":

    st.title("➕ Add Waste Record")

    with st.form("waste_form"):

        waste_date = st.date_input(
            "Date",
            value=date.today()
        )

        location = st.selectbox(
            "Select Campus Location",
            LOCATIONS
        )

        category = st.selectbox(
            "Select Waste Category",
            CATEGORIES
        )

        quantity = st.number_input(
            "Waste Quantity (kg)",
            min_value=0.1,
            step=0.5
        )

        status = st.selectbox(
            "Collection Status",
            ["Pending", "Collected"]
        )

        submit = st.form_submit_button("Save Waste Record")

        if submit:

            record = {
                "Date": str(waste_date),
                "Location": location,
                "Category": category,
                "Quantity": quantity,
                "Status": status
            }

            if save_data(record):
                st.success("Waste record added successfully!")
            else:
                st.warning("This waste record already exists.")

# -------------------------------
# REPORTS
# -------------------------------

elif page == "Reports":

    st.title("📊 Waste Management Reports")

    if records:

        st.subheader("All Waste Records")

        st.dataframe(
            records,
            use_container_width=True,
            hide_index=True
        )

        # Location summary

        st.subheader("Location-wise Waste Summary")

        for location in LOCATIONS:

            total = 0

            for r in records:
                if r["Location"] == location:
                    total += float(r["Quantity"])

            if total > 0:
                st.write(f"**{location}:** {total:.1f} kg")

        # Download CSV

        with open(FILE, "rb") as f:
            st.download_button(
                "Download Waste Records (CSV)",
                data=f,
                file_name="waste_records.csv",
                mime="text/csv"
            )

    else:
        st.info("No reports available yet.")

# -------------------------------
# ABOUT
# -------------------------------

elif page == "About":

    st.title("About CHRIST EcoSmart")

    st.write("""
    CHRIST EcoSmart is a campus waste management application
    developed using Python and Streamlit.

    The application helps the university:

    1. Record waste generation.
    2. Categorize different types of waste.
    3. Monitor waste generation by location.
    4. Track waste collection status.
    5. Identify high waste-generating areas.
    6. Generate waste management reports.

    **Technologies Used:**
    - Python
    - Streamlit
    - CSV File Storage

    **Objective:**

    To encourage proper waste management and promote
    a cleaner and greener campus environment.
    """)
