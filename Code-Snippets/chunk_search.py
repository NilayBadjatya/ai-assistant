import os
import numpy
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY")
)

EMBED_MODEL = os.getenv("EMBEDDING_MODEL")
KB_FOLDER = os.getenv("KB_FOLDER")
VECTOR_STORE_PATH = os.getenv("VECTOR_STORE_PATH")

def get_embeddings(text):
    response = client.embeddings.create(
        model=EMBED_MODEL,
        input=text
    )

    return response.data[0].embedding

def cosine_similarity(A, B):
    dot_product = numpy.dot(A, B)
    norm_A = numpy.linalg.norm(A)
    norm_B = numpy.linalg.norm(B)
    return dot_product / (norm_A * norm_B) if norm_A and norm_B else 0.0


# Load the documents from the knowledge base folder
def load_documents(folder=KB_FOLDER):
    documents = []

    for filename in sorted(os.listdir(folder)):
        if not filename.endswith(".txt"):
            continue

        path = os.path.join(folder, filename)
        with open(path, "r", encoding='utf-8') as f:
            documents.append({
                "source": filename,
                "text": f.read()
            })

    return documents

def add_embeddings(documents):
    for document in documents:
        vector = get_embeddings(document["text"])
        document["vector"] = vector

    return documents


def search(userquery, chunks, top_k=3):
    userquery_vector = get_embeddings(userquery)

    results = []
    for chunk in chunks:
        score = cosine_similarity(userquery_vector, chunk["vector"])
        results.append({
            "score": score,
            "source": chunk["source"],
            "text": chunk["text"],
            "size": len(chunk["text"]),
            "chunk_id" : chunk["chunk_id"]
        })

    results.sort(key=lambda rec: rec["score"], reverse=True)
    return results[:top_k]

def chunk_document(documents):
    # This is a simple chunking function that splits each document into chunks of a fixed size.
    # In a real-world scenario, you might want to use a more sophisticated chunking strategy.
    chunks = []

    chunk_id = 0
    for part in documents["text"].split("\n\n"):  # Split by paragraphs
        part = part.strip()
        if part:
            chunks.append({
                "source": documents["source"],
                "chunk_id": chunk_id,
                "text": part,
            })
            chunk_id += 1

    return chunks

def create_chunks():
    documents = load_documents()
    chunks = []

    for document in documents:
        chunks.extend(chunk_document(document))

    return chunks

def test(user_query, chunks, tok_k=3):
    print(f"User Query: {user_query}")

    results = search(user_query, chunks, 3)

    for r in results:
        print(f"Score: {r['score']:.2f}, Source: {r['source']}, Size: {r['size']}")
        print(f"    {r['text']}\n")

def save_vector_store(chunks):
    with open(VECTOR_STORE_PATH, "w", encoding='utf-8') as f:
        json.dump(chunks, f, indent=4)

def load_vector_store():
    with open(VECTOR_STORE_PATH, "r", encoding='utf-8') as f:
        return json.load(f);

chunks = []

if os.path.exists(VECTOR_STORE_PATH):
    chunks = load_vector_store()
    print(f"Loaded {len(chunks)} chunks from the vector store file.")
else:
    chunks = create_chunks()
    chunks = add_embeddings(chunks)
    save_vector_store(chunks)
    print(f"Created and embedded {len(chunks)} chunks saved to vector store file {VECTOR_STORE_PATH}")


print(f"Loaded {len(chunks)} chunks from {KB_FOLDER} and added embeddings")

user_query = "What are the benefits of Maternity Leave ?"

test(user_query, chunks, 3)