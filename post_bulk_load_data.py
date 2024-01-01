import subprocess
from utils import load_jsonl, get_container_names
# Bulk Load With Mongo's mongo restore
def import_data_to_mongo(container_name):
	print(f"Loading for {container_name}")
	# Change the working directory to 'data_load'
	data_load_path = '/data_load'  # Update with the actual path to your 'data_load' directory

	# Import user.jsonl into the user table
	subprocess.run(['docker', 'exec', '-it', container_name, 'mongoimport', f'--db=info', '--collection=user', f'{data_load_path}/user.jsonl'])

	# Import article.jsonl into the article table
	subprocess.run(['docker', 'exec', '-it', container_name, 'mongoimport', f'--db=info', '--collection=article', f'{data_load_path}/article.jsonl'])

	# Import read.json into the read table
	subprocess.run(['docker', 'exec', '-it', container_name, 'mongoimport', f'--db=history', '--collection=read', f'{data_load_path}/read.jsonl'])

mongo_containers = sorted(get_container_names(prefix="ddbs_mongo_"),key=lambda x:len(x))
for container in mongo_containers:
	import_data_to_mongo(container)