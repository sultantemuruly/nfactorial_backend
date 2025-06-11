from fastapi import APIRouter, Form
from fastapi.responses import JSONResponse
import os
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

router = APIRouter(prefix="/ai", tags=["AI"])
vector_store = None


def initialize_vector_store():
    global vector_store
    base_path = os.path.dirname(__file__)
    files = ["LSTMPaper.pdf", "AttentionIsAllYouNeed.pdf"]

    all_docs = []
    for file in files:
        file_path = os.path.join(base_path, file)
        loader = PyPDFLoader(file_path)
        docs = loader.load()
        all_docs.extend(docs)

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    split_docs = splitter.split_documents(all_docs)

    embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
    vector_store = FAISS.from_documents(split_docs, embeddings)


# Initialize vector store once
initialize_vector_store()


@router.post("/ask")
async def ask_ai(question: str = Form(...)):
    global vector_store
    if not vector_store:
        return JSONResponse(
            status_code=500, content={"error": "Vector store not initialized."}
        )

    retriever = vector_store.as_retriever(search_type="similarity", k=4)
    llm = ChatOpenAI(temperature=0.3, model="gpt-4", openai_api_key=OPENAI_API_KEY)
    qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)

    try:
        result = qa_chain.run(question)
        return {"question": question, "answer": result}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
