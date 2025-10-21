import jsonpickle
from json2html import *
from loguru import logger
import time
from netbox_network_importer.config import get_config

TIMESTAMP = time.strftime("%Y%m%d-%H%M%S")


def json_output(results: dict):
    try:
        OUTPUT_DIR = get_config()['config'].get('OUTPUT_DIR')
        json_file_path = f"{OUTPUT_DIR}/{TIMESTAMP}-result.json"
        json_data = jsonpickle.encode(
            results, keys=True, max_depth=20, indent=4)
        with open(json_file_path, "w") as outfile:
            outfile.write(json_data)
    except Exception as e:
        logger.error("Unable to results as json")
        logger.error(e)


def html_output(results: dict):
    try:
        OUTPUT_DIR = get_config()['config'].get('OUTPUT_DIR')
        html_file_path = f"{OUTPUT_DIR}/{TIMESTAMP}-result.html"
        html_json_data = jsonpickle.encode(results, keys=True, max_depth=20)
        html_data = json2html.convert(json=html_json_data)
        with open(html_file_path, "w") as outfile:
            outfile.write(html_data)
    except Exception as e:
        logger.error("Unable to results as html")
        logger.error(e)
