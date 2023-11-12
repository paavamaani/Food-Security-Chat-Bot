from flask import Flask, request
from flask_cors import CORS
import dotenv
import os
from chat import PDFChatBot 
import requests
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

app = Flask(__name__)
CORS(app)

dotenv.load_dotenv(os.path.join(os.getcwd(), '.env'), override=True)



# Load the log endpoint from environment variables
log_endpoint = os.environ.get('Log_Endpoint')

@app.route('/', methods=['GET'])
def home():
    return "Welcome!"

def send_log_data(log_data):
    try:
        # Send the POST request to the Flask app
        response = requests.post(log_endpoint, json=log_data)

        # Check if the request was successful (status code 201)
        if response.status_code == 201:
            data = response.json()
            log_id = data.get("log_id")
            print(f"Log created successfully. Log ID: {log_id}")
        else:
            print(f"Failed to create log. Status code: {response.status_code}, Response: {response.text}")
    except requests.RequestException as e:
        print(f"Error sending log data: {e}")

@app.route('/api/chatbot/greeting', methods=['GET'])
def chatbot_greeting():
    greeting = pdf_chatbot.get_greeting()
    return {"greeting": greeting}

@app.route('/api/pdfchatbot', methods=['POST'])
def chatbot_response():
    user_input = request.json['message']
    response = pdf_chatbot.get_response(user_input)


    return {"response": response['output']}

def load_docs(directory):
    documents = []
    name_to_path = {}
    for file in os.listdir(directory):
        if file.endswith(".pdf"):
            pdf_path = "./data/" + file
            loader = PyPDFLoader(pdf_path)
            documents.extend(loader.load())
            name_to_path[file] = pdf_path  # map file name to its path
    return documents, name_to_path

def split_docs(documents, chunk_size=1000, chunk_overlap=20):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    docs = text_splitter.split_documents(documents)
    return docs

if __name__ == "__main__":
    documents, name_to_path = load_docs('./data')
    docs = split_docs(documents)
     # Set the persist directory here
    persist_directory = "./chroma_db"
    
    # Pass it as an argument when initializing the PDFChatBot
    pdf_chatbot = PDFChatBot(documents, name_to_path, docs, persist_directory)
    app.run(host='0.0.0.0', port=5001)





