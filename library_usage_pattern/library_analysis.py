import pandas as pd
import matplotlib.pyplot as plt #streamlit
import os #streamlit run app.py
import requests

# =========================
# GOOGLE SHEET
# =========================
sheet_id = "1GwocFxBzhj-Or5iqhs3ms95_8TulwN85bag1uU9z7zM"
gid = "1297665301"

url = (
    f"https://docs.google.com/spreadsheets/d/"
    f"{sheet_id}/export?format=csv&gid={gid}"
)

# =========================
# LOAD DATA
# =========================
data = pd.read_csv(url)

data.columns = data.columns.str.strip()

# Create reports folder
os.makedirs("reports", exist_ok=True)

# =========================
# PRINT RESPONSE DATA
# =========================
print("\n========== 📋 GOOGLE FORM RESPONSES ==========\n")

print(data)

print("\nTotal Responses Received:", len(data))

print("\n=============================================\n")

# =========================
# TIME PROCESSING
# =========================
data["Entry DateTime"] = pd.to_datetime(
    data["Visit Date"].astype(str)
    + " "
    + data["Entry Time"].astype(str),
    errors='coerce'
)

data["Exit DateTime"] = pd.to_datetime(
    data["Visit Date"].astype(str)
    + " "
    + data["Exit Time"].astype(str),
    errors='coerce'
)

# Remove invalid rows
data = data.dropna(
    subset=["Entry DateTime", "Exit DateTime"]
)

# =========================
# STUDY HOURS
# =========================
data["Study Hours"] = (
    data["Exit DateTime"]
    - data["Entry DateTime"]
).dt.total_seconds() / 3600

# Remove negative values
data["Study Hours"] = (
    data["Study Hours"].clip(lower=0)
)

# =========================
# ANALYSIS
# =========================
dept_counts = (
    data["Department"].value_counts()
)

purpose_counts = (
    data["Purpose of Visit"].value_counts()
)

book_counts = (
    data["Book Category"].value_counts()
)

print("\n========== 📊 ANALYSIS REPORT ==========")

print("\nTotal Visits:", len(data))

print(
    "\nAverage Study Hours:",
    round(data["Study Hours"].mean(), 2)
)

print(
    "\nMaximum Study Hours:",
    round(data["Study Hours"].max(), 2)
)

print(
    "Minimum Study Hours:",
    round(data["Study Hours"].min(), 2)
)

print("\nMost Active Department:")

print(
    dept_counts.idxmax(),
    "->",
    dept_counts.max(),
    "visits"
)

print("\nMost Common Purpose of Visit:")

print(
    purpose_counts.idxmax(),
    "->",
    purpose_counts.max()
)

print("\nMost Popular Book Category:")

print(
    book_counts.idxmax(),
    "->",
    book_counts.max()
)

print("\n=======================================")

# =========================
# FREQUENCY ANALYSIS
# =========================
print("\n========== 🔁 FREQUENCY ANALYSIS ==========\n")

visit_frequency = (
    data["USN"].value_counts()
)

print(visit_frequency)

# Save frequency report
visit_frequency.to_csv(
    "reports/usn_frequency_report.csv"
)

print(
    "\n✅ Frequency report saved successfully!"
)

# =========================
# PLUGIN: BOOK RECOMMENDATION ENGINE
# Uses Google Books API with fallback to curated local plugin database
# =========================

# --- LOCAL PLUGIN DATABASE (Fallback) ---
BOOK_PLUGIN_DB = {
    "Programming": [
        "Clean Code by Robert C. Martin",
        "The Pragmatic Programmer by Andrew Hunt",
        "Introduction to Algorithms by Thomas H. Cormen",
        "Python Crash Course by Eric Matthes",
    ],
    "Data Science": [
        "Hands-On Machine Learning with Scikit-Learn by Aurélien Géron",
        "Python for Data Analysis by Wes McKinney",
        "The Data Science Handbook by Field Cady",
        "Data Science from Scratch by Joel Grus",
    ],
    "Mathematics": [
        "Engineering Mathematics by B.S. Grewal",
        "Higher Engineering Mathematics by H.K. Dass",
        "Advanced Engineering Mathematics by Erwin Kreyszig",
        "Linear Algebra and Its Applications by Gilbert Strang",
    ],
    "Electronics": [
        "Digital Electronics by R.P. Jain",
        "Electronic Devices and Circuit Theory by Robert Boylestad",
        "Fundamentals of Electric Circuits by Charles Alexander",
        "Microelectronics by Sedra & Smith",
    ],
    "Novel": [
        "To Kill a Mockingbird by Harper Lee",
        "The Alchemist by Paulo Coelho",
        "1984 by George Orwell",
        "The Great Gatsby by F. Scott Fitzgerald",
    ],
}


