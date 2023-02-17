import json
from .reader import Reader
from .retriever import Retriever, DPR_Retriever
import pandas as pd
from haystack.pipelines import ExtractiveQAPipeline
import logging
from elasticsearch import Elasticsearch
from haystack.document_stores import ElasticsearchDocumentStore

logger = logging.getLogger(__name__)

class HeatmapGenerator():
    def __init__(self, retriever:Retriever, reader:Reader, unit:str='paragraph'):
        self.unit = unit
        self.pipeline = ExtractiveQAPipeline(reader.haystack_reader, retriever.haystack_retriever)

        data = json.load(open("data/qanta.train.2018.04.18.json"))
        self.df = pd.json_normalize(data["questions"])
        wiki = json.load(open("data/wiki_lookup.json"))
        self.df = self.df[(self.df["difficulty"] == "MS") | (self.df["difficulty"] == "HS")]
        drop_indices = []
        
        for index, row in self.df.iterrows():
            if row["page"] not in wiki:
                drop_indices.append(index)
        self.df = self.df.drop(index=drop_indices)
    
    def extract_info(self, query, answer, retrieve_num, read_num):
        res = self.pipeline.run(
                    query=query,
                    params={
                        "Retriever": {"top_k": retrieve_num},
                        "Reader": {"top_k": read_num}
                    }
            )
        #we can filter non-related articles out afterwards from source in meta of res
        
        logger.debug(f"Running query: {query}")
        logger.debug(f"\tExpected Answer: {answer}")
        logger.debug(f"\tResult: {res}\n\n")
        # print(query)
        # print(answer)
        # print(res)
        # print("\n\n\n")

        answers = [x.to_dict() for x in res['answers']]
        for ans in answers:
            if ans['answer'] == answer:
                correct_unit_num = ans['meta']['unit_number']
                logger.debug(f"\tCorrect answer found")
                logger.debug(f"\tCorrect context (part of article): {ans['context']}")
                logger.debug(f"\tCorrect {self.unit}: {correct_unit_num}")

                if correct_unit_num not in self.unit_freq:
                    self.unit_freq[correct_unit_num] = 1
                else:
                    self.unit_freq[correct_unit_num] += 1
           
    def get_page_heatmap(self, page_name, retrieve_num=10, read_num=5):
        self.unit_freq = dict()
        curr_df = self.df[self.df["page"] == page_name]

        for index, row in curr_df.iterrows():
            df_question = row["text"]
            from nltk.tokenize import sent_tokenize
            clues = sent_tokenize(df_question)
            for clue in clues:
                self.extract_info(clue, page_name, retrieve_num, read_num)

        print(self.unit_freq)
        self.generate_heatmap(page_name, 0, 68, 27, 0, 0.8)
    
    
    def add_html(self, text, r, g, b, a):
        self.html += f"<p style=\"background-color: rgba({r},{g},{b},{a})\">{text}</p>\n"

    def generate_heatmap(self, answer, r, g, b, mina, maxa):
        es_user = "elastic"
        es_password = "vqyxbiHqq=jbB4l2JqPZ"#"RZJVsRjjv7ZeD6lezInf" # "vqyxbiHqq=jbB4l2JqPZ"
        self.doc_store = ElasticsearchDocumentStore(
            host = "localhost",
            port = 9200,
            scheme = "https",
            username = es_user,
            password = es_password,
            verify_certs = False,
            index = self.unit
        )
        curr_documents = self.doc_store.get_all_documents(index=self.unit, filters={"source": {"$eq": answer}})
        self.html = ""
        step = (maxa - mina) / max(self.unit_freq.values()) #maybe do max(1, ___) to get rid of x/0 issues
        for i in range(len(curr_documents)):
            if i in self.unit_freq:
                self.add_html(curr_documents[i].content, r, g, b, mina + (step * self.unit_freq[i]))
            else:
                self.add_html(curr_documents[i].content, r, g, b, mina)
        self.html += f"<p style=\"background-color: rgba({r},{g},{b},{0})\">{self.unit_freq}</p>"
        file = open(f"sample/{answer}.html", "w")
        file.write(self.html)
        file.close()