from flask import Flask, request, Response, render_template
import requests
from pymongo import MongoClient
from tqdm import tqdm
from datetime import datetime
clients = dict(
    db1 = [
        MongoClient(host="ddbs_mongo_1", port=27017),
        MongoClient(host="ddbs_mongo_1_bak", port=27017),
        ],
    db2 = [
        MongoClient(host="ddbs_mongo_2", port=27017),
        MongoClient(host="ddbs_mongo_2_bak", port=27017),
        ]
    )
app = Flask(__name__)

def convert_file_to_path(file_name):
    for client in sum(list(clients.values()),[]):
        try:
            return client.file.mapping.find_one(dict(name=file_name))["path"]
        except:
            pass
    return None


def article_by_id(aid):
    for db2_client in clients["db2"]:
        try:
            article = db2_client.info.article.find_one(dict(aid=aid))
            text_file = article["text"]
            text_location = convert_file_to_path(text_file).replace("0.0.0.0","nginx").strip()
            text = requests.get(text_location).text


            images = [convert_file_to_path(i).replace("0.0.0.0","localhost").strip() for i in article["image"].split(',') if i.strip()]

            videos = [convert_file_to_path(i).replace("0.0.0.0","localhost").strip() for i in article["video"].split(',') if i.strip()] # in the form of url in flv

            return dict(text=text,images=images,videos=videos)
        except:
            pass

def user_by_id(uid):
    for client in sum(list(clients.values()),[]):
        try:
            user = client.info.user.find_one(dict(uid=uid))
            if user:
                return user
        except:
            pass
    return dict(message="User Not Found")

def find_user_read_list(uid):
    for client in sum(list(clients.values()),[]):
        try:
            history = list(client.history.read.find(dict(uid=uid)))
            if history:
                return history
        except:
            pass
    return []

def get_popular_rank(grainaty, rid):
    for client in clients["db1" if grainaty=="daily" else "db2"]:
        try:
            rank = client.history.popular_rank.find_one(dict(temporalGranularity=grainaty, id=rid))
            if rank:
                return rank
        except:
            pass
    return None

@app.route("/frontend/article/<aid>")
def get_article(aid: str):
    return render_template('article.html', aid=aid, **article_by_id(aid))

@app.route("/frontend/user/<uid>")
def get_user(uid: str):
    user = user_by_id(uid)
    history = find_user_read_list(uid)
    history = [dict(text=article_by_id(i["aid"])["text"], **i) for i in history]
    for i in range(len(history)):
        history[i]["location"] = f"/frontend/article/{history[i]['aid']}"
        del history[i]["_id"]
    return render_template('user_history.html', user=user, history=history)

@app.route("/frontend/popular_rank/<grainaty>/<rid>")
def get_popular_rank_route(grainaty: str, rid: str):
    rid = int(rid)
    rank = get_popular_rank(grainaty, rid)
    rank["article_list"] = [dict(text=article_by_id(i)["text"], aid=i) for i in rank["articleAidList"]]
    
    # Convert the timestamp to a Date
    timestamp = int(rank["timestamp"]) / 1000
    rank["begin_date"] = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')

    del rank["timestamp"]
    return render_template('popular_rank.html', rank=rank)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8060)
