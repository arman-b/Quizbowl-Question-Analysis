from abc import ABC, abstractmethod
from typing import List
import json
import logging
from elasticsearch import Elasticsearch
from haystack.document_stores import ElasticsearchDocumentStore
from haystack.nodes import DensePassageRetriever

logger = logging.getLogger(__name__)

class Retriever(ABC):
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
        
    def __init__(self, unit):
        # units
        if unit not in ['sentence', 'paragraph']:
            logger.error("Invalid unit to divide Wikipedia article.")
            raise Exception("Invalid unit to divide Wikipedia article.")
        self.unit = unit

        # Set up elasticsearch
        es_user = "elastic"
        es_password = "RZJVsRjjv7ZeD6lezInf" # "vqyxbiHqq=jbB4l2JqPZ"

        logger.info("Attempting to connect to Elasticsearch on port 9200.")
        self.es = Elasticsearch(
            f"http://{es_user}:{es_password}@localhost:9200",
            use_ssl=True,
            verify_certs=False,
            ssl_show_warn=False
        )

        if (self.es is not None and self.es.ping() and
                self.es.cluster.health()['status'] in ['yellow', 'green']):
            # Ensure ES is running
            logger.info("Successfully connected to Elasticsearch.")
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
                raise Exception("Dividing article into chunks is not implemented.")
            else:
                raise Exception("Not valid unit, choose one of [paragraph, sentence, chunk]")
            
            logger.info(f"Adding embeddings for article {article}.")
            for i, doc in enumerate(doc_list):
                logger.debug(f"Adding {unit} {i}/{len(doc_list)}: {doc}")
                dict_to_add =\
                    {
                        'content': doc,
                        'meta': {
                            'source': wiki_json[article]['title'],
                            'id': wiki_json[article]['id'],
                            'unit_number': i,
                            'unit_number_norm': i/len(doc_list)
                        }
                    }
                data_json.append(dict_to_add)
            
            logger.info(f"Attempting to write all {len(doc_list)} documents.")
            self.doc_store.write_documents(data_json, duplicate_documents="skip", index=self.unit)
            self.haystack_retriever = DensePassageRetriever(
                document_store=self.doc_store,
                query_embedding_model='facebook/dpr-question_encoder-single-nq-base',
                passage_embedding_model='facebook/dpr-ctx_encoder-single-nq-base',
                top_k=10,
                use_gpu=True,
                embed_title=True
            )

            self.doc_store.update_embeddings(retriever=self.haystack_retriever,
                update_existing_embeddings=False)
        else:
            raise("Elasticsearch cluster error")
        
    # def _chunkz(text, size=512, stride=430):
    #     chunks = []
    #     start, end = 0, size
        
    #     while end < len(text):
    #         chunks.append(text[start:end])
    #         start += stride
    #         end += stride
        
    #     chunks.append(text[start:-1])
    #     return chunks

    def contexts(self):
        return self.es # maybe es.indexes() or smth

    def unit(self):
        return self.unit

