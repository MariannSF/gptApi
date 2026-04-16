import moviesDB
from flask import Flask, render_template, request, session
from openai import OpenAI
import os
from moviesDB import client
from chatDB import init_chat_db, save_message, load_messages
import uuid
from utils import format_for_openai

init_chat_db()

#create flask app
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")


# Initialize chat history
@app.before_request
def init_session():
    if "session_id" not in session:
        session["session_id"] = str(uuid.uuid4())

#renders home screen and loads in chat history
@app.route('/')
def home():
    session_id = session["session_id"]
    chat_history = load_messages(session_id)
    return render_template("index.html", chat_history=chat_history)


@app.route("/query", methods=["POST"])
def query(): #runs when form is submitted
    user_input = request.form["user_input"] #takes what user typed


    sql_query = moviesDB.generate_sql(user_input)  #convert to natural language to SQL
    results, columns = moviesDB.run_query(sql_query) #executes SQL on SQLite database which returns results and column names

    session_id = session["session_id"]
    chat_history = load_messages(session_id)
    #sending everything to UI
    return render_template(
        "index.html",
        results=results,
        columns=columns,
        query=sql_query,
        chat_history=chat_history
    )

#*********************************************CHAT***************************
@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.form["chat_input"]
    session_id = session["session_id"]

    save_message(session_id, "user", user_input)

    try:
        # 🔥 Step 1: Try to generate SQL
        sql_query = moviesDB.generate_sql(user_input)

        # 🔥 Step 2: Run SQL
        results, columns = moviesDB.run_query(sql_query)

        # 🔥 Step 3: If results exist → explain them
        if results:
            response = client.responses.create(
                model="gpt-4.1-mini",
                input=f"""
                User question: {user_input}

                SQL query:
                {sql_query}

                Results:
                {results}

                Explain this clearly and briefly.
                """
            )

            bot_reply = response.output_text

            # Save query too (nice upgrade!)
            save_message(session_id, "assistant", bot_reply, query=sql_query)

        else:
            # No results → fallback to chat
            raise Exception("No SQL results")

    except:
        # 🔥 Normal chat fallback
        chat_history = load_messages(session_id)
        formatted_history = format_for_openai(chat_history)

        response = client.responses.create(
            model="gpt-4.1-mini",
            input=formatted_history
        )

        bot_reply = response.output_text
        save_message(session_id, "assistant", bot_reply)

    chat_history = load_messages(session_id)

    return render_template(
        "index.html",
        chat_history=chat_history
    )


if __name__ == '__main__':
    app.run(debug=True)


