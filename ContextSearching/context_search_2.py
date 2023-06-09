# -*- coding: utf-8 -*-
"""Text_Gen_with_GAN.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1SMD9Ia_KKLgBKlYQHlZ8iq9jpA7qqSks
"""

#!pip install PyPDF2 #download PDF

#!pip install -U spacy #install spaCy

from PyPDF2 import PdfReader
import pandas as pd
import json

#!python -m spacy download en_core_web_lg #load the en_core_web_lg

import spacy
from spacy.tokens import DocBin
from tqdm import tqdm


def extract_text_from_pdf(path):
    # creating a pdf reader object
    reader = PdfReader(path)

    # printing number of pages in pdf file
    print(len(reader.pages))

    # getting a specific page from the pdf file
    text_array = []


    for i in range(len(reader.pages)):
    # extracting text from page
        page = reader.pages[i]
        text = page.extract_text()
        text_array.append(text)

    return text_array

# text = ""
# text_arr = extract_text_from_pdf("ContextSearch/SampleSearch.pdf")
# for i in text_arr:
#   text+=i




# with open('annotations.json', 'r') as f:
#     data = json.load(f)

# for text, annot in tqdm(data['annotations']):
#     doc = nlp.make_doc(text)
#     ents = []
#     for start, end, label in annot["entities"]:
#         span = doc.char_span(start, end, label=label, alignment_mode="contract")
#         if span is None:
#             print("Skipping entity")
#         else:
#             ents.append(span)
#     doc.ents = ents
#     db.add(doc)

# db.to_disk("./training_data.spacy") # save the docbin object

# ! python -m spacy init config config.cfg --lang en --pipeline ner --optimize efficiency

# ! python -m spacy train config.cfg --output ./ --paths.train ./training_data.spacy --paths.dev ./training_data.spacy



# doc = nlp_ner(text) # input sample text


#spacy.displacy.render(doc, style="ent", jupyter=True) # display in Jupyter

def get_labels(nlp):
  return nlp.get_pipe('ner').labels

# get_labels(nlp_ner)

# Process each page using spaCy
def sentence_extraction(filename):

  #get text from pdf
  text_array =  extract_text_from_pdf(filename)
  processed_pages = []
  page_no = 0

  #converting pages into docs for vectorization
  for page in text_array:
      doc = nlp(page)
      processed_pages.append([doc, page_no])
      page_no+=1

  #creating sentences array to access every vectorized sentence
  sentences = []
  for doc, page_no in processed_pages:
      for sentence in doc.sents:
          sentences.append([sentence, page_no])
  return sentences

def create_json_file(context_sents, filename):
  #get the required sentences from the given file
  sentences = sentence_extraction(filename)

  #create a dictionary to dump into the json file
  context_dict = {}
  for input_sent in context_sents:
    context_dict[input_sent] = []

  for input_sent in context_sents:
    # Process the input sentence
    input_doc = nlp(input_sent)

    # Calculate similarity with each sentence
    similarity_scores = []
    for sentence, page_no in sentences:
        similarity_score = input_doc.similarity(sentence)
        similarity_scores.append((sentence, similarity_score, page_no))

    label_similarity_scores = {}
    nlp_ner_labels = get_labels(nlp_ner)
    nlp_labels = get_labels(nlp)
    nlp_ner_labels+=nlp_labels
    for i in nlp_ner_labels:
      similarity_score= input_doc.similarity(nlp(i))
      label_similarity_scores[i] = similarity_score

    similarity_scores.sort(key=lambda x: x[1], reverse=True)
    i = 0
    similarity_scores = similarity_scores[:10]

    sentence_label_similarity = []
    for sentence, page_no in sentences:
      for token in sentence:
        if token.ent_type_ in label_similarity_scores.keys():
          #print(token, token,token.ent_type)
          sentence_label_similarity.append((token, label_similarity_scores[token.ent_type_], page_no))

    # Print the most similar sentences
    sentence_label_similarity = sentence_label_similarity[:10]
    for i in sentence_label_similarity:
        print(i)

    similarity_scores+= sentence_label_similarity
    for i in similarity_scores:
      print(i)
    sorted_list = sorted(similarity_scores, key = lambda x: -1*x[1])

    for sentence, similarity_score, page_no in sorted_list:
        temp_dict = {}
        temp_dict['file'] = filename
        temp_dict['page_no'] = page_no
        temp_dict['sentence'] = sentence.text
        temp_dict['similarity_score'] = similarity_score
        context_dict[input_sent].append(temp_dict)


    #write into json file
    json_string = json.dumps(context_dict, indent = 2)
    with open("context_search_results.json", "w") as f:
      f.write(json_string)


nlp = spacy.load('en_core_web_lg')
db = DocBin() # create a DocBin object
nlp_ner= spacy.load("ContextSearching/model-best")
create_json_file(["DATE", "General Partner"], "ContextSearching/SampleSearch.pdf")