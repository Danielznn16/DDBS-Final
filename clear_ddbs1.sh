docker cp mongo_drop.sh ddbs_mongo_1:/root
docker exec -it ddbs_mongo_1 bash /root/mongo_drop.sh
