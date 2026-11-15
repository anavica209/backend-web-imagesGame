from pathlib import Path
import sys

from dotenv import load_dotenv
#from langchain.document_loaders import PyPDFLoader
#from langchain.text_splitter import RecursiveCharacterTextSplitter
# Corrección para PyPDFLoader (Se movió a langchain_community)
from langchain_community.document_loaders import PyPDFLoader

# Corrección para RecursiveCharacterTextSplitter (Se movió a langchain_text_splitters)
from langchain_text_splitters import RecursiveCharacterTextSplitter
#from langchain.vectorstores import Chroma
from langchain_community.vectorstores import Chroma

load_dotenv()

BASE_DIR = Path(__file__).resolve().parents[2]
PDF_DIR = BASE_DIR / "pdf_files"
PERSIST_DIR = Path(__file__).resolve().parents[1] / "vector_store"


def load_pdf_documents(pdf_dir: Path):
    documents = []
    if not pdf_dir.exists():
        raise FileNotFoundError(f"No se encuentra el directorio de PDFs: {pdf_dir}")

    for pdf_path in sorted(pdf_dir.glob("*.pdf")):
        loader = PyPDFLoader(str(pdf_path))
        documents.extend(loader.load())

    return documents


def create_vector_store():
    documents = load_pdf_documents(PDF_DIR)
    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=120)
    docs = splitter.split_documents(documents)

    use_openai = bool(os.getenv("OPENAI_API_KEY"))
    if use_openai:
        try:
            from langchain.embeddings import OpenAIEmbeddings
            embeddings = OpenAIEmbeddings()
        except Exception as exc:
            raise ImportError(
                "No se pudo cargar OpenAIEmbeddings. Instale el paquete openai y configure OPENAI_API_KEY."
            ) from exc
    else:
        try:
            from langchain.embeddings import HuggingFaceEmbeddings
            embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        except Exception as exc:
            raise ImportError(
                "No se pudo cargar HuggingFaceEmbeddings para ingestión de PDF. Verifique que sentence-transformers, transformers y torch estén instalados correctamente o configure OPENAI_API_KEY para usar OpenAIEmbeddings."
            ) from exc
    vectordb = Chroma.from_documents(
        docs,
        embedding=embeddings,
        persist_directory=str(PERSIST_DIR),
        collection_name="magic_eye_support",
    )
    vectordb.persist()
    return vectordb


if __name__ == "__main__":
    store = create_vector_store()
    print(f"Vector store persistido en: {PERSIST_DIR}")
