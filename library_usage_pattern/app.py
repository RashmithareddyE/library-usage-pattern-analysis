import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="Smart Library Analytics",
    page_icon="📚",
    layout="wide"
)

# =========================================================
# TITLE
# =========================================================
st.title("📚 AI-Based Smart Library Analytics System")
st.markdown("## Smart Recommendation & Usage Analytics Dashboard")

# =========================================================
# DATA FOLDER
# =========================================================
os.makedirs("data", exist_ok=True)

# =========================================================
# CSV FILE
# =========================================================
local_file = "data/library_data.csv"

# =========================================================
# REQUIRED COLUMNS
# =========================================================
required_columns = [

    "Timestamp",
    "USN",
    "Department",
    "Year",
    "Visit Date",
    "Entry Time",
    "Exit Time",
    "Purpose of Visit",
    "Book Category"
]

# =========================================================
# CREATE LOCAL FILE
# =========================================================
if not os.path.exists(local_file):

    pd.DataFrame(
        columns=required_columns
    ).to_csv(
        local_file,
        index=False
    )

# =========================================================
# GOOGLE SHEET
# =========================================================
sheet_id = "1GwocFxBzhj-Or5iqhs3ms95_8TulwN85bag1uU9z7zM"
gid = "1297665301"

url = (
    f"https://docs.google.com/spreadsheets/d/"
    f"{sheet_id}/export?format=csv&gid={gid}"
)

# =========================================================
# LOAD GOOGLE DATA
# =========================================================
try:

    google_data = pd.read_csv(url)

    google_data.columns = (
        google_data.columns.str.strip()
    )

except:

    google_data = pd.DataFrame(
        columns=required_columns
    )

# =========================================================
# KEEP ONLY REQUIRED COLUMNS
# =========================================================
google_data = google_data.reindex(
    columns=required_columns
)

# =========================================================
# LOAD LOCAL DATA
# =========================================================
local_data = pd.read_csv(local_file)

local_data = local_data.reindex(
    columns=required_columns
)

# =========================================================
# MERGE BOTH
# =========================================================
data = pd.concat(
    [google_data, local_data],
    ignore_index=True
)

# =========================================================
# CLEAN DATA
# =========================================================
data = data.fillna("")
data = data.drop_duplicates()

# =========================================================
# SIDEBAR
# =========================================================
st.sidebar.title("📂 Navigation")

page = st.sidebar.radio(

    "Select Section",

    [
        "🏠 Dashboard",
        "➕ Add Entry",
        "📊 Graphs",
        "🔁 Frequency Analysis",
        "🤖 AI Recommendations"
    ]
)

# =========================================================
# DASHBOARD
# =========================================================
if page == "🏠 Dashboard":

    st.header("📋 Complete Library Data")

    st.dataframe(
        data.reset_index(drop=True),
        use_container_width=True
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total Visits",
        len(data)
    )

    col2.metric(
        "Departments",
        data["Department"].nunique()
    )

    col3.metric(
        "Book Categories",
        data["Book Category"].nunique()
    )

    col4.metric(
        "Average Visits",
        round(
            data["USN"]
            .value_counts()
            .mean(),
            2
        )
    )

# =========================================================
# ADD ENTRY
# =========================================================
elif page == "➕ Add Entry":

    st.header("➕ Add New Entry")

    with st.form(
        "entry_form",
        clear_on_submit=True
    ):

        usn = st.text_input("USN")

        department = st.selectbox(

            "Department",

            [
                "Computer Science Engineering",
                "Electrical Engineering",
                "Mechanical Engineering",
                "Aerospace Engineering"
            ]
        )

        year = st.selectbox(

            "Year",

            [
                "1st",
                "2nd",
                "3rd",
                "4th"
            ]
        )

        visit_date = st.date_input(
            "Visit Date"
        )

        entry_time = st.time_input(
            "Entry Time"
        )

        exit_time = st.time_input(
            "Exit Time"
        )

        purpose = st.selectbox(

            "Purpose of Visit",

            [
                "Study",
                "Borrow Book",
                "Return Book",
                "Exam Preparation"
            ]
        )

        category = st.selectbox(

            "Book Category",

            [
                "Programming",
                "Data Science",
                "Mathematics",
                "Electronics",
                "Novel"
            ]
        )

        submit = st.form_submit_button(
            "Save Entry"
        )

        # =================================================
        # SAVE ENTRY
        # =================================================
        if submit:

            timestamp = datetime.now().strftime(
                "%m/%d/%Y %H:%M:%S"
            )

            new_row = pd.DataFrame({

                "Timestamp": [timestamp],

                "USN": [usn],

                "Department": [department],

                "Year": [year],

                "Visit Date": [
                    visit_date.strftime(
                        "%m/%d/%Y"
                    )
                ],

                "Entry Time": [
                    entry_time.strftime(
                        "%I:%M:%S %p"
                    )
                ],

                "Exit Time": [
                    exit_time.strftime(
                        "%I:%M:%S %p"
                    )
                ],

                "Purpose of Visit": [purpose],

                "Book Category": [category]

            })

            # LOAD OLD DATA
            old_data = pd.read_csv(local_file)

            # APPEND
            updated_data = pd.concat(
                [old_data, new_row],
                ignore_index=True
            )

            # SAVE
            updated_data.to_csv(
                local_file,
                index=False
            )

            st.success(
                "✅ Entry Saved Successfully!"
            )

            st.rerun()

