import moviesDB
from flask import Flask, render_template, request, session
from openai import OpenAI
import os
from moviesDB import client

#create flask app
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")


# Initialize chat history
@app.before_request
def init_chat():
    if "chat_history" not in session:
        session["chat_history"] = [] #if users first visit create an empty chat history ---- doesn't work as of 4/2


@app.route('/')
def home():
    return render_template("index.html", chat_history=session["chat_history"])


@app.route("/query", methods=["POST"])
def query():
    user_input = request.form["user_input"]

    sql_query = moviesDB.generate_sql(user_input)
    results, columns = moviesDB.run_query(sql_query)

    return render_template(
        "index.html",
        results=results,
        columns=columns,
        query=sql_query,
        chat_history=session["chat_history"]
    )


@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.form["chat_input"]

    chat_history = session["chat_history"]

    # Add user message
    chat_history.append({"role": "user", "content": user_input})

    # Call OpenAI
    response = client.responses.create(
        model="gpt-4.1-mini",
        input=user_input
    )

    bot_reply = response.output_text

    # Add bot response
    chat_history.append({"role": "bot", "content": bot_reply})

    session["chat_history"] = chat_history

    return render_template(
        "index.html",
        chat_history=chat_history
    )


if __name__ == '__main__':
    app.run(debug=True)


