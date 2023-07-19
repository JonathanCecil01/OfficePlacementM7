import ssl
ssl._create_default_https_context = ssl._create_unverified_context
from multiprocessing import freeze_support

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

def highlight_pdf(pdf_path, sentence):
    # Open the PDF file
    pdf = fitz.open(pdf_path)

    # Iterate over the pages
    for page in pdf:
        # Search for the sentence and get its bounding box
        rect = page.search_for(sentence)

        # Add a highlight annotation for the sentence
        for r in rect:
            highlight = page.add_highlight_annot(r)

    # Save the modified PDF
    pdf.save("new_pdf.pdf")
    pdf.close()


if __name__ == "__main__":

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

    reader = FARMReader(model_name_or_path="deepset/roberta-base-squad2", use_gpu=True)

    pipe = ExtractiveQAPipeline(reader, retriever)


    prediction = pipe.run(
        query="How much is the Main Fund?", params={"Retriever": {"top_k": 10}, "Reader": {"top_k": 5}}
    )

    queries = ["what is the Fund Name?", "Start Date?", "Which Section has Carried Interest?", "Who is the General Partner?", "When is the Initial Closing Date?", "When is the Final Closing Date?", "Which is the Management Company?", "What are the Investment Limitations?", "Which sections has the Purpose?", "How long is the Partnership Term?", "How much is the Main Fund?", "How Much is the Transaction Fees?", "How much is the Makeup Contribution?"]
    predictions = {}
    for query in queries:
        prediction = pipe.run( query, params={"Retriever": {"top_k": 10}, "Reader": {"top_k": 5}})
        predictions[query] = []
        for i in prediction['answers']:
            temp_dict = {}
            temp_dict['answer'] = i.answer
            temp_dict['context'] = i.context
            temp_dict['filename'] = i.meta['name']
            temp_dict['score'] = i.score
            predictions[query].append(temp_dict)
    
    import json
    json_string = json.dumps(predictions, indent = 2)
    with open("context_search_results.json", "w") as f:
        f.write(json_string)

    for prediction in predictions:
        highlight_pdf("ContextSearching/hayStack_implementation/data/SampleContent2LPA.pdf", predictions[prediction][0]['context'])