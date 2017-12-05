import pymongo
from pymongo import MongoClient
from bson import json_util
from pprint import pprint




if __name__ == "__main__":
    client = MongoClient()
    db = client.test

    print( "Total nodes {0}".format( db.nodes.count()) )

    print( "Number of nodes: {0}".format( 
        db.nodes.find({"type":"node"}).count() ))

    print( "Number of ways: {0}".format(
        db.nodes.find({"type":"way"}).count() ))

    print( "Number of unique users: {0}".format(
        len(db.nodes.find().distinct("created.user")) ))

    print( "Number of unique type of place: {0}".format(
        len(db.nodes.find().distinct("place")) ))

    pipeline = [
      { "$match":{"place":{"$exists": "true", "$ne": "null"}} },
      { "$group":{ "_id":"$place", "count": {"$sum":1}}} ,
      { "$sort":  {"count":-1 } },
      { "$limit": 5}
    ]
    print( "Top 5 type of places:"
	      
    )
    alist = db.nodes.aggregate(pipeline)
    i = 1
    for item in alist:
      print( "{}.- Place: {}, count: {}".format(i, item["_id"],item["count"]) )
      i = i + 1

