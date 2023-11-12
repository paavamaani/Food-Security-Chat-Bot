import os
import dotenv
from langchain.document_loaders import DirectoryLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from unstructured.partition.auto import partition
import urllib.parse

class PDFChatBot():

    def initialize(self):
        # put initialization code here
        pass

    def get_greeting(self):
        return self.greeting_message

    def __init__(self, documents, name_to_path, docs, persist_directory):
        self.initialize()
        self.greeting_message = "Hello! I'm your ChatBot. How can I help you today?"
        
        dotenv.load_dotenv(os.path.join(os.getcwd(), '.env'), override=True)
        self.name_to_path = name_to_path
        self.documents = documents
        self.docs = docs
        self.persist_directory = persist_directory
        self.embeddings = OpenAIEmbeddings()
        
        # Check if vector DB exists on disk, if not, create and save it
        if os.path.exists(self.persist_directory):
            self.vectordb = Chroma(persist_directory=self.persist_directory, embedding_function=self.embeddings)
        else:
            self.vectordb = Chroma.from_documents(self.docs, self.embeddings, persist_directory=self.persist_directory)
        
        self.memory = ConversationBufferMemory(memory_key="chat_history", input_key='question', output_key='answer', return_messages=True)
        self.qa = self.init_qa()
        self.chat_history = []

    def init_qa(self):
        qa = ConversationalRetrievalChain.from_llm(
            llm=ChatOpenAI(temperature=0, model_name="gpt-4-0613"), 
            retriever=self.vectordb.as_retriever(search_kwargs={'k': 6}),
            return_source_documents=True,
            verbose=True
        )
        return qa


    def get_response(self, query):
        if query.lower() == "hi":
            return {"output": "Hello! How can I assist you today?"}
        elif query.lower() == "thank you":
            return {"output": "You're welcome! Do you have any other questions?"}
        elif query.lower() == "bye":
            return {"output": "Goodbye! Have a great day!"}
        prompt = "As a chatbot, I must answer food-related questions from budget PDFs in 50 words or fewer. Please ensure responses are concise."
        prompt += "Now, let's get started. You asked: " + query
        result = self.qa({"question": query, "chat_history": self.chat_history})
        self.chat_history.append((query, result["answer"]))
        output = result["answer"]
        
        return {"output": output}









    def chat(self):
        query = input('Hi! How can I help you? ')
        while query != "Bye":
            print(self.get_response(query))
            query = input()
        print("Bye!")
