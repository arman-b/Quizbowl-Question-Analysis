from abc import ABC, abstractmethod
from typing import List
import json
from haystack.nodes import FARMReader
from haystack.pipelines import ExtractiveQAPipeline

class Reader():
    def __init__(self, name="deepset/roberta-base-squad2"):
        self.reader = FARMReader(model_name_or_path=name, use_gpu=True)