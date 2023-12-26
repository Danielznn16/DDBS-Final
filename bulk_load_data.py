# Code used to bulk seperate and then load data
from utils import load_jsonl, dump_jsonl, StreamDumpBuffer, get_container_names
from threading import Thread
from tqdm import tqdm
import subprocess

db1_user_set = set()
db2_user_set = set()
# Users
users_db_1_data_buffer = StreamDumpBuffer()
users_db_2_data_buffer = StreamDumpBuffer()

users_db_1_out_thread = Thread(target=dump_jsonl, args=(users_db_1_data_buffer, "ddbs_1_data/user.jsonl"))
users_db_2_out_thread = Thread(target=dump_jsonl, args=(users_db_2_data_buffer, "ddbs_2_data/user.jsonl"))

users_db_1_out_thread.start()
users_db_2_out_thread.start()

for slic in tqdm(load_jsonl("db-generation/user.dat")):
	if slic["region"]=="Beijing":
		users_db_1_data_buffer(slic)
		db1_user_set.add(slic["uid"])
	elif slic["region"]=="Hong Kong":
		users_db_2_data_buffer(slic)
		db2_user_set.add(slic["uid"])
	else:
		print(slic)
		assert(slic["region"] in ["Beijing", "HongKong"])

users_db_1_data_buffer.done()
users_db_2_data_buffer.done()

# Articles
articles_db_1_data_buffer = StreamDumpBuffer()
articles_db_2_data_buffer = StreamDumpBuffer()

articles_db_1_out_thread = Thread(target=dump_jsonl, args=(articles_db_1_data_buffer, "ddbs_1_data/article.jsonl"))
articles_db_2_out_thread = Thread(target=dump_jsonl, args=(articles_db_2_data_buffer, "ddbs_2_data/article.jsonl"))

articles_db_1_out_thread.start()
articles_db_2_out_thread.start()

for slic in tqdm(load_jsonl("db-generation/article.dat")):
	if slic["category"]=="science":
		articles_db_1_data_buffer(slic)
		articles_db_2_data_buffer(slic)
	elif slic["category"]=="technology":
		articles_db_2_data_buffer(slic)
	else:
		print(slic)
		assert(slic["category"] in ["science", "technology"])

articles_db_1_data_buffer.done()
articles_db_2_data_buffer.done()

# Read
reads_db_1_data_buffer = StreamDumpBuffer()
reads_db_2_data_buffer = StreamDumpBuffer()

reads_db_1_out_thread = Thread(target=dump_jsonl, args=(reads_db_1_data_buffer, "ddbs_1_data/read.jsonl"))
reads_db_2_out_thread = Thread(target=dump_jsonl, args=(reads_db_2_data_buffer, "ddbs_2_data/read.jsonl"))

reads_db_1_out_thread.start()
reads_db_2_out_thread.start()

for slic in tqdm(load_jsonl("db-generation/read.dat")):
	if slic["uid"] in db1_user_set:
		reads_db_1_data_buffer(slic)
	elif slic["uid"] in db2_user_set:
		reads_db_2_data_buffer(slic)
	else:
		print(slic)
		assert(slic["uid"] in db1_user_set or slic["uid"] in db2_user_set)

reads_db_1_data_buffer.done()
reads_db_2_data_buffer.done()

# Clearning Up
users_db_1_out_thread.join()
users_db_2_out_thread.join()
articles_db_1_out_thread.join()
articles_db_2_out_thread.join()
reads_db_1_out_thread.join()
reads_db_2_out_thread.join()


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