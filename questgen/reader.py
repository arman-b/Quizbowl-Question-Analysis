from typing import List
from haystack.nodes import FARMReader
import logging

logger = logging.getLogger(__name__)

class Reader():
    def __init__(self, name : str ="deepset/roberta-base-squad2"):
        logger.info(f"Inititializing reader {name}")
        self.haystack_reader = FARMReader(model_name_or_path=name, use_gpu=True)