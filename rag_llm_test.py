from langchain_openai import ChatOpenAI
import ragtesting
import json
import os 
from dotenv import load_dotenv

llm = ChatOpenAI(model_name="gpt-4.1", temperature=0, max_tokens=2000)
CHUNK_TOKEN_SIZE = 200

load_dotenv()
# debugging purpose langsmith env vars!
if not os.getenv("LANGSMITH_API_KEY"):
    print("LANGSMITH_API_KEY_NOT_FOUND")
if not os.getenv("LANGSMITH_PROJECT"):
    print("LANGSMITH_PROJECT is set to default")
    os.environ["LANGSMITH_PROJECT"] = "default"
if not os.getenv("LANGSMITH_TRACING_V2"):
    print("LANGSMITH_TRACING_V2 is set to true")
    os.environ["LANGSMITH_TRACING_V2"] = "true" 
if not os.getenv("OPENAI_API_KEY"):
    print("OPENAI_API_KEY_NOT_FOUND")
    
def search(user_input) -> object:
    """_summary_

    Args:
        user_input (_type_): Use user's input to ask the llm after retrieving relevant chunks from the db.

    Returns:
        _type_: llm response
    """
    results = ragtesting.retrieve_similar_content(user_input)
    temp_output = "/ ".join(row[1] for row in results) # separating each chunk with "/ "
    temp_prompt = "use information provided to answer user's question. If you do not know, say so. Do not make up an answer."\
        + temp_output + "\n user's question: "\
            + user_input
    response = llm.invoke(temp_prompt)
    return response

def reasoning(question, expected_answer, received_response) -> object:
    """_summary_
    llm will create answers and compare them with expected answers to see if they match. If not, we can take a look into reasoning.
    
    Args:
        question (str): original question asked to llm.
        expected_answer (str): expected answer to the question.
        received_response (str): llm's response to the question.
    Returns:
        object: llm's evaluation response.
    """
    
    prompt = f"""The following is a question, the expected answer, and the received answer from an LLM.
    Your task is to determine if the received answer matches the expected answer.
    Question: {question}
    Expected Answer: {expected_answer}
    Received Answer: {received_response}
    
    Does the received answer match the expected answer? First, respond with 'Yes' or 'No'.
    Then provide a brief explanation of your reasoning.
    """
    
    evaluation = llm.invoke(prompt)
    return evaluation
    
def evaluation():
    """_summary_
    Reads test questions and expected answers from a JSON file,
    asks the LLM for answers, and evaluates the correctness of those answers using reasoning().
    Finally, it prints the total number of tests, correct answers, accuracy, and total tokens used for the llm usages.
    """
    total_token_used = 0
    test_count = 0
    correct_count = 0
    with open('wrong_questions.json', 'r', encoding='utf-8') as f:
        test_data = json.load(f)
    for i, item in enumerate(test_data):
        test_count += 1
        question = item['question']
        expected_answer = item['answer']
        response = search(question)
        total_token_used+= response.response_metadata['token_usage']['total_tokens']
        reasoning_response = reasoning(question, expected_answer, response.content)
        total_token_used += reasoning_response.response_metadata['token_usage']['total_tokens']
        if reasoning_response.lower().startswith('yes'): correct=True
        else: 
            correct=False 
        
        if correct:
            print("OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO")
            correct_count += 1
        else:
            print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
            
        print(f"{i}. Question: {question}")
        print(f"Expected Answer: {expected_answer}")
        print(f"LLM Response: {response}")
        print(f"Evaluation: {reasoning_response}\n")
        if correct:
            print("OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO")
        else:
            print("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
            
    print(f"Total Tests: {test_count}, Correct: {correct_count}, Accuracy: {correct_count/test_count*100:.2f}%. \n In other words,\
        {correct_count}/{test_count} questions were answered correctly.\n  \
        Total tokens used: {total_token_used}")
    pass
        
while True:
    user_input = input("""
                       Enter your task. type 'insert' to put in pdf data into db,\n
                       or 'search' to receive answer from the llm.  (or 'exit' to quit): 
                       """)
    if user_input.lower() == 'exit':
        ragtesting.close_connection()
        break
    elif user_input.lower() == 'insert':
        ragtesting.insert_pdf(CHUNK_TOKEN_SIZE)
        continue
    elif user_input.lower() == 'search':
        user_input = input("Enter word to test embedding: ")
        response = search(user_input)
        print("LLM Response:", response.content)
        print("DEBUGGING_TOTAL_TOKENS_USED: ", response.response_metadata['token_usage']['total_tokens'])
    elif user_input.lower() == 'test':
        evaluation()

    