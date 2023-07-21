The Objectve of this application is to identify the location of the Texts with the highest context match with an input Query.

This follows the extractive QnA technique to Highlight the highest context match in a given pdf file.

Haystack Library is used to create a retriever reader pipeline for the extraction.
Retriever - BM25
Reader Model - Roberta Uncased

Steps to Run the application:

1. Insert the file of interest in the haystack implementation folder to perform extraction
2. install the 'nltk' library, install the complete version of haystack with the command -  pip install 'farm-haystack[colab,faiss,inference,ocr,preprocessing,file-conversion,pdf]', 
Make sure to install the pdfplumber library as well.
3. Then run the program from the existing directory. 
4. A faiss document db, a results json file and a new pdf with the highlights will be created.

Note: before rerunning the application ensure to delete the existing db.