# =========================================================
# GRAPHS
# =========================================================
elif page == "📊 Graphs":

    st.header("📊 Library Analytics Graphs")

    plt.style.use("ggplot")

    # =====================================================
    # CLEAN COUNTS
    # =====================================================
    dept_counts = (
        data["Department"]
        .replace("", pd.NA)
        .dropna()
        .value_counts()
    )

    category_counts = (
        data["Book Category"]
        .replace("", pd.NA)
        .dropna()
        .value_counts()
    )

    purpose_counts = (
        data["Purpose of Visit"]
        .replace("", pd.NA)
        .dropna()
        .value_counts()
    )

    # =====================================================
    # DEPARTMENT GRAPH
    # =====================================================
    st.subheader(
        "Department-wise Library Usage"
    )

    fig1, ax1 = plt.subplots(
        figsize=(10, 5)
    )

    dept_counts.plot(

        kind="bar",

        color="tomato",

        edgecolor="black",

        ax=ax1
    )

    ax1.set_ylabel(
        "Number of Students"
    )

    ax1.set_xlabel(
        "Department"
    )

    plt.xticks(rotation=20)

    for i, v in enumerate(dept_counts):

        ax1.text(
            i,
            v + 0.1,
            str(v),
            ha='center',
            fontsize=11
        )

    st.pyplot(fig1)

    # =====================================================
    # BOOK CATEGORY GRAPH
    # =====================================================
    st.subheader(
        "Book Category Popularity"
    )

    fig2, ax2 = plt.subplots(
        figsize=(10, 5)
    )

    category_counts.plot(

        kind="bar",

        color="orange",

        edgecolor="black",

        ax=ax2
    )

    ax2.set_ylabel(
        "Count"
    )

    ax2.set_xlabel(
        "Book Category"
    )

    plt.xticks(rotation=20)

    for i, v in enumerate(category_counts):

        ax2.text(
            i,
            v + 0.1,
            str(v),
            ha='center',
            fontsize=11
        )

    st.pyplot(fig2)

    # =====================================================
    # PIE CHART
    # =====================================================
    st.subheader(
        "Purpose of Visit Distribution"
    )

    fig3, ax3 = plt.subplots(
        figsize=(7, 7)
    )

    purpose_counts.plot(

        kind="pie",

        autopct="%1.1f%%",

        ax=ax3
    )

    plt.ylabel("")

    st.pyplot(fig3)

# =========================================================
# FREQUENCY ANALYSIS
# =========================================================
elif page == "🔁 Frequency Analysis":

    st.header("🔁 Student Visit Frequency")

    frequency = (
        data["USN"]
        .replace("", pd.NA)
        .dropna()
        .value_counts()
    )

    freq_df = pd.DataFrame({

        "USN": frequency.index,

        "Visits": frequency.values
    })

    st.dataframe(
        freq_df,
        use_container_width=True
    )

    fig4, ax4 = plt.subplots(
        figsize=(10, 5)
    )

    frequency.plot(

        kind="bar",

        color="purple",

        edgecolor="black",

        ax=ax4
    )

    ax4.set_ylabel("Visits")
    ax4.set_xlabel("USN")

    plt.xticks(rotation=90)

    for i, v in enumerate(frequency):

        ax4.text(
            i,
            v + 0.1,
            str(v),
            ha='center'
        )

    st.pyplot(fig4)

# =========================================================
# AI RECOMMENDATIONS
# =========================================================
elif page == "🤖 AI Recommendations":

    st.header("🤖 Smart Book Recommendations")

    BOOK_PLUGIN_DB = {

        "Programming": [
            "Clean Code",
            "Python Crash Course",
            "The Pragmatic Programmer"
        ],

        "Data Science": [
            "Hands-On Machine Learning",
            "Python for Data Analysis",
            "Data Science Handbook"
        ],

        "Mathematics": [
            "Engineering Mathematics",
            "Linear Algebra",
            "Calculus Made Easy"
        ],

        "Electronics": [
            "Digital Electronics",
            "Electric Circuits",
            "Microelectronics"
        ],

        "Novel": [
            "1984",
            "The Alchemist",
            "The Great Gatsby"
        ]
    }

    usn_input = st.text_input(
        "Enter Student USN"
    )

    if st.button(
        "Generate Recommendation"
    ):

        student_data = data[
            data["USN"] == usn_input
        ]

        if not student_data.empty:

            total_visits = len(student_data)

            st.success(
                f"Total Visits: {total_visits}"
            )

            favorite_categories = (

                student_data[
                    "Book Category"
                ]

                .replace("", pd.NA)
                .dropna()
                .value_counts()
            )

            st.subheader(
                "📚 Interested Categories"
            )

            for category in favorite_categories.index:

                st.write(
                    f"✅ {category}"
                )

            st.subheader(
                "📖 Recommended Books"
            )

            for category in favorite_categories.index:

                st.markdown(
                    f"### {category}"
                )

                books = BOOK_PLUGIN_DB.get(
                    category,
                    []
                )

                for book in books:

                    st.write(
                        f"📘 {book}"
                    )

        else:

            st.error(
                "❌ No Student Found"
            )