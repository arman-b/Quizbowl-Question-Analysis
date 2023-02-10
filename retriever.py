from abc import ABC, abstractmethod
from typing import List
import json

class Retriever(ABC):

    @abstractmethod
    def retrieve(self, num_results=10):
        pass

    @abstractmethod
    @property
    def contexts(self):
        pass
    
    @abstractmethod
    @property
    def metrics(self) -> List[str]:
        pass

    @abstractmethod
    @metrics.setter
    def metrics(self) -> List[str]:
        pass

# class RC_Retriever(Retriever):
#     def __init__(self) -> None:
#         self._metrics = ["chunk", "starting index character"]

# FOLLOW OOD 
class DPR_Retriever(Retriever):
    def __init__(self):
        # Metrics
        self._metrics = ["sentence", "chunk", "paragraph"]

        # Set up elasticsearch
        es_user = "elastic"
        es_password = "RZJVsRjjv7ZeD6lezInf"

        from elasticsearch import Elasticsearch
        from haystack.document_stores import ElasticsearchDocumentStore

        self.es = Elasticsearch(
            f"http://{es_user}:{es_password}@localhost:9200",
            use_ssl=True,
            verify_certs=False,
            ssl_show_warn=False
        )

        # Ensure ES is running
        if (self.es is not None and self.es.ping() and
                self.es.cluster.health()['status'] in ['yellow', 'green']):
            doc_store = ElasticsearchDocumentStore(
                host = "localhost",
                port = 9200,
                scheme = "https",
                username = es_user,
                password = es_password,
                verify_certs = False,
                index = "test"
            )

            with open("wiki_lookup.json", "r") as f:
                wiki_json = json.loads(f.read())

            data_json = []

            for article in wiki_json:
                pgs = article['text'].split('\n\n')
                num_pgs = len(pgs)

                for i, paragraph in enumerate(pgs):
                    dict_to_add =\
                        {
                            'text': paragraph,
                            'meta': {
                                'source': article['title'],
                                'id': article['id'],
                                'paragraph_number': i,
                                'paragraph_number_norm': i/num_pgs
                            }
                        }
                    data_json.append(dict_to_add)
            
            doc_store.write_documents(data_json)

        else:
            raise("Elasticsearch cluster error")

        # Add indexes to elastic search
        # Idea: create different indexes for sentence, chunks, paragraphs
            # Must include meta data for each document (Wiki page, sentence/chunks/paragraphs (normalized and unnormalized))
                # Sentence = sent tokenizer
                # Chunks = already written
                # Paragraph = split by \n\n
            # Wikipedia is 500 MB --> Doing all 3 segmentations should be 1.5 GB total

    @property
    def contexts(self):
        return self.es # maybe es.indexes() or smth

    @abstractmethod
    @property
    def metrics(self) -> List[str]:
        self._metrics

    @abstractmethod
    @metrics.setter
    def metrics(self, metrics: List[str]) -> List[str]:
        self._metrics = metrics