import os
import numpy
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY")
)

EMBED_MODEL = os.getenv("EMBEDDING_MODEL")
KB_FOLDER = os.getenv("KB_FOLDER")

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

def search(userquery, documents, top_k=3):
    userquery_vector = get_embeddings(userquery)

    results = []
    for document in documents:
        score = cosine_similarity(userquery_vector, document["vector"])
        results.append({
            "score": score,
            "source": document["source"],
            "text": document["text"],
            "size": len(document["text"])
        })

    results.sort(key=lambda rec: rec["score"], reverse=True)
    return results[:top_k]

def test(user_query, documents, tok_k=3):
    print(f"User Query: {user_query}")

    results = search(user_query, documents, 3)

    for r in results:
        print(f"Score: {r['score']:.2f}, Source: {r['source']}, Size: {r['size']}")

documents = load_documents()
documents = add_embeddings(documents)

print(f"Loaded {len(documents)} documents from {KB_FOLDER} and added embeddings.")

user_query = "How many days I will get for maternity leave ?"

test(user_query, documents, 3)