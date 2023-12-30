#!/bin/bash

# Bring down any currently running containers
docker-compose down

# Create directories
mkdir -p ./ddbs_1_data
mkdir -p ./ddbs_2_data

# Start the Docker Compose services in detached mode
docker-compose up -d

# Function to check if a Docker container is healthy
is_container_healthy() {
    [[ "$(docker inspect -f '{{.State.Health.Status}}' "$1" 2>/dev/null)" == 'healthy' ]]
}

# Wait for containers to become healthy
echo "Waiting for containers to become healthy..."
for container in namenode datanode1 datanode2 datanode3; do
    while ! is_container_healthy "$container"; do
        echo "Waiting for $container..."
        sleep 5
    done
done
echo "All containers are up and running."

# Run your Python script
python3 bulk_load_data.py

# Execute command inside the container
# docker exec -it ddbsNamenode bash -c "hadoop fs -mkdir -p /articles"
# docker exec -it ddbsNamenode bash -c "hadoop fs -chmod -R 777 /articles"
# docker exec -it ddbsNamenode bash -c "hadoop fs -put /buffer/* /articles/"
