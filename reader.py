from typing import List
from haystack.nodes import FARMReader
import logging

class Reader():
    def __init__(self, name : str ="deepset/roberta-base-squad2"):
        logging.info(f"Inititializing reader {name}")
        self.haystack_reader = FARMReader(model_name_or_path=name, use_gpu=True)