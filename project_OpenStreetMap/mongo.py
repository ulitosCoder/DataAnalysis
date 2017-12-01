import pymongo
from pymongo import MongoClient
from bson import json_util
from pprint import pprint




if __name__ == "__main__":
    client = MongoClient()
    db = client.test

    print( db.nodes.count())

    print( "Number of nodes: {0}", db.nodes.find({"type":"node"}).count() )

    print( "Number of ways: {0}", db.nodes.find({"type":"way"}).count() )

#"Number of unique users: %d",
    pprint( db.nodes.find().distinct("created.user") )

    #pprint(db.nodes.find_one({"type":"node"})) 
