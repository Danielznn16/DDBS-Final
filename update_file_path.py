# Code used to bulk seperate and then load data
from time import sleep
from utils import load_jsonl, dump_jsonl, get_container_names
from threading import Thread
from tqdm import tqdm
import subprocess

# To wait for docker

# Bulk Load With Mongo's mongo restore
def import_data_to_mongo(container_name):
	print(f"Loading for {container_name}")
	# Change the working directory to 'data_load'
	data_load_path = '/data_load'  # Update with the actual path to your 'data_load' directory

	# Import user.jsonl into the user table
	subprocess.run(['docker', 'exec', container_name, 'mongoimport', f'--db=file', '--collection=mapping', f'{data_load_path}/file_map.jsonl'])



mongo_containers = sorted(get_container_names(prefix="ddbs_mongo_"),key=lambda x:len(x))


def refresh_file():
	in_file = open("backend/mapping_results.txt",'r').readlines()
	in_file = [i.split(" --> ") for i in in_file if i.strip()]
	mapping = dict()
	for k,v in in_file:
		mapping[k]=v
	mapping = [dict(name=k,path=v) for k,v in mapping.items()]
	dump_jsonl(mapping,"ddbs_1_data/file_map.jsonl")
	dump_jsonl(mapping,"ddbs_2_data/file_map.jsonl")

refresh_file()
for container in mongo_containers:
	import_data_to_mongo(container)