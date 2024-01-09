docker cp mongo_restore.sh ddbs_mongo_1_bak:/root
docker exec -it ddbs_mongo_1_bak bash /root/mongo_restore.sh
