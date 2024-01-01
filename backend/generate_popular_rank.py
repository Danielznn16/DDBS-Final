from pymongo import MongoClient
from datetime import datetime
from bson.son import SON

clients = [
        [
            MongoClient(host="ddbs_mongo_1", port=27017),
            MongoClient(host="ddbs_mongo_2", port=27017),
        ],
        [
            MongoClient(host="ddbs_mongo_1_bak", port=27017),
            MongoClient(host="ddbs_mongo_2_bak", port=27017),
        ]
    ]

def get_daily_top_articles(client):
    pipeline = [
            {
                '$unwind': '$timestamp'
            }, {
                '$addFields': {
                    'timestampDate': {
                        '$dateFromString': {
                            'dateString': '$timestamp'
                        }
                    }
                }
            }, {
                '$project': {
                    'year': {
                        '$year': '$timestampDate'
                    }, 
                    'day': {
                        '$dayOfYear': '$timestampDate'
                    }, 
                    'aid': '$aid'
                }
            }, {
                '$group': {
                    '_id': {
                        'year': '$year', 
                        'day': '$day', 
                        'aid': '$aid'
                    }, 
                    'accessCount': {
                        '$sum': 1
                    }
                }
            }, {
                '$sort': {
                    '_id.year': 1, 
                    '_id.day': 1, 
                    'accessCount': -1
                }
            }, {
                '$group': {
                    '_id': {
                        'year': '$_id.year', 
                        'day': '$_id.day'
                    }, 
                    'articles': {
                        '$push': {
                            'aid': '$_id.aid', 
                            'accessCount': '$accessCount'
                        }
                    }
                }
            }, {
                '$project': {
                    'articles': {
                        '$slice': [
                            '$articles', 5
                        ]
                    }, 
                    'year': '$_id.year', 
                    'dayOfYear': '$_id.day'
                }
            }, {
                '$addFields': {
                    'date': {
                        '$function': {
                            'body': 'function(year, dayOfYear) { return new Date(Date.UTC(year, 0, dayOfYear)); }', 
                            'args': [
                                '$year', '$dayOfYear'
                            ], 
                            'lang': 'js'
                        }
                    }
                }
            }, {
                '$project': {
                    'timestamp': {
                        '$toLong': '$date'
                    }, 
                    'temporalGranularity': 'daily', 
                    'articleAidList': '$articles.aid'
                }
            }
        ]
    results = client.aggregate(pipeline, allowDiskUse=True)
    return sorted(list(results),key=lambda x: x["timestamp"])

def get_weekly_top_articles(client):
    pipeline = [
            {
                '$unwind': '$timestamp'
            }, {
                '$addFields': {
                    'timestampDate': {
                        '$dateFromString': {
                            'dateString': '$timestamp'
                        }
                    }
                }
            }, {
                '$addFields': {
                    'firstDayOfWeek': {
                        '$subtract': [
                            '$timestampDate', {
                                '$multiply': [
                                    {
                                        '$subtract': [
                                            {
                                                '$dayOfWeek': '$timestampDate'
                                            }, 1
                                        ]
                                    }, 86400000
                                ]
                            }
                        ]
                    }
                }
            }, {
                '$project': {
                    'year': {
                        '$year': '$firstDayOfWeek'
                    }, 
                    'day': {
                        '$dayOfYear': '$firstDayOfWeek'
                    }, 
                    'aid': '$aid'
                }
            }, {
                '$group': {
                    '_id': {
                        'year': '$year', 
                        'day': '$day', 
                        'aid': '$aid'
                    }, 
                    'accessCount': {
                        '$sum': 1
                    }
                }
            }, {
                '$sort': {
                    '_id.year': 1, 
                    '_id.day': 1, 
                    'accessCount': -1
                }
            }, {
                '$group': {
                    '_id': {
                        'year': '$_id.year', 
                        'day': '$_id.day'
                    }, 
                    'articles': {
                        '$push': {
                            'aid': '$_id.aid', 
                            'accessCount': '$accessCount'
                        }
                    }
                }
            }, {
                '$project': {
                    'articles': {
                        '$slice': [
                            '$articles', 5
                        ]
                    }, 
                    'year': '$_id.year', 
                    'dayOfYear': '$_id.day'
                }
            }, {
                '$addFields': {
                    'date': {
                        '$function': {
                            'body': 'function(year, dayOfYear) { return new Date(Date.UTC(year, 0, dayOfYear)); }', 
                            'args': [
                                '$year', '$dayOfYear'
                            ], 
                            'lang': 'js'
                        }
                    }
                }
            }, {
                '$project': {
                    'timestamp': {
                        '$toLong': '$date'
                    }, 
                    'temporalGranularity': 'weekly',
                    "articleAidList": "$articles.aid"
                }
            }
        ]
    results = client.aggregate(pipeline)
    return sorted(list(results),key=lambda x: x["timestamp"])

def get_monthly_top_articles(client):
    pipeline = [
        {
            '$unwind': '$timestamp'
        }, {
            '$addFields': {
                'timestampDate': {
                    '$dateFromString': {
                        'dateString': '$timestamp'
                    }
                }
            }
        }, {
            '$project': {
                'year': {
                    '$year': '$timestampDate'
                }, 
                'month': {
                    '$month': '$timestampDate'
                }, 
                'aid': '$aid'
            }
        }, {
            '$group': {
                '_id': {
                    'year': '$year', 
                    'month': '$month', 
                    'aid': '$aid'
                }, 
                'accessCount': {
                    '$sum': 1
                }
            }
        }, {
            '$sort': {
                '_id.year': 1, 
                '_id.month': 1, 
                'accessCount': -1
            }
        }, {
            '$group': {
                '_id': {
                    'year': '$_id.year', 
                    'month': '$_id.month'
                }, 
                'articles': {
                    '$push': {
                        'aid': '$_id.aid', 
                        'accessCount': '$accessCount'
                    }
                }
            }
        }, {
            '$project': {
                'articles': {
                    '$slice': [
                        '$articles', 5
                    ]
                }, 
                'year': '$_id.year', 
                'month': '$_id.month'
            }
        }, {
            '$addFields': {
                'date': {
                    '$dateFromParts': {
                        'year': '$year', 
                        'month': '$month'
                    }
                }
            }
        }, {
            '$project': {
                'timestamp': {
                    '$toLong': '$date'
                }, 
                'temporalGranularity': 'monthly', 
                'articleAidList': '$articles.aid'
            }
        }
    ]

    results = client.aggregate(pipeline)
    return sorted(list(results),key=lambda x: x["timestamp"])

# Example usage
for db1_client, db2_client in clients:
    top_articles = list()
    # Daily
    top_articles += get_daily_top_articles(db2_client.history.beread)
    top_articles += get_weekly_top_articles(db2_client.history.beread)
    top_articles += get_monthly_top_articles(db2_client.history.beread)

    for _id, a in enumerate(top_articles):
        a["id"]=_id
        del a["_id"]
        if a["temporalGranularity"] == "daily":
            db1_client.history.popular_rank.update_one(dict(timestamp=a["timestamp"]), {"$set":a},upsert=True)
        else:
            db2_client.history.popular_rank.update_one(dict(timestamp=a["timestamp"]), {"$set":a},upsert=True)
