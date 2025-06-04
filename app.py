from flask import Flask, request, render_template, redirect, url_for, session, jsonify
from flask_cors import CORS
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain.agents import initialize_agent, AgentType
from langchain_openai import ChatOpenAI
from config import API_KEY
from langdetect import detect

app = Flask(__name__)
app.secret_key = '19d418093727726463a1f0e222749a4e43e2ffe05680a5dd'

# Autorise Angular à accéder à Flask
CORS(app)

# LangChain + GPT-4o
model_name = "gpt-4o"
model = ChatOpenAI(model_name=model_name, api_key=API_KEY)

# Connexion à la base SQLite
db = SQLDatabase.from_uri('sqlite:///bank.db')
toolkit = SQLDatabaseToolkit(llm=model, db=db)
tools = toolkit.get_tools()
agent_executor = initialize_agent(
    tools=tools,
    llm=model,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    handle_parsing_errors=True
)

# Interface HTML (ancienne méthode)
@app.route('/banko', methods=['GET', 'POST'])
def chat():
    if 'chat' not in session:
        session['chat'] = []

    if request.method == 'POST':
        user_message = request.form.get('message')

        if user_message:
            session['chat'].append({'text': user_message, 'class': 'User'})
            session.modified = True

            lang_code = detect(user_message)
            lang_name = {
                "en": "English",
                "fr": "French",
                "ar": "Arabic"
            }.get(lang_code, "English")

            base_prompt = f"""
You are Banko, a smart banking assistant.
You must answer in the same language used in the message.

Access the database only if the user asks about:
- balance
- fees
- transactions
- card info

User said: "{user_message}"
"""

            try:
                result = agent_executor.invoke({"input": base_prompt})
                session['chat'].append({'text': result['output'], 'class': model_name})
                session.modified = True
            except Exception as e:
                session['chat'].append({'text': f"Erreur : {str(e)}", 'class': 'Error'})
                session.modified = True

    return render_template('index.html', chat=session['chat'])

# Route Angular-compatible : /api/chat
@app.route('/api/chat', methods=['POST'])
def api_chat():
    data = request.json
    user_message = data.get('message')

    if not user_message:
        return jsonify({"error": "Message is required"}), 400

    lang_code = detect(user_message)
    lang_name = {
        "en": "English",
        "fr": "French",
        "es": "Spanish",
        "ar": "Arabic"
    }.get(lang_code, "English")

    base_prompt = f"""
You are Banko, a smart banking assistant.
You must answer in the same language used in the message.

Access the database only if the user asks about:
- balance
- fees
- transactions
- card info

User said: "{user_message}"
"""

    try:
        result = agent_executor.invoke({"input": base_prompt})
        return jsonify({"reply": result['output']})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Autres routes
@app.route('/')
def redirect_home():
    return redirect(url_for('chat'))

@app.route('/home')
def dashboard():
    return render_template('dashboard.html')

if __name__ == '__main__':
    app.run(debug=True)
