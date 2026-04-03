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
    return render_template("index.html", chat_history=session["chat_history"])


@app.route("/query", methods=["POST"])
def query(): #runs when form is submitted
    user_input = request.form["user_input"] #takes what user typed


    sql_query = moviesDB.generate_sql(user_input)  #convert to natural language to SQL
    results, columns = moviesDB.run_query(sql_query) #executes SQL on SQLite database which returns results and column names

    #sending everything to UI
    return render_template(
        "index.html",
        results=results,
        columns=columns,
        query=sql_query,
        chat_history=session["chat_history"]
    )

#*********************************************CHAT***************************
@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.form["chat_input"]
    session_id = session["session_id"]

    save_message(session_id, "user", user_input)


    chat_history = load_messages(session_id)
    formatted_history = format_for_openai(chat_history)


    # Call OpenAI
    response = client.responses.create(
        model="gpt-4.1-mini",
        input=formatted_history
    )
    print("RAW RESPONSE:", response)
    print("OUTPUT TEXT:", response.output_text)


    bot_reply = response.output_text if response.output_text else ("No response")
    save_message(session_id,"assistant", bot_reply)

    # Add bot response
    chat_history = load_messages(session_id)


    return render_template(
        "index.html",
        chat_history=chat_history
    )


if __name__ == '__main__':
    app.run(debug=True)


