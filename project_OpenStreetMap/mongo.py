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

