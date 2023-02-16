from abc import ABC, abstractmethod
from typing import List
import json

class Retriever(ABC):
    @abstractmethod
    def retrieve(self, query, num_results=10):
        pass
    
    @property
    @abstractmethod
    def contexts(self):
        pass
    
    @property
    @abstractmethod
    def unit(self) -> str:
        pass
    
# class RC_Retriever(Retriever):
#     def __init__(self) -> None:
#         self._units = ["chunk", "starting index character"]

# FOLLOW OOD 
class DPR_Retriever(Retriever):
    
    def _chunkz(text, size=512, stride=430):
        chunks = []
        start, end = 0, size
        
        while end < len(text):
            chunks.append(text[start:end])
            start += stride
            end += stride
        
        chunks.append(text[start:-1])
        return chunks
        
    def __init__(self, unit):
        # units
        self.unit = unit
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
        if (self.es is not None and self.es.ping() and
                self.es.cluster.health()['status'] in ['yellow', 'green']):
        # Ensure ES is running        
            self.doc_store = ElasticsearchDocumentStore(
                host = "localhost",
                port = 9200,
                scheme = "https",
                username = es_user,
                password = es_password,
                verify_certs = False,
                index = self.unit
            )

            with open("wiki_lookup.json", "r") as f:
                wiki_json = json.loads(f.read())

            
            data_json = []
            #to-do: add all articles from the wiki in the docstore, for article in wiki_json:
            article = "Osmosis"
            if self.unit == "paragraph":
                doc_list = wiki_json[article]['text'].split('\n\n')[1:]
            elif self.unit == "sentence":
                from nltk.tokenize import sent_tokenize
                doc_list = sent_tokenize(wiki_json[article]['text'])[1:]
            elif self.unit == "chunk":
                raise Exception("unimplemented")
            else:
                raise Exception("not valid unit, choose one of [paragraph, sentence, chunk]")
            for i, self.unit in enumerate(doc_list):
                dict_to_add =\
                    {
                        'content': self.unit,
                        'meta': {
                            'source': wiki_json[article]['title'],
                            'id': wiki_json[article]['id'],
                            'unit_number': i,
                            'unit_number_norm': i/len(doc_list)
                        }
                    }
                data_json.append(dict_to_add)
            self.doc_store.write_documents(data_json, duplicate_documents="skip")
            self.retrieve()
        else:
            raise("Elasticsearch cluster error")

    def retrieve(self, num_results=10):
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
        # return self.retriever.retrieve(query)

    def contexts(self):
        return self.es # maybe es.indexes() or smth

    def unit(self):
        return self.unit



