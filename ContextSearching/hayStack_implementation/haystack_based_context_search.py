# Invent M7 Technologies Private Limited CONFIDENTIAL AND PROPRIETARY
# This source code is the sole property of Invent M7 Technologies Private Limited.
# Reproduction or utilization of this source code in whole or in part is    
# forbidden without the prior written consent of Invent M7 Technologies Private Limited.
# (c) Copyright Invent M7 Technologies Private Limited. 2023. All rights reserved.   
# Author: Jonathan Cecil
# Updated:By K Manickam
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
import pdfplumber
import nltk
from haystack.document_stores import FAISSDocumentStore
from haystack.utils import convert_files_to_docs
from haystack.nodes import PreProcessor
from haystack.nodes import EmbeddingRetriever
from haystack.nodes import FARMReader
from haystack.pipelines import ExtractiveQAPipeline
import fitz
import re
import os
import sys, getopt, traceback
import json

'''Function get_sentence identifies and returns the sentence in which the answer exists.'''
def get_sentence(context, answer):
    loc  = context.find(answer)
    start = loc
    end = loc+len(answer)
    for i in range(0, loc):
        if context[i]=='\n':
            start = i
    for i in range(loc, len(context)):
        if context[i]=='\n':
            end = i
            break
    sentence = context[start+1:end]
    return sentence
    
'''Function clears all the intermediate text files in the data_folder after execution.'''
def delete_all_files_in_folder(folder_path):
    try:
        # Get a list of all files in the folder
        files_list = os.listdir(folder_path)

        # Loop through the files and delete them one by one
        for file_name in files_list:
            file_path = os.path.join(folder_path, file_name)
            if os.path.isfile(file_path):  # Ensure it's a file and not a subdirectory
                os.remove(file_path)
                print(f"Deleted: {file_name}")

        print("All files in the folder have been deleted.")
    except Exception as e:
        print(f"Error: {e}")

'''Function returns the page number coressponding to the text_file'''
def extract_number_from_string(input_string):
    numbers = re.findall(r'\d+', input_string)
    return int(numbers[0]) if numbers else None


'''Highlights the context after prediction and creates a new highlighted pdf file'''
def highlight_pdf(pdf_path, predictions):
    doc = fitz.open(pdf_path)
    context_location = {}
    for (k, v) in predictions["data"].items():
      for context in v:
        try:
            page = doc.load_page(context["page_no"]) 
            search_sentence = get_sentence(context["context"], context["answer"])
            search_results = page.search_for(search_sentence)
            if not search_results:
                search_results = page.search_for(context["answer"])
            for rect in search_results:
                highlight = page.add_highlight_annot(rect)
                context_location[context["context"]] = (rect.x0, rect.y0)
                break
        except Exception as e:
            print (context)
            traceback.print_exc()
            print(e)
    output_file =os.path.splitext(pdf_path)[0] + '_highlighted.pdf'
    doc.save(output_file)
    doc.close()
    return output_file, context_location



'''Adds bookmarks in the json file linking to the location of the highlights'''
def hyperlink_pdf(predictions, new_pdf_path, context_location):
    for (k, v) in predictions["data"].items():
      for context in v:
          if context["context"] not in context_location:
              continue
          x1, y1 = context_location[context['context']]
          context['book_mark'] =f"file:///{new_pdf_path}#page={context['page_no']}&x={x1}&y={y1}"

'''converts the pdf to a text_array which retains the structure of the pdf'''
def pdf_to_text_with_structure(pdf_file_path):
    text = []
    with pdfplumber.open(pdf_file_path) as pdf:
        for page in pdf.pages:
            text .append(page.extract_text()+'\n')

    return text

'''Final output json file is written'''
def write_json(predictions, pdf_path):
    json_string = json.dumps(predictions, indent = 2)
    with open(os.path.splitext(pdf_path)[0] +".json", "w") as f:
        f.write(json_string)

def usage():
    print (sys.argv[0] + ' -i <inputfile> -c <category> -m <model>')
    print ('\t category: LLP,CCN,DN,SA,SL')
    print ('\t model: RL, RB, AX')
    sys.exit()


