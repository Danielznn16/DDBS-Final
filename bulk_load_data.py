# Code used to bulk seperate and then load data
from time import sleep
from utils import load_jsonl
import json
from threading import Thread
from tqdm import tqdm
import subprocess

# To wait for docker
sleep(10)

db1_user_set = set()
db2_user_set = set()

# Users
user_db_1_out = open("ddbs_1_data/user.jsonl",'w')
user_db_2_out = open("ddbs_2_data/user.jsonl",'w')

for slic in tqdm(load_jsonl("db-generation/user.dat")):
	if slic["region"]=="Beijing":
		user_db_1_out.write(json.dumps(slic)+"\n")
		db1_user_set.add(slic["uid"])
	elif slic["region"]=="Hong Kong":
		user_db_2_out.write(json.dumps(slic)+"\n")
		db2_user_set.add(slic["uid"])
	else:
		print(slic)
		assert(slic["region"] in ["Beijing", "HongKong"])

article_db_1_out = open("ddbs_1_data/article.jsonl",'w')
article_db_2_out = open("ddbs_2_data/article.jsonl",'w')

for slic in tqdm(load_jsonl("db-generation/article.dat")):
	if slic["category"]=="science":
		article_db_1_out.write(json.dumps(slic)+"\n")
		article_db_2_out.write(json.dumps(slic)+"\n")
	elif slic["category"]=="technology":
		article_db_2_out.write(json.dumps(slic)+"\n")
	else:
		print(slic)
		assert(slic["category"] in ["science", "technology"])

read_db_1_out = open("ddbs_1_data/read.jsonl",'w')
read_db_2_out = open("ddbs_2_data/read.jsonl",'w')

for slic in tqdm(load_jsonl("db-generation/read.dat")):
	if slic["uid"] in db1_user_set:
		read_db_1_out.write(json.dumps(slic)+"\n")
	elif slic["uid"] in db2_user_set:
		read_db_2_out.write(json.dumps(slic)+"\n")
	else:
		print(slic)
		assert(slic["uid"] in db1_user_set or slic["uid"] in db2_user_set)

# Bulk Load With Mongo's mongo restore
def import_data_to_mongo(container_name):
	print(f"Loading for {container_name}")
	# Change the working directory to 'data_load'
	data_load_path = '/data_load'  # Update with the actual path to your 'data_load' directory

	# Import user.jsonl into the user table
	subprocess.run(['docker', 'exec', container_name, 'mongoimport', f'--db=info', '--collection=user', f'{data_load_path}/user.jsonl'])

	# Import article.jsonl into the article table
	subprocess.run(['docker', 'exec', container_name, 'mongoimport', f'--db=info', '--collection=article', f'{data_load_path}/article.jsonl'])

	# Import read.json into the read table
	subprocess.run(['docker', 'exec', container_name, 'mongoimport', f'--db=history', '--collection=read', f'{data_load_path}/read.jsonl'])

mongo_containers = sorted(get_container_names(prefix="ddbs_mongo_"),key=lambda x:len(x))
for container in mongo_containers:
	import_data_to_mongo(container)