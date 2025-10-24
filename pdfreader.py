# -*- coding: utf-8 -*-

import pypdf
import tiktoken

def pdf_reader(pdf_name: str, token_size=200) -> list:
    """read pdf and divide into chunks based on token size. Then returns a list of text chunks."""
    reader = pypdf.PdfReader(pdf_name)
    print(f"Number of pages: {len(reader.pages)}")

    encoder = tiktoken.encoding_for_model("gpt-3.5-turbo")


    token_count = 0
    per_n_tokens = []
    temp_list = []
    for page in reader.pages:

        text = page.extract_text()
        tokens = encoder.encode(text)
        for token in tokens:

            if token_count < token_size:
                token_count += 1
                temp_list.append(token)
            else:
                token_count = 1
                per_n_tokens.append(temp_list)
                temp_list = [token]

    if len(temp_list) > 0:
        per_n_tokens.append(temp_list)
        
    decoded_output = []

    for lists in per_n_tokens:
        result = encoder.decode(lists)
        cleaned_text = " ".join(result.replace('\n', ' ').split())
        decoded_output.append(cleaned_text)
    return decoded_output