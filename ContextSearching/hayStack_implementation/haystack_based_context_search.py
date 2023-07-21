import ssl
ssl._create_default_https_context = ssl._create_unverified_context
from multiprocessing import freeze_support

import pdfplumber
import nltk
nltk.data.path.append("ContextSearching/hayStack_implementation/nltk_data")
nltk.download('punkt')

from haystack.document_stores import FAISSDocumentStore
from haystack.utils import clean_wiki_text, convert_files_to_docs, fetch_archive_from_http
from haystack.nodes import PreProcessor
from haystack.nodes import EmbeddingRetriever
from haystack.nodes import FARMReader
from haystack.pipelines import ExtractiveQAPipeline
from haystack.utils import print_answers
import fitz
import re

def extract_number_from_string(input_string):
    numbers = re.findall(r'\d+', input_string)
    return int(numbers[0]) if numbers else None

def highlight_pdf(pdf_path, sentences):
    doc = fitz.open(pdf_path)
    for sentence in sentences:
        page = doc.load_page(sentence[1]) 
        context = sentence[0]
        search_results = page.search_for(context)
        for rect in search_results:
                highlight = page.add_highlight_annot(rect)
    output_file = "ContextSearching/hayStack_implementation/n_file.pdf"
    doc.save(output_file)
    doc.close()

def pdf_to_text_with_structure(pdf_file_path):
    text = []
    with pdfplumber.open(pdf_file_path) as pdf:
        for page in pdf.pages:
            text .append(page.extract_text()+'\n')
            #text+='\n'

    return text



if __name__ == "__main__":

    pdf_path = "ContextSearching/hayStack_implementation/SampleSearch.pdf"
    pages_arr = pdf_to_text_with_structure(pdf_path)
    for i in range(len(pages_arr)):
        file = "ContextSearching/hayStack_implementation/data/doc" + str(i)+".txt"
        with open(file, 'w') as f:
            f.write(pages_arr[i])

    doc_dir = "ContextSearching/hayStack_implementation/data"

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

    #reader = FARMReader(model_name_or_path="ahotrod/albert_xxlargev1_squad2_512", use_gpu=False)

    #reader = FARMReader(model_name_or_path="deepset/roberta-large-squad2", use_gpu=False)
    
    reader = FARMReader(model_name_or_path="deepset/roberta-base-squad2", use_gpu=False)

    pipe = ExtractiveQAPipeline(reader, retriever)


    # prediction = pipe.run(
    #     query="What is the Fax Number?", params={"Retriever": {"top_k": 10}, "Reader": {"top_k": 5}}
    # )
    queries = [
    "What is the Fund Name?",
    "When did the Fund Start?",
    "What is the Carried Interest?",
    "What is the Name of the General Partner?",
    "When was the Initial Closing Date?",
    "When was the Final Closing Date?",
    "What is the Management Company?",
    "What are the Investment Limitations?",
    "Which section has the Purpose of the Fund?",
    "What is the Partnership Term?",
    "How much is the Main Fund?",
    "How much is the Transaction Fees?",
    "What is the Makeup Contribution?",
    ]

    #Queries for Subscription Agreement
    # queries = [
    # "What is the Date?",
    # "What is the Applicant Name?",
    # "What is the Name of the General Partner?",
    # "What is the Name of the Limited Partner?",
    # "What is the Fund Name?",
    # "What is the Law Firm?",
    # "What is the Fund Address?",
    # "What is the Fund Domicile?",
    # "How much is the Commitment Fees?",
    # "What is the Vehicle?",
    # "What is the Telephone Number?",
    # "What is the Fax Number?",
    # "What is the Email Address?",
    # "What is the Tax ID Number?"
    # ]

    #Queries for Equity
    # queries = [
    # "What is the Investment Name?",
    # "Who is the General Partner?",
    # "Who is the Limited Partner?",
    # "What is the Fund Name?",
    # "What is the Fund Address?",
    # "How much is the Investment Amount?",
    # "When is the Notice Date?",
    # "When is the Due Date?",
    # "What is the Currency Code?",
    # "What is the Amount Due?",
    # "What is the Management Fees?",
    # "What is the Total Capital Contribution?",
    # "What is the Bank Name?",
    # "What is the Account Name?",
    # "How muc us the Partnership Expenses?",
    # "how much is the Management Fee Discount?",
    # "How much is the Total Due from Investors?",
    # "What is the Undrawn Commitment Before?",
    # "What is the Undrawn Commitment After?",
    # "Excess Cash returned?",
    # "What is the  Number for the Bank Account?",
    # "What is the Address of the Bank?"
    # ]
    predictions = {}
    all_results = []
    for query in queries:
        prediction = pipe.run( query, params={"Retriever": {"top_k": 10}, "Reader": {"top_k": 5}})
        predictions[query] = []
        for i in prediction['answers']:
            temp_dict = {}
            temp_dict['answer'] = i.answer
            temp_dict['context'] = i.context
            temp_dict['filename'] = "SearchContextTest1.pdf"
            temp_dict['page_no'] = extract_number_from_string(i.meta['name'])
            temp_dict['score'] = i.score
            predictions[query].append(temp_dict)
            #print(i.answer)
            all_results.append([i.context, temp_dict['page_no']])
            # highlight_pdf("ContextSearching/hayStack_implementation/data/SampleContent2LPA.pdf", i.answer)
    document_store.delete_all_documents()
    import json
    json_string = json.dumps(predictions, indent = 2)
    with open("ContextSearching/hayStack_implementation/context_search_results.json", "w") as f:
        f.write(json_string)
    highlight_pdf("ContextSearching/hayStack_implementation/SampleSearch.pdf", all_results)
    
    # json_string = json.dumps(predictions, indent = 2)
    # with open("ContextSearching/hayStack_implementation/context_search_results.json", "w") as f:
    #     f.write(json_string)
    