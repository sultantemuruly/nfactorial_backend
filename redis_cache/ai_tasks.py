from celery_worker.celery_worker import celery_app
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
import os


@celery_app.task
def ask_ai_task(question: str):
    try:
        base_path = os.path.join(os.path.dirname(__file__), "../api/ai")
        files = ["LSTMPaper.pdf", "AttentionIsAllYouNeed.pdf"]

        all_docs = []
        for file in files:
            file_path = os.path.join(base_path, file)
            loader = PyPDFLoader(file_path)
            docs = loader.load()
            all_docs.extend(docs)

        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        split_docs = splitter.split_documents(all_docs)

        embeddings = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))
        vector_store = FAISS.from_documents(split_docs, embeddings)

        retriever = vector_store.as_retriever(search_type="similarity", k=4)
        llm = ChatOpenAI(
            temperature=0.3, model="gpt-4", openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)

        return qa_chain.run(question)
    except Exception as e:
        return f"Error: {str(e)}"
