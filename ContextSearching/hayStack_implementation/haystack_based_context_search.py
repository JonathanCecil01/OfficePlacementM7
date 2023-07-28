# Invent M7 Technologies Private Limited CONFIDENTIAL AND PROPRIETARY
# This source code is the sole property of Invent M7 Technologies Private Limited.
# Reproduction or utilization of this source code in whole or in part is    
# forbidden without the prior written consent of Invent M7 Technologies Private Limited.
# (c) Copyright Invent M7 Technologies Private Limited. 2023. All rights reserved.   
# Author: Jonathan Cecil
# Updated:By K Manickam
import uuid
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
from multiprocessing import freeze_support

import pdfplumber
import nltk
import io
from PyPDF2 import PdfReader, PdfWriter
from PyPDF2.generic import AnnotationBuilder
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from haystack.document_stores import FAISSDocumentStore
from haystack.utils import clean_wiki_text, convert_files_to_docs
from haystack.nodes import PreProcessor
from haystack.nodes import EmbeddingRetriever
from haystack.nodes import FARMReader
from haystack.pipelines import ExtractiveQAPipeline
from haystack.utils import print_answers
import fitz
import re
import os
from os import path
import sys, getopt, traceback
import json

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


def extract_number_from_string(input_string):
    numbers = re.findall(r'\d+', input_string)
    return int(numbers[0]) if numbers else None

def highlight_pdf(pdf_path, predictions):
    doc = fitz.open(pdf_path)
    context_location = {}
    for (k, v) in predictions["data"].items():
      for context in v:
        try:
            page = doc.load_page(context["page_no"]) 
            search_results = page.search_for(context["context"])
            for rect in search_results:
                highlight = page.add_highlight_annot(rect)
                context_location[context["context"]] = (rect.x0, rect.y0)

        except Exception as e:
            print (context)
            traceback.print_exc()
            print(e)
    output_file = os.path.splitext(pdf_path)[0] + '_highlighted.pdf'
    doc.save(output_file)
    doc.close()
    return output_file, context_location


def get_sentence_rectangle(pdf_path, target_sentence, i):
    with open(pdf_path, 'rb') as pdf_file:
        pdf_reader = PdfReader(pdf_file)

        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]

            # Extract text from the page
            page_text = page.extract_text()

            # Check if the target sentence exists in the page's text
            if target_sentence in page_text:
                # Split the page's text into lines
                lines = page_text.split('\n')

                # Loop through the lines to find the target sentence
                for line_num, line in enumerate(lines):
                    if target_sentence in line:
                        # Calculate the coordinates of the rectangle
                        x0, y0, x1, y1 = 0, 700, 0, 0  # Initialize coordinates to zero
                        # Assuming you have a single line sentence
                        x0 = line.find(target_sentence)+150
                        y0 = 700-i*20#page.mediabox.height - (line_num * 5)  # Adjust the y0 position as needed
                        x1 = x0 + 150  # Adjust the x1 position as needed
                        y1 = y0 + 10  # Adjust the y1 position as needed
                        return x0, y0, x1, y1

    # If the target sentence is not found, return None
    return None


def annotate_queries(pdf_path, queries):
    pdf_writer = PdfWriter()
    pdf_reader = PdfReader(open(pdf_path, 'rb'))
    final_path = pdf_path
    for page in range(len(pdf_reader.pages)):
        current_page = pdf_reader.pages[page]
        pdf_writer.add_page(current_page)
    border_color = [0, 0, 1]  # Blue border
    border_color = [c / 255.0 for c in border_color]
    i=0
    for query in queries:
        
        annotation = AnnotationBuilder.link(
            rect=get_sentence_rectangle(pdf_path, query, i), target_page_index=int(queries[query][1])+1,
        )
        pdf_writer.add_annotation(page_number = 0, annotation= annotation)
        i+=1
    with open(path.abspath(final_path), 'wb') as f:
        pdf_writer.write(f)


def create_queries_page(queries):
    buffer = io.BytesIO()  # Create a buffer to store the PDF content
    c = canvas.Canvas(buffer, pagesize=letter)
    c.drawString(100, 750, "Queries")  # Add the "Queries" title

    # Add the queries to the page
    y = 700
    for query in queries:
        c.drawString(150, y, f"{query}")
        y -= 20

    c.save()
    buffer.seek(0)  # Move back to the beginning of the buffer
    return PdfReader(buffer).pages[0]  # Return the PDF page


def _highlight_pdf(pdf_path, sentences):
    doc = fitz.open(pdf_path)
    for sentence in sentences:
        page = doc.load_page(sentence[1]) 
        context = sentence[0]
        search_results = page.search_for(context)
        for rect in search_results:
            highlight = page.add_highlight_annot(rect)
            
    output_file = os.path.splitext(pdf_path)[0] + '_highlighted.pdf'
    doc.save(output_file)
    doc.close()

