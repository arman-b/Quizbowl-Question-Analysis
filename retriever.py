from abc import ABC, abstractmethod
from typing import List
import json

class Retriever(ABC):

    @abstractmethod
    def retrieve(self, query, num_results=10):
        pass
    
    @abstractmethod
    def read(self, query, num_results=10):
        pass

    @property
    @abstractmethod
    def contexts(self):
        pass
    
    @property
    @abstractmethod
    def metrics(self) -> List[str]:
        pass

    @metrics.setter
    @abstractmethod
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
        es_password = "vqyxbiHqq=jbB4l2JqPZ"

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
            self.doc_store = ElasticsearchDocumentStore(
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
            article = "Osmosis"
            pgs = wiki_json[article]['text'].split('\n\n')[1:]
            num_pgs = len(pgs)

            for i, paragraph in enumerate(pgs):
                dict_to_add =\
                    {
                        'content': paragraph,
                        'meta': {
                            'source': wiki_json[article]['title'],
                            'id': wiki_json[article]['id'],
                            'paragraph_number': i,
                            'paragraph_number_norm': i/num_pgs
                        }
                    }
                data_json.append(dict_to_add)
            print(data_json)
            self.doc_store.write_documents(data_json, duplicate_documents="skip")
            print(self.retrieve('When was the observation of osmosis first documented?', 10))
            print(self.read('When was the observation of osmosis first documented?', 10, 5))
            # for article in wiki_json:
            #     pgs = wiki_json[article]['text'].split('\n\n')
            #     num_pgs = len(pgs)

            #     for i, paragraph in enumerate(pgs):
            #         dict_to_add =\
            #             {
            #                 'content': paragraph,
            #                 'meta': {
            #                     'source': wiki_json[article]['title'],
            #                     'id': wiki_json[article]['id'],
            #                     'paragraph_number': i,
            #                     'paragraph_number_norm': i/num_pgs
            #                 }
            #             }
            #         data_json.append(dict_to_add)
            
            # doc_store.write_documents(data_json)

        else:
            raise("Elasticsearch cluster error")

        # Add indexes to elastic search
        # Idea: create different indexes for sentence, chunks, paragraphs
            # Must include meta data for each document (Wiki page, sentence/chunks/paragraphs (normalized and unnormalized))
                # Sentence = sent tokenizer
                # Chunks = already written
                # Paragraph = split by \n\n
            # Wikipedia is 500 MB --> Doing all 3 segmentations should be 1.5 GB total

    def retrieve(self, query, num_results=10):
        from haystack.nodes import DensePassageRetriever
        self.retriever = DensePassageRetriever(
            document_store=self.doc_store,
            query_embedding_model='facebook/dpr-question_encoder-single-nq-base',
            passage_embedding_model='facebook/dpr-ctx_encoder-single-nq-base',
            top_k=num_results,
            use_gpu=True,
            embed_title=True
        )
        self.doc_store.update_embeddings(retriever=self.retriever)
        return self.retriever.retrieve(query)
    
    def read(self, query, retrieve_num=10, read_num=5):
        from haystack.nodes import FARMReader
        from haystack.pipelines import ExtractiveQAPipeline
        self.reader = FARMReader(model_name_or_path="deepset/roberta-base-squad2", use_gpu=True)
        pipe = ExtractiveQAPipeline(self.reader, self.retriever)
        return pipe.run(
            query=query,
            params={
                "Retriever": {"top_k": retrieve_num},
                "Reader": {"top_k": read_num}
            }
        )
        

    
    def contexts(self):
        return self.es # maybe es.indexes() or smth

    def metrics(self) -> List[str]:
        self._metrics

    def metrics(self, metrics: List[str]) -> List[str]:
        self._metrics = metrics



