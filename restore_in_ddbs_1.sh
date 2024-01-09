docker cp mongo_restore.sh ddbs_mongo_1:/root
docker exec -it ddbs_mongo_1 bash /root/mongo_restore.sh
