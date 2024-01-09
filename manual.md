<h2>Manual<h2>

[toc]

### TLDR

#### Setup

First clone the repository

```bash
git clone https://github.com/Danielznn16/DDBS-Final.git
cd DDBS-Final
```

Extract the data generation to `db-generation` directory, then run `python3 genTable_mongoDB10G.py`, the resulting file should look similar to

```bash
./
├── Dockerfile
├── backend
│   ├── backend.py
│   ├── generate_beread.py
│   ├── generate_popular_rank.py
│   ├── requirements.txt
│   ├── start.sh
│   └── templates
├── backup_ddbs1.sh
├── bulk_load_data.py
├── bulk_load_file.sh
├── clear_ddbs1.sh
├── clear_ddbs1_bak.sh
├── configs
│   ├── nginx.conf
│   ├── storage.conf
│   ├── storage0.conf
│   └── storage1.conf
├── db-generation
│   ├── article.dat
│   ├── articles
│   ├── bbc_news_texts
│   ├── genTable_mongoDB100G.py
...
├── docker-compose.yml
├── fuse_ddbs1_from_bak.sh
├── initialization.sh
├── mongo_drop.sh
├── mongo_dump.sh
├── mongo_restore.sh
├── post_bulk_load_data.py
├── presentation.pptx
├── restore_in_bak_ddbs1.sh
├── restore_in_ddbs_1.sh
├── startup_log.log
├── update_file_path.py
├── utils.py
```

Make sure to setup docker and docker-compose. For details see [Docker Manual](https://docs.docker.com/engine/install/ubuntu/). Personally I recommend to use Docker-Engine on servers.

Then with python3 install, run

```bash
pip3 install tqdm
```

#### Run

To start the system, run

```bash
chmod +x ./initialization.sh
initialization.sh
```

If everything is set up correctly, and assuming you have already pulled related images before(If you haven't pulling these images and building docker images should be done automatically), you should get something similar to this

```bash
Line 5: Tue Jan  9 16:21:18 CST 2024 - Command took 0 seconds
rm: db-generation/articles/mapping_results.txt: No such file or directory
Line 10: Tue Jan  9 16:21:19 CST 2024 - Command took 1 seconds
...
...
Loading for ddbs_mongo_1_bak
2024-01-09T08:45:15.923+0000	connected to: mongodb://localhost/
2024-01-09T08:45:16.292+0000	30479 document(s) imported successfully. 0 document(s) failed to import.
Loading for ddbs_mongo_2_bak
2024-01-09T08:45:16.408+0000	connected to: mongodb://localhost/
2024-01-09T08:45:16.929+0000	30479 document(s) imported successfully. 0 document(s) failed to import.
Line 43: Tue Jan  9 16:45:16 CST 2024 - Command took 2 seconds
```

Then the system should be completely started.

#### Usage

We created three major APIs

1. http://localhost:9090/frontend/article/1012
   Feel free to change the `1012` to other article ids

   You should get something like this
   ![image-20240109192549664](/Users/zlnn/noICloud/DDBS-Final/manual.assets/image-20240109192549664.png)

2. http://localhost:9090/frontend/popular_rank/daily/1
   This api is in the form of grainularity and popular_rank id, make sure to check the mongodb for ids.
   Resulting output should look like
   ![image-20240109192753250](/Users/zlnn/noICloud/DDBS-Final/manual.assets/image-20240109192753250.png)

3. http://localhost:9090/frontend/user/1012
   Feel free to change user id from `1012` into other ids
   ![image-20240109192828849](/Users/zlnn/noICloud/DDBS-Final/manual.assets/image-20240109192828849.png)

## Detailed Manual

In this section we give a detailed manual of which file does what

### initialization.sh

Overall startup script, contains all steps of startup in one script. it also logs the time spend for each operation

```sh
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
```

### Docker Related

#### Dockerfile

A build file describing how to build the docker image for the python container

### docker-compose.yml

Stores the configuration of all containers started by docker-compose.

```yml
version: "3"

networks:
  ddbs_network:
    driver: bridge


services:
  tracker:
    image: delron/fastdfs
    container_name: tracker
    networks:
      - ddbs_network
    ports:
      - "22122:22122"
    command: "tracker"

  storage0:
    image: delron/fastdfs
    container_name: storage0
    environment:
      - TRACKER_SERVER=tracker:22122
    volumes:
      - ${PWD}/db-generation/articles:/etc/fdfs_buffer/
      # - ${PWD}/dfs_1_data:/etc/fdfs_buffer/
      - ${PWD}/configs/storage0.conf:/etc/fdfs/storage.conf
      - ${PWD}/configs/storage.conf:/usr/local/nginx/conf/nginx.conf
    depends_on:
      - tracker
  ...
```

### Backend Related

#### backend/backend.py

backend implementation for backend service.

#### backend/generate_beread.py

Used to generate the beread table, implemented with raw mongo requests over pymongo.

#### backend/generate_popular_rank.py

Used to generate the popular rank table, implemented with mongo's aggregate api.

#### backend/requirements.txt

The requirement packages needed for the python container, will be installed during build

#### backend/start.sh

Used to start the backend service with delay so docker bridge network's routing can be added to the service

```bash
#!/bin/bash
sleep 10  # Waits 10 seconds
python backend.py
```

#### backend/templates

Stores the html templates used to render the response webpage for backend service

### MongoDB Related

#### bulk_load_data.py

Used to process the input files into files to be imported with `post_bulk_load_data.py`

#### post_bulk_load_data.py

Used to upload the processed data files into mongo.

#### mongo_dump.sh

Used to dump all data for a mongo deployment.

#### backup_ddbs1.sh

Used to dump the content in ddbs1's first replica.

#### mongo_drop.sh

Used to drop all colllections for a mongo deployment.

#### clear_ddbs1.sh

Simulated droping mongo deployment by clearing all data stored in ddbs1's first replica.

#### clear_ddbs1_bak.sh

Simulated droping mongo deployment by clearing all data stored in ddbs1's second replica.

#### mongo_restore.sh

Used to restore all data for a mongo deployment from dumped data.

#### restore_in_ddbs_1.sh

Used to restore the first replica of ddbs1 from files.

#### restore_in_bak_ddbs1.sh

Used to restore the second replica of ddbs1 from files.

#### fuse_ddbs1_from_bak.sh

Transfer the data stored in ddbs1's second replica to its first replica.

### FastDFS Related

#### bulk_load_file.sh

Used to load files into FastDFS.

#### update_file_path.py

Used to upload the path mapping yielded by `bulk_load_file.sh` into mongo deployments.

#### configs/storage.conf

Used to overwrite nginx configuration within storage nodes.

#### configs/storage0.conf

Used to overwrite the Storage configuration in the first storage node.

#### configs/storage1.conf

Used to overwrite the Storage configuration in the second storage node.

### Nginx Related

#### configs/nginx.conf

Used to overwrite nginx configureation in Nginx container.

### Others

#### utils.py

Stores frequently used utils maintained by Daniel and only necessary utils for this project are kept.

