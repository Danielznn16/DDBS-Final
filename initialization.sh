#!/bin/bash

# Bring down any currently running containers
SECONDS=0
echo "Line $LINENO: $(date) - Command took $SECONDS seconds"; SECONDS=0
docker-compose down

rm db-generation/articles/mapping_results.txt

echo "Line $LINENO: $(date) - Command took $SECONDS seconds"; SECONDS=0
# Create directories
mkdir -p ./ddbs_1_data
mkdir -p ./ddbs_2_data

mkdir -p ./dfs_1_data
mkdir -p ./dfs_2_data

# Start the Docker Compose services in detached mode
docker-compose up -d
echo "Line $LINENO: $(date) - Command took $SECONDS seconds"; SECONDS=0

# Run your Python script
python3 bulk_load_data.py
echo "Line $LINENO: $(date) - Command took $SECONDS seconds"; SECONDS=0
sleep 5;
echo "Line $LINENO: $(date) - Command took $SECONDS seconds"; SECONDS=0
python3 post_bulk_load_data.py
echo "Line $LINENO: $(date) - Command took $SECONDS seconds"; SECONDS=0
docker exec -it python-app bash -c "cd /usr/src/app/ && python3 ./generate_beread.py"
echo "Line $LINENO: $(date) - Command took $SECONDS seconds"; SECONDS=0
docker exec -it python-app bash -c "cd /usr/src/app/ && python3 ./generate_popular_rank.py"
echo "Line $LINENO: $(date) - Command took $SECONDS seconds"; SECONDS=0

docker cp bulk_load_file.sh storage0:/etc/fdfs_buffer/
echo "Line $LINENO: $(date) - Command took $SECONDS seconds"; SECONDS=0

echo "Uploading Files"
docker exec -it storage0 bash -c "cd /etc/fdfs_buffer/ && bash ./bulk_load_file.sh"
echo "Line $LINENO: $(date) - Command took $SECONDS seconds"; SECONDS=0

mv db-generation/articles/mapping_results.txt backend/mapping_results.txt
python3 ./update_file_path.py
echo "Line $LINENO: $(date) - Command took $SECONDS seconds"; SECONDS=0
