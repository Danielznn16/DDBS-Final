docker cp mongo_dump.sh ddbs_mongo_1_bak:/root
docker exec -it ddbs_mongo_1_bak bash /root/mongo_dump.sh

docker cp mongo_restore.sh ddbs_mongo_1:/root
docker exec -it ddbs_mongo_1 bash /root/mongo_restore.sh
