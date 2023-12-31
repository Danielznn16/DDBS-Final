from pymongo import MongoClient
from tqdm import tqdm
clients = zip(
        [
            MongoClient(host="ddbs_mongo_1", port=27017),
            MongoClient(host="ddbs_mongo_2", port=27017),
        ],
        [
            MongoClient(host="ddbs_mongo_1_bak", port=27017),
            MongoClient(host="ddbs_mongo_2_bak", port=27017),
        ]
    )



for db1_client, db2_client in clients:
    db1_client.history.read.create_index([("aid",1)])
    db2_client.history.read.create_index([("aid",1)])

    for article in tqdm(db2_client.info.article.find({}), total=10000):
        aid = article["aid"]
        beread = dict(
            id=article["id"],
            timestamp=list(),
            aid=aid,
            readNum = 0,
            readUidList = list(),
            commentNum = 0,
            commentUidList = list(),
            agreeNum = 0,
            agreeUidList = list(),
            shareNum = 0,
            shareUidList = list(),
            )

        for read_record in db1_client.history.read.find(dict(aid=aid)):
            beread["timestamp"].append(read_record["timestamp"])
            beread["readNum"]+=1
            beread["readUidList"].append(read_record["uid"])
            if int(read_record["commentOrNot"]):
                beread["commentNum"]+=1
                beread["commentUidList"].append(read_record["uid"])
            if int(read_record["agreeOrNot"]):
                beread["agreeNum"]+=1
                beread["agreeUidList"].append(read_record["uid"])
            if int(read_record["shareOrNot"]):
                beread["shareNum"]+=1
                beread["shareUidList"].append(read_record["uid"])

        for read_record in db2_client.history.read.find(dict(aid=aid)):
            beread["timestamp"].append(read_record["timestamp"])
            beread["readNum"]+=1
            beread["readUidList"].append(read_record["uid"])
            if int(read_record["commentOrNot"]):
                beread["commentNum"]+=1
                beread["commentUidList"].append(read_record["uid"])
            if int(read_record["agreeOrNot"]):
                beread["agreeNum"]+=1
                beread["agreeUidList"].append(read_record["uid"])
            if int(read_record["shareOrNot"]):
                beread["shareNum"]+=1
                beread["shareUidList"].append(read_record["uid"])

        db2_client.history.beread.update_one(dict(aid=aid),{"$set":read_record},upsert=True)
        if article["category"] == "science":
            db1_client.history.beread.update_one(dict(aid=aid),{"$set":read_record},upsert=True)