def pdf_to_text_with_structure(pdf_file_path):
    text = []
    with pdfplumber.open(pdf_file_path) as pdf:
        for page in pdf.pages:
            text .append(page.extract_text()+'\n')
            #text+='\n'

    return text

def hyperlink_queries(json_file_path, new_pdf_path):
    with open(json_file_path, 'r') as j:
        data = json.load(j)
    
    queries = {}
    for query in data['data']:
       queries[query] =  ((data['data'][query][0]['context'],data['data'][query][0]['page_no']))
    
    new_queries_page = create_queries_page(queries.keys())
    pdf_writer = PdfWriter()
    # Add the "Queries" page to the new PDF writer
    pdf_writer.add_page(new_queries_page)
    # Create a PDF reader for the existing PDF
    pdf_reader = PdfReader(new_pdf_path)
    # Merge the existing PDF with the new queries page
    for page_num in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_num]
        pdf_writer.add_page(page)
    # Save the merged PDF
    new_pdf_path = os.path.splitext(pdf_path)[0] + "_hyperlinked.pdf"
    with open(new_pdf_path, 'wb') as output_file:
        pdf_writer.write(output_file)
    annotate_queries(new_pdf_path, queries)


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
    print("hello", json_file)

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
    #doc_dir = "ContextSearching/hayStack_implementation/data"
    doc_dir = "data"
    import shutil
    if os.path.exists(doc_dir):
        shutil.rmtree(doc_dir)
        os.mkdir(doc_dir)
    for i in range(len(pages_arr)):
        file = doc_dir + "/doc" + str(i)+".txt"
        with open(file, 'w') as f:
            f.write(pages_arr[i])


    docs = convert_files_to_docs(dir_path=doc_dir, clean_func=clean_wiki_text, split_paragraphs=True)
    preprocessor = PreProcessor(
        clean_empty_lines=True,
        clean_whitespace=True,
        clean_header_footer=False,
        split_by="word",
        split_length=100,
        split_respect_sentence_boundary=True,
    )
    preprocessed_docs = preprocessor.process(docs)
    document_store = FAISSDocumentStore(faiss_index_factory_str="Flat")
    document_store.write_documents(preprocessed_docs)
    retriever = EmbeddingRetriever(
        document_store=document_store, embedding_model="sentence-transformers/multi-qa-mpnet-base-dot-v1"
    )
    document_store.update_embeddings(retriever)

    reader = FARMReader(model_name_or_path="ahotrod/albert_xxlargev1_squad2_512", use_gpu=True)

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

    if category == 'LPA':
        queries = [
        {'s': 'Fund Name', 'q': "What is the Fund Name?"},
        {'s': 'Start Date', 'q': "When did the Fund Start?"},
        {'s': 'Carried Interest', 'q': "What is the Carried Interest?"},
        {'s': 'General Partner Name', 'q': "What is the Name of the General Partner?"},
        {'s': 'Initial Closing Date', 'q': "When was the Initial Closing Date?"},
        {'s': 'Final Closing Date', 'q': "When was the Final Closing Date?"},
        {'s': 'Management Company', 'q': "What is the Management Company?"},
        {'s': 'Investment Limitations', 'q': "What are the Investment Limitations?"},
        {'s': 'Purpose', 'q': "Which section has the Purpose of the Fund?"},
        {'s': 'Partnership Term', 'q': "What is the Partnership Term?"},
        {'s': 'Main Fund', 'q': "How much is the Main Fund?"},
        {'s': 'Transaction Fees', 'q': "How much is the Transaction Fees?"},
        {'s': 'Makeup Contribution', 'q': "What is the Makeup Contribution?"},
        ]
    elif category == 'SA':
        #  Queries for Subscription Agreement
        queries = [
        {'s': 'Date', 'q': "What is the Date?"},
        {'s': 'Applicant Name', 'q': "What is the Applicant Name?"},
        {'s': 'General Partner Name', 'q': "What is the Name of the General Partner?"},
        {'s': 'Limited Partner Name', 'q': "What is the Name of the Limited Partner?"},
        {'s': 'Fund Name', 'q': "What is the Fund Name?"},
        {'s': 'Law Firm', 'q': "What is the Law Firm?"},
        {'s': 'Fund Address', 'q': "What is the Fund Address?"},
        {'s': 'Fund Domicile', 'q': "What is the Fund Domicile?"},
        {'s': 'Commitment Amount', 'q': "How much is the Commitment Fees?"},
        {'s': 'Vehicle', 'q': "What is the Vehicle?"},
        {'s': 'Telephone Number', 'q': "What is the Telephone Number?"},
        {'s': 'Fax Number', 'q': "What is the Fax Number?"},
        {'s': 'Email Address', 'q': "What is the Email Address?"},
        {'s': 'Tax ID Number', 'q': "What is the Tax ID Number?"}
        ]

    elif category == 'CCN':
        #Queries for Equity
        queries = [
        {'s': 'Fund Name', 'q': "What is the Fund Name?"},
        {'s': 'General Partner Name', 'q': "Who is the General Partner?"},
        {'s': 'Limited Partner Name', 'q': "Who is the Limited Partner?"},
        {'s': 'Investment Name', 'q': "What is the Investment Name?"},
        {'s': 'Investment Amount', 'q': "How much is the Investment Amount?"},
        {'s': 'Notice Date', 'q': "When is the Notice Date?"},
        {'s': 'Due Date', 'q': "When is the Due Date?"},
        {'s': 'Currency Code', 'q': "What is the Currency Code?"},
        {'s': 'Amount Due', 'q': "What is the Amount Due?"},
        {'s': 'Commitment Amount', 'q': "How muxh is Commitment Amount?"},
        {'s': 'Unfunded Commitment Amount', 'q': "How muxh is Unfunded Commitment Amount?"},
        {'s': 'Investor Number', 'q': "What is the Investor Number?"},
        {'s': 'Notice Number', 'q': "What is the Notice Number?"},
        {'s': 'Investment Fast Logics', 'q': "What is the Investment Fast Logics?"},
        {'s': 'Excess Cash Returned', 'q': "How much is Excess Cash Returned?"},
        {'s': 'Management Fee', 'q': "How much is Management Fee?"},
        {'s': 'Management Fee Discount', 'q': "How much is Management Fee Discount?"},
        {'s': 'Make Up Management Fee', 'q': "How much is Make Up Management Fee?"},
        {'s': 'Management Fee Interest', 'q': "Management Fee Interest?"},
        {'s': 'Net Management Fee', 'q': "Net Management Fee?"},
        {'s': 'Partnership Expenses', 'q': "Partnership Expenses?"},
        {'s': 'Organizational Costs', 'q': "Organizational Costs?"},
        {'s': 'Distribution of Proceeds', 'q': "Distribution of Proceeds?"},
        {'s': 'Capital Contribution', 'q': "Capital Contribution?"},
        {'s': 'Aggregate Capital Call Amount', 'q': "Aggregate Capital Call Amount?"},
        {'s': 'Total Capital Call Amount', 'q': "Total Capital Call Amount?"},
        {'s': 'Total Make up Contributions', 'q': "Total Make up Contributions?"},
        {'s': 'Make Up Interest Payment', 'q': "Make Up Interest Payment?"},
        {'s': 'Total Due From Investor', 'q': "Total Due From Investor?"},
        {'s': 'Undrawn Commitment before', 'q': "Undrawn Commitment before?"},
        {'s': 'Undrawn Commitment Effect', 'q': "Undrawn Commitment Effect?"},
        {'s': 'Undrawn Commitment After', 'q': "Undrawn Commitment After?"},
        {'s': 'Distribution Amount', 'q': "Distribution Amount?"}
        ]
    elif category == 'DN':
        queries = [
        {'s': 'Fund Name', 'q': "What is the Fund Name?"},
        {'s': 'General Partner Name', 'q': "Who is the General Partner?"},
        {'s': 'Limited Partner Name', 'q': "Who is the Limited Partner?"},
        {'s': 'Investment Name', 'q': "What is the Investment Name?"},
        {'s': 'Investment Amount', 'q': "How much is the Investment Amount?"},
        {'s': 'Notice Date', 'q': "When is the Notice Date?"},
        {'s': 'Due Date', 'q': "When is the Due Date?"},
        {'s': 'Currency Code', 'q': "What is the Currency Code?"},
        {'s': 'Amount Due', 'q': "What is the Amount Due?"},
        {'s': 'Commitment Amount', 'q': "How muxh is Commitment Amount?"},
        {'s': 'Unfunded Commitment Amount', 'q': "How muxh is Unfunded Commitment Amount?"},
        {'s': 'Investor Number', 'q': "What is the Investor Number?"},
        {'s': 'Notice Number', 'q': "What is the Notice Number?"},
        {'s': 'Investment Fast Logics', 'q': "What is the Investment Fast Logics?"},
        {'s': 'Excess Cash Returned', 'q': "How much is Excess Cash Returned?"},
        {'s': 'Management Fee', 'q': "How much is Management Fee?"},
        {'s': 'Management Fee Discount', 'q': "How much is Management Fee Discount?"},
        {'s': 'Make Up Management Fee', 'q': "How much is Make Up Management Fee?"},
        {'s': 'Management Fee Interest', 'q': "Management Fee Interest?"},
        {'s': 'Net Management Fee', 'q': "Net Management Fee?"},
        {'s': 'Partnership Expenses', 'q': "Partnership Expenses?"},
        {'s': 'Organizational Costs', 'q': "Organizational Costs?"},
        {'s': 'Distribution of Proceeds', 'q': "Distribution of Proceeds?"},
        {'s': 'Capital Contribution', 'q': "Capital Contribution?"},
        {'s': 'Aggregate Capital Call Amount', 'q': "Aggregate Capital Call Amount?"},
        {'s': 'Total Capital Call Amount', 'q': "Total Capital Call Amount?"},
        {'s': 'Total Make up Contributions', 'q': "Total Make up Contributions?"},
        {'s': 'Make Up Interest Payment', 'q': "Make Up Interest Payment?"},
        {'s': 'Total Due From Investor', 'q': "Total Due From Investor?"},
        {'s': 'Undrawn Commitment before', 'q': "Undrawn Commitment before?"},
        {'s': 'Undrawn Commitment Effect', 'q': "Undrawn Commitment Effect?"},
        {'s': 'Undrawn Commitment After', 'q': "Undrawn Commitment After?"},
        {'s': 'Distribution Amount', 'q': "Distribution Amount?"},
        {'s': 'Total Make Up Contributions', 'q': "Total Make Up Contributions?"},
        {'s': ' Interest Owed', 'q': "Interest Owed?"},
        {'s': ' Interest Rebalance Contributions', 'q': "Interest Rebalance Contributions?"},
        {'s': ' Cummulative Distribution Prior', 'q': "Cummulative Distribution Prior?"},
        {'s': ' Current Distribution Amount', 'q': "Current Distribution Amount?"},
        {'s': ' Total Distribution Amount', 'q': "Total Distribution Amount?"},
        {'s': ' Return of Capital', 'q': "Return of Capital?"},
        {'s': ' Special Contribution', 'q': "Special Contribution?"},
        {'s': ' Realized Gains', 'q': "Realized Gains?"},
        {'s': ' Carried Interest', 'q': "Carried Interest?"}
        ]
    elif category == 'SL':
        queries = [
        {'s': 'Fund Name', 'q': "What is the Fund Name?"},
        {'s': 'Address', 'q': "Where is the Address?"},
        {'s': 'Date', 'q': "When is the Date?"},
        {'s': 'Limited Partner Name', 'q': "What is the Name of the Limited Partner?"},
        {'s': 'Fund Manager', 'q': "What is Name of the Fund Manager?"},
        {'s': 'Commitment Amount', 'q': "What is the Commiment Amount?"},
        {'s': 'Favored Nation', 'q': "Which is the Favored Nation?"},
        {'s': 'Management Fee', 'q': "Who is the Management?"},
        {'s': 'Investment Requirement', 'q': "What is the Investment Requirement?"},
        {'s': 'Fee Expense Offset', 'q': "How much is the Fee Expense Offset?"}
        ]
    predictions = {'file': pdf_path, 'data':{}}
    
    # all_results = []
    for query in queries:
        prediction = pipe.run( query['q'], params={"Retriever": {"top_k": 10}, "Reader": {"top_k": 2}})
        predictions["data"][query['s']] = []
        for i in prediction['answers']:
            temp_dict = {}
            temp_dict['answer'] = i.answer
            temp_dict['context'] = i.context
            temp_dict['page_no'] = extract_number_from_string(i.meta['name'])
            temp_dict['book_mark'] = ""
            temp_dict['score'] = i.score
            predictions["data"][query['s']].append(temp_dict)
            #print(i.answer)
            # all_results.append([i.context, temp_dict['page_no']])
            # highlight_pdf("ContextSearching/hayStack_implementation/data/SampleContent2LPA.pdf", i.answer)
    document_store.delete_all_documents()
    delete_all_files_in_folder(doc_dir)
    new_pdf_path, context_location = highlight_pdf(pdf_path, predictions)
    for (k, v) in predictions["data"].items():
      for context in v:
          if context["context"] not in context_location:
              continue
          x1, y1 = context_location[context['context']]
          context['book_mark'] =f"file:///{new_pdf_path}#page={context['page_no']}&x={x1}&y={y1}"
            
    json_string = json.dumps(predictions, indent = 2)
    with open(os.path.splitext(pdf_path)[0] +".json", "w") as f:
        f.write(json_string)