if __name__ == "__main__":

    argv = sys.argv[1:]
    pdf_path = ""
    category = ""
    model = ""
    json_file = ""
    try:
        opts, args = getopt.getopt(argv,"hi:c:m:j:",["ifile=","category=","model=","json="])
        for opt, arg in opts:
            if opt == '-h':
               usage()
            elif opt in ("-i", "--ifile"):
               pdf_path = arg
            elif opt in ("-c", "--category"):
               category = arg
            elif opt in ("-m", "--model"):
               model = arg
            elif opt in ("-j", "--json"):
               json_file = arg
    except Exception as e:
        print(e)
        usage()

    if category == "" or model == "" or pdf_path == "":
        if pdf_path == "" and json_file == "" :
            print ("File:", pdf_path)
            print ("Model:", model)
            print ("Category:", category)
            usage()
        else:
            try:
               json_file_ptr = open(json_file)
               highlight_pdf(pdf_path, json.load(json_file_ptr))
               json_file_ptr.close()
            except Exception as e:
                traceback.print_exc()
                print(e)
            sys.exit()
     
    nltk.data.path.append("ContextSearching/hayStack_implementation/nltk_data")
    nltk.download('punkt')
    pages_arr = pdf_to_text_with_structure(pdf_path)
    doc_dir = "data"
    import shutil
    if os.path.exists(doc_dir):
        shutil.rmtree(doc_dir)
        os.mkdir(doc_dir)
    for i in range(len(pages_arr)):
        file = doc_dir + "/doc" + str(i)+".txt"
        with open(file, 'a') as f:
            f.write(pages_arr[i])
    
    doc_split_len = 500
    if len(pages_arr) > 50:
        doc_split_len = 100
    
    docs = convert_files_to_docs(dir_path=doc_dir, split_paragraphs=True)
    document_store = FAISSDocumentStore(faiss_index_factory_str="Flat", similarity= 'dot_product')
    preprocessor = PreProcessor(
        clean_empty_lines=False,
        clean_whitespace=False,
        clean_header_footer=False,
        split_by="word",
        split_length=doc_split_len,
        split_respect_sentence_boundary=True,
    )
    preprocessed_docs = preprocessor.process(docs)
    document_store.write_documents(preprocessed_docs)
    
    retriever = EmbeddingRetriever(
        document_store=document_store, embedding_model="sentence-transformers/multi-qa-mpnet-base-dot-v1"
    )
    document_store.update_embeddings(retriever)

    reader = FARMReader(model_name_or_path="deepset/roberta-base-squad2", use_gpu=False)

    if model == 'RB':
        #Roberta Base
        reader = FARMReader(model_name_or_path="deepset/roberta-base-squad2", use_gpu=False)
    elif model == 'RL':
        #Roberta Large
        reader = FARMReader(model_name_or_path="deepset/roberta-large-squad2", use_gpu=False)
    elif model == 'AX':
        #Albert 
        reader = FARMReader(model_name_or_path="ahotrod/albert_xxlargev1_squad2_512", use_gpu=True)
    else:
        usage()
    

    pipe = ExtractiveQAPipeline(reader, retriever)


    queries = []
    if category == 'LPA':
        json_path = 'query_config/query_lpa.json'
    elif category == 'SA':
        json_path = 'query_config/query_sa.json'
    elif category == 'CCN':
        json_path = 'query_config/query_ccn.json'
    elif category == 'DN':
        json_path = 'query_config/query_dn.json'
    elif category == 'SL':
        json_path = 'query_config/query_sl.json'

    with open(json_path, 'r') as f:
        json_data = json.load(f)
    for item in json_data:
        section = item.get('s', "")
        query = item.get('q', "")
        temp_dict = {'s' : section, 'q' : query}
        queries.append(temp_dict)

    
    predictions = {'file': pdf_path, 'data':{}}
    for query in queries:
        prediction = pipe.run( query['q'], params={"Retriever": {"top_k": 10}, "Reader": {"top_k": 2}})
        predictions["data"][query['s']] = []
        for i in prediction['answers']:
            if i.score<0.05:
                continue
            temp_dict = {}
            temp_dict['answer'] = i.answer
            temp_dict['context'] = i.context
            temp_dict['page_no'] = extract_number_from_string(i.meta['name'])
            temp_dict['book_mark'] = ""
            temp_dict['score'] = i.score
            predictions["data"][query['s']].append(temp_dict)


    document_store.delete_all_documents()
    delete_all_files_in_folder(doc_dir)
    new_pdf_path, context_location = highlight_pdf(pdf_path, predictions)
    hyperlink_pdf(predictions, new_pdf_path, context_location)
    write_json(predictions, pdf_path)
