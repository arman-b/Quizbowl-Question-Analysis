import json
import pandas as pd
import logging
from questgen.reader import Reader
from questgen.retriever import DPR_Retriever
from questgen.heatmap_generator import HeatmapGenerator

def main():
    logging.basicConfig(filename='tester.log', level=logging.INFO)
    logging.info('Starting')
    logging.info("Loading dataframe from qanta.train.2018.04.18.json.")
    data = json.load(open("data/qanta.train.2018.04.18.json"))
    df = pd.json_normalize(data["questions"])
    logging.info("Only looking at MS questions.")
    # df = df[df["difficulty"] == "MS"]
    # print(df[df["page"] == "Osmosis"])

    generator = HeatmapGenerator(DPR_Retriever('paragraph'), Reader(), 'paragraph')
    generator.get_page_heatmap("Osmosis")
    
    logging.info('Finished')

if __name__ == '__main__':
    main()

