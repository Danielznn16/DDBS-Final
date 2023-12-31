#!/bin/bash

# Bring down any currently running containers
docker-compose down

rm db-generation/articles/mapping_results.txt

# Create directories
mkdir -p ./ddbs_1_data
mkdir -p ./ddbs_2_data

mkdir -p ./dfs_1_data
mkdir -p ./dfs_2_data

# Start the Docker Compose services in detached mode
docker-compose up -d

# Run your Python script
python3 bulk_load_data.py
docker exec -it python-app bash -c "cd /usr/src/app/ && python3 ./generate_beread.py"

docker cp bulk_load_file.sh storage0:/etc/fdfs_buffer/

echo "Uploading Files"
docker exec -it storage0 bash -c "cd /etc/fdfs_buffer/ && bash ./bulk_load_file.sh"

mv db-generation/articles/mapping_results.txt backend/mapping_results.txt
python3 ./update_file_path.py