def recommend_books_plugin(category):
    """
    Book Recommendation Plugin:
    Step 1 - Try Google Books API (live).
    Step 2 - If API fails or returns empty, use local plugin database.
    """
    recommendations = []

    # --- PLUGIN STEP 1: Try Google Books API ---
    try:
        category_mapping = {
            "Programming":
                "Python programming Java C++ coding software engineering",
            "Data Science":
                "Data Science Python Machine Learning Deep Learning",
            "Mathematics":
                "Engineering Mathematics Algebra Calculus Linear Algebra",
            "Electronics":
                "Digital Electronics Circuits Electronic Devices",
            "Novel":
                "Best fiction novels literature bestselling story books",
        }

        search_query = category_mapping.get(category, category)

        api_url = (
            "https://www.googleapis.com/books/v1/volumes"
            f"?q={search_query}"
            "&maxResults=4"
            "&printType=books"
        )

        response = requests.get(api_url, timeout=5)
        data_json = response.json()

        if "items" in data_json:
            for item in data_json["items"][:4]:
                volume_info = item.get("volumeInfo", {})
                title = volume_info.get("title", "No Title")
                authors = volume_info.get("authors", ["Unknown Author"])
                recommendations.append(f"{title} by {authors[0]}")

    except Exception as e:
        print(f"   [API Plugin] Google Books unavailable: {e}")

    # --- PLUGIN STEP 2: Fallback to local plugin database ---
    if not recommendations:
        print(
            f"   [Local Plugin] Using curated database for '{category}'"
        )
        recommendations = BOOK_PLUGIN_DB.get(
            category,
            ["No recommendations available for this category."]
        )

    return recommendations


# =========================
# SMART RECOMMENDATION SYSTEM
# =========================
print(
    "\n========== 📚 SMART BOOK RECOMMENDATIONS ==========\n"
)

visit_frequency = data["USN"].value_counts()

for usn, count in visit_frequency.items():

    # Recommend only for repeated visitors
    if count > 1:

        student_data = data[data["USN"] == usn]

        print(f"\nUSN: {usn}")
        print(f"Total Visits: {count}")

        # Get most frequent book category for this student
        top_category = (
            student_data["Book Category"]
            .value_counts()
            .idxmax()
        )

        # All unique categories
        favorite_categories = student_data["Book Category"].unique()

        print("Interested Topics:")
        for category in favorite_categories:
            print("-", category)

        # Recommendation for each category using Plugin
        for category in favorite_categories:

            print(f"\n📚 Recommendations for {category}:")

            books = recommend_books_plugin(category)

            if books:
                for book in books:
                    print("-", book)
            else:
                print("No recommendations found.")

# =========================
# STYLE
# =========================
plt.style.use('ggplot')

# =========================
# BAR CHART FUNCTION
# =========================
def plot_bar(
    data_counts,
    title,
    xlabel,
    ylabel,
    filename
):
    plt.figure(figsize=(8, 5))

    ax = data_counts.plot(
        kind='bar',
        edgecolor='black'
    )

    plt.title(title, fontsize=14)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.xticks(rotation=25)

    # Show values on bars
    for i, v in enumerate(data_counts):
        ax.text(
            i,
            v + 0.05,
            str(v),
            ha='center',
            fontsize=10
        )

    plt.grid(axis='y', linestyle='--')
    plt.tight_layout()

    plt.savefig(f"reports/{filename}")
    plt.show()


# =========================
# GRAPHS
# =========================

# Department Chart
plot_bar(
    dept_counts,
    "Department-wise Library Usage",
    "Department",
    "Number of Students",
    "department_chart.png"
)

# Book Category Chart
plot_bar(
    book_counts,
    "Book Category Popularity",
    "Category",
    "Count",
    "book_category_chart.png"
)

# =========================
# PIE CHART
# =========================
plt.figure(figsize=(6, 6))

if not purpose_counts.empty:

    purpose_counts.plot(
        kind="pie",
        autopct="%1.1f%%",
        startangle=90
    )

    plt.title("Purpose of Visit Distribution")
    plt.ylabel("")
    plt.tight_layout()

    plt.savefig("reports/purpose_pie_chart.png")
    plt.show()

else:
    print("No data available for pie chart")

print(
    "\n✅ All reports and graphs generated successfully!"
)

print(
    "📁 Check the 'reports' folder."
)