from abc import ABC, abstractmethod
from typing import List

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
        self._metrics = ["sentence", "chunks", "paragraphs"]

        # Set up elasticsearch
        es_user = "elastic"
        es_password = "RZJVsRjjv7ZeD6lezInf"

        from elasticsearch import Elasticsearch
        self.es = Elasticsearch(
            f"http://{es_user}:{es_password}@localhost:9200",
            use_ssl=True,
            verify_certs=False,
            ssl_show_warn=False
        )

        # Ensure ES is running
        if (self.es is not None and self.es.ping() and
                self.es.cluster.health()['status'] in ['yellow', 'green']):

        else:
            raise("Elasticsearch cluster error")

        # Add indexes to elastic search
        # Idea: create different indexes for sentence, chunks, paragraphs
            # Must include meta data for each document (Wiki page, sentence/chunks/paragraphs (normalized and unnormalized))
                # Sentence = sent tokenizer
                # Chunks = already written
                # Paragraph = split by \n
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