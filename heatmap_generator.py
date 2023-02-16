import json
from reader import Reader
from retriever import Retriever, DPR_Retriever
import pandas as pd
from haystack.pipelines import ExtractiveQAPipeline
import logging

class HeatmapGenerator():
    def __init__(self, retriever:Retriever, reader:Reader, unit:str='paragraph'):
        self.unit = unit
        self.pipeline = ExtractiveQAPipeline(reader.haystack_reader, retriever.haystack_retriever)

        data = json.load(open("qanta.train.2018.04.18.json"))
        self.df = pd.json_normalize(data["questions"])
        wiki = json.load(open("wiki_lookup.json"))
        self.df = self.df[self.df["difficulty"] == "MS"]
        drop_indices = []
        
        for index, row in self.df.iterrows():
            if row["page"] not in wiki:
                drop_indices.append(index)
        self.df = self.df.drop(index=drop_indices)
        self.unit_freq = dict()
    
    def extract_info(self, query, answer, retrieve_num, read_num):
        res = self.pipeline.run(
                    query=query,
                    params={
                        "Retriever": {"top_k": retrieve_num},
                        "Reader": {"top_k": read_num}
                    }
            )
        
        logging.debug(f"Running query: {query}")
        logging.debug(f"\tAnswer: {answer}")
        logging.debug(f"\tResult: {res}\n\n")
        print(query)
        print(answer)
        print(res)
        print("\n\n\n")

        answers = [x.to_dict() for x in res['answers']]
        for ans in answers:
            if ans['answer'] == answer:
                correct_unit_num = ans['meta']['unit_number']
                logging.debug(f"\tCorrect context (part of article): {ans['context']}")
                logging.debug(f"\tCorrect {self.unit}: {correct_unit_num}")

                if correct_unit_num not in self.unit_freq:
                    self.unit_freq[correct_unit_num] = 1
                else:
                    self.unit_freq[correct_unit_num] += 1
           
    def get_page_heatmap(self, page_name, retrieve_num=10, read_num=5):
        curr_df = self.df[self.df["page"] == page_name]

        for index, row in curr_df.iterrows():
            df_question = row["text"]
            from nltk.tokenize import sent_tokenize
            clues = sent_tokenize(df_question)
            for clue in clues:
                self.extract_info(clue, page_name, retrieve_num, read_num)
        
        print(self.unit_freq)