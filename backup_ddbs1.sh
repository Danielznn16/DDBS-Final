docker cp mongo_dump.sh ddbs_mongo_1:/root
docker exec -it ddbs_mongo_1 bash /root/mongo_dump.sh
