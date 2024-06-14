from flask import Flask, request, render_template
from llm.wrapper import setup_qa_chain, query_embeddings,set_qa_prompt
from config import config_dict
import os
from flask_minify import Minify
from apps import create_app

app = Flask(__name__)

DEBUG = (os.getenv('DEBUG', 'False') == 'True')

get_config_mode = 'Debug' if DEBUG else 'Production'

try:
    # Load the configuration using the default values
    app_config = config_dict[get_config_mode.capitalize()]
except KeyError:
    exit('Error: Invalid <config_mode>. Expected values [Debug, Production] ')

app = create_app(app_config)
# Migrate(app, db)

if not DEBUG:
    Minify(app=app, html=True, js=False, cssless=False)

if DEBUG:
    app.logger.info('DEBUG            = ' + str(DEBUG))
    app.logger.info('Page Compression = ' + ('FALSE' if DEBUG else 'TRUE'))
    app.logger.info('DBMS             = ' + app_config.SQLALCHEMY_DATABASE_URI)
    app.logger.info('ASSETS_ROOT      = ' + app_config.ASSETS_ROOT)

@app.route('/')
def home():
    return render_template('home/login.html')

@app.route('/login')
def login():
    return render_template('home/login.html')

@app.route('/chat')
def chat():
    return render_template('home/chatbot.html')

@app.route('/get', methods=['GET'])
def get_response():
    query = request.args.get('msg')
    semantic_search = False  # Désactivez la recherche sémantique pour cet exemple
    API_URL = "https://api-inference.huggingface.co/models/mistralai/Mixtral-8x7B-Instruct-v0.1"
    qa_template = set_qa_prompt()
    if semantic_search:
        response = query_embeddings(query)
    else:
        retriever = setup_qa_chain()
        documents = retriever.get_relevant_documents(query)
        print(documents)
        prompt_text = qa_template.format(context=documents, question=query)
    return function(prompt_text, API_URL)

def function(text ,API_URL ):
    import requests
    from flask import jsonify
    hf_auth = "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"
    headers = {"Authorization": f"Bearer {hf_auth}"}
    data = {"inputs": text}
    response = requests.post(API_URL, headers=headers, json=data)

    if response.status_code == 200:
        result = response.json()
        result = result[0]["generated_text"]
        if "answer" in str(result):
            response = result.split("answer:")[-1].strip()

        return response
    else:
        print(jsonify({"error": "Erreur de l'API"}))
        return str("Erreur de l'API")

if __name__ == '__main__':
    app.run(debug=True)
