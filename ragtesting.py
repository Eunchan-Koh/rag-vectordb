import psycopg2
from pgvector.psycopg2 import register_vector
import pdfreader
from langchain_openai import OpenAIEmbeddings
import numpy as np

connect = psycopg2.connect(
    host='localhost',
    dbname='rag_project',
    user='postgres',
    password='XXXXXXXX',
    port=5432    
)
register_vector(connect)
cur=connect.cursor()
embeddings = OpenAIEmbeddings()

def initialize_rag_database() -> None:
    """only call it if the testing_rag table does not exist yet."""
    vector = embeddings.embed_query("Hello world")
    vector_size = len(vector)
    cur.execute("""
            create table if not exists testing_rag (
                id serial primary key, 
                embedding vector(%s), 
                content text);
            """, (vector_size,))
    connect.commit()

def cosine_similarity(vec1, vec2) -> float:
    """check cosine similarity between two vectors."""
    dot_product = np.dot(vec1, vec2)
    norm_vec1 = np.linalg.norm(vec1)
    norm_vec2 = np.linalg.norm(vec2)
    if norm_vec1 == 0 or norm_vec2 == 0:
        return 0.0
    return dot_product / (norm_vec1 * norm_vec2)

def insert_pdf(token_size=200) -> None:
    """insert pdf content into the testing_rag table with embeddings after chunking."""
    pdf_path = input("Enter PDF file path(name): ")
    decoded_output = pdfreader.pdf_reader(pdf_path, token_size)
    for content in decoded_output:
        vector = embeddings.embed_query(content)
        cur.execute("INSERT INTO testing_rag (embedding, content) VALUES (%s, %s);", (vector, content))
    connect.commit()
    print("Inserted PDF content with embeddings.")

def retrieve_similar_content(user_input, top_k=5, threshold=0.7) -> list:
    """_summary_

    Args:
        user_input (str): user query. used to retreive similar vectors from db.
        top_k (int, optional): max number of chunks to get from db. Defaults to 5.
        threshold (float, optional): similarity threshold. Defaults to 0.7, do not get chunks from db that have lower similarity than 
        this value.

    Returns:
        tuple list: rows in the results: (id, content, embedding). content is text to be used in prompt, embedding is vector.
    """
    temp_embed=embeddings.embed_query(user_input)
    cur.execute(
        "SELECT id, content, embedding FROM testing_rag ORDER BY embedding <-> %s::vector LIMIT %s;",
        (temp_embed, top_k)
        )
    results = cur.fetchall()
    for row in results:
        if cosine_similarity(temp_embed, row[2]) < threshold:
            results.remove(row)
            
    return results

def close_connection() -> None:
    """close the db connection."""
    cur.close()
    connect.close()

