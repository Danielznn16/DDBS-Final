from flask import Flask, request, Response, render_template
import requests
from pymongo import MongoClient
from tqdm import tqdm
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


@app.route("/frontend/article/<aid>")
def get_article(aid: str):
    for db2_client in clients["db2"]:
        article = db2_client.info.article.find_one(dict(aid=aid))
        text_file = article["text"]
        text = convert_file_to_path(text_file).replace("0.0.0.0","nginx")
        # text = requests.get(text, stream=True).text


        images = [convert_file_to_path(i).replace("0.0.0.0","localhost") for i in article["image"].split(',') if i.strip()]

        videos = [convert_file_to_path(i).replace("0.0.0.0","localhost") for i in article["video"].split(',') if i.strip()] # in the form of url in flv

        # Make a simple webpage to display everything
        return render_template('article.html', aid=aid, text=str(text), images=images, videos=videos)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8060)
