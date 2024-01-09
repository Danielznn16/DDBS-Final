docker cp mongo_drop.sh ddbs_mongo_1_bak:/root
docker exec -it ddbs_mongo_1_bak bash /root/mongo_drop.sh
