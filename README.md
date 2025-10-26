# Rag Project Made To....
Understand full steps of the RAG.  

# How does it work?
## ragtesting.py
- connects to the vector db.
- inserts the pdf into the vector db. The size of the chunks can be set, with default value of 200.
- retreive similar contents with the user query from the vector db. Then check the cosine similarity between the query embedding and output embeddings. If the similarity does not pass threshold, those will not be returned.
- function to close the db connection is included.

## pdfreader.py
- read the pdf and extract the texts.
- Organize the texts into the list of strings, where each string contains only set number of tokens. The default size is set to 200 tokens using tiktoken.

## rag_llm_test.py
- allows user to do multiple things.
- if the user input is 'insert', the user can type in the name of the pdf. That pdf will go through preprocessing then saved into the vector db.
- if the user input is 'search', the user can type in the sentence to search of. The query will go into the vector db first, gain up to five chunks with the highest similarity(smallest L2 distance), and add those chunks into the user prompt. Then the prompt will be provided to the llm, letting it generate the more accurate answer.
- if the user input is 'test', it will automatically check the questions in the given json file. Then the generated answer will be compared to the original answer by llm with reasoning. By this, we can test the accuracy of the information provided using RAG.

## How was the accuracy?
- it was around 72%. I've checked the reasonings and the answers provided by and to the llm, and realized that absolute 200 tokens per chunk is causing the problem. For example, if the sentence 'Alex's number was 100 and Jay's number was 923.' was divided into 'Alex's number was 100 and Jay's number' and 'was 923.', then if we search for Jay's number, the vector db will return the first sentence.
- So to improve the accuracy of this method, better preprocessing steps will be needed, instead of using the magic number as the token number per chunk.

## resource
- I used sample pdfs and question lists from pixegami. The link to the source is here:
- https://github.com/pixegami/simple-rag-pipeline
