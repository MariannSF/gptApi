import sqlite3
import os
import pandas as pd
from openai import OpenAI
from pandas.plotting import table

# gets the api Key and creates a connection using key
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
print("API KEY in moviesDB:", os.getenv("OPENAI_API_KEY"))


def load_to_sqlite():
    conn = sqlite3.connect("movies.db")

    files = {
        "credits.csv": "credits",
        "keywords.csv": "keywords",
        "links.csv": "linksM",
        "links_small.csv": "links_small",
        "movies_metadata.csv": "moviesMeta",
        "ratings.csv": "ratings",
        "ratings_small.csv": "ratings_small"
    }

    dataframes = {}

    for file_name, table_name in files.items():
        # print(f"Loading {file_name} into {table_name}...")
        df = pd.read_csv(file_name, nrows=5000)
        df.to_sql(table_name, conn, if_exists="replace", index=False)
        dataframes[table_name] = df
        # print(df.columns)

    conn.close()
    return dataframes


# Connects to SQLite and displays the table names
def check_data():
    conn = sqlite3.connect("movies.db")
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    print("Tables in database:")
    for table in tables:
        print(table[0])

    conn.close()


# Takes human requests and turns it into SQL using OpenAI model
def generate_sql(user_input):
    prompt = f"""
    Convert this request into a SQLite SQL query.
    Return ONLY the SQL query. No explanation.

    Table: moviesMeta
    Columns: title, vote_average, release_date

    Request: {user_input}
    """

    # sending prompt to OpenAI and receiving response (SQL query)
    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )

    # extract generated SQL
    query = response.output[0].content[0].text.strip()

    # clean formatting
    query = query.replace("```sql", "").replace("```", "").strip()

    return query


def run_query(query):
    conn = sqlite3.connect("movies.db")
    cursor = conn.cursor()

    cleaned_query = query.strip().lower()

    # Only allow SELECT queries (basic SQL injection protection)
    if not cleaned_query.startswith("select"):
        raise ValueError("Only SELECT queries are allowed.")

    # allow one trailing semicolon
    if cleaned_query.endswith(";"):
        query = query.strip()[:-1]
        cleaned_query = query.strip().lower()

    # block multiple statements
    if ";" in cleaned_query:
        raise ValueError("Multiple statements are not allowed.")

    try:
        cursor.execute(query)
        results = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]

    except Exception as e:
        print("SQL Error:", e)
        results = []
        columns = []

    conn.close()
    return results, columns