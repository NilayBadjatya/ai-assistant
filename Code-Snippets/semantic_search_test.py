from openai import OpenAI
import os
import numpy
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("API_KEY")
)

def get_embeddings(text):
    """Get embeddings for the given text using the OpenAI API."""
    response = client.embeddings.create(
        model=os.getenv("EMBEDDING_MODEL"),
        input=text
    )
    return response.data[0].embedding

def cosine_similarity(A, B):
    """Calculate the cosine similarity between two vectors."""
    dot_prod = numpy.dot(A, B)
    norm_A = numpy.linalg.norm(A)
    norm_B = numpy.linalg.norm(B)
    return dot_prod / (norm_A * norm_B) if norm_A and norm_B else 0.0

text1 = "The quick brown fox jumps over the lazy dog"
text2 = "A fast dark-colored fox leaps over a sleepy canine"
text3 = "I am learning about embeddings and semantic search."

embeddings1 = get_embeddings(text1)
embeddings2 = get_embeddings(text2)
embeddings3 = get_embeddings(text3)

sim_1_2 = cosine_similarity(embeddings1, embeddings2)
sim_1_3 = cosine_similarity(embeddings1, embeddings3)

print(f"Cosine similarity between text1 and text2: {sim_1_2:.2f}")
print(f"Cosine similarity between text1 and text3: {sim_1_3:.2f}")
