# from questgen.heatmap_generator import HeatmapGenerator as HeatmapGenerator
# from questgen.reader import Reader as Reader
# from questgen.retriever import Retriever as Retriever
import logging
import sys

# logging.basicConfig(level=logging.DEBUG,
#     filename="questgen.log",
#     format='%(asctime)s %(name)s %(levelname)s:%(message)s')

# loggers = logging.getLogger(__name__).addHandler(logging.StreamHandler(sys.stdout))
# .addHandler(logging.StreamHandler(sys.stdout)) # logging.StreamHandler() => stderr

# Create the Logger
loggers = logging.getLogger(__name__)
loggers.setLevel(logging.DEBUG)

# Create the Handler for logging data to a file
file_handler = logging.FileHandler(filename="questgen.log")
file_handler.setLevel(logging.DEBUG)

stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setLevel(logging.DEBUG)

# Create a Formatter for formatting the log messages
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Add the Formatter to the Handler
file_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)

# Add the Handler to the Logger
loggers.addHandler(file_handler)
loggers.addHandler(stream_handler)
loggers.info('Completed configuring logger()!') 
