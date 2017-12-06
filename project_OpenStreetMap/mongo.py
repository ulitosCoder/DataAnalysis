import pymongo
from pymongo import MongoClient
from pprint import pprint


def print_list(title,pipeline,db, aggregated=True):

    alist = db.nodes.aggregate(pipeline)
    print("\n"+ title + "\n")
    i = 1
    for item in alist:
      if aggregated:
        print( "{}.- Place: {}, count: {}".format(
          i, item["_id"],item["count"]) 
        )
      else:
        print("{}.- {}, pop: {}".format( i,item["name"],item["population"]))
      i = i + 1


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
    print_list("Top 5 type of places:",pipeline,db)
  
    pipeline = [
      { "$match":{"place":{"$exists": "true", "$ne": "null"}} },
      { "$group":{ "_id":"$place", "count": {"$sum":1}}} ,
      { "$sort":  {"count":1 } },
      { "$limit": 3}
    ]
    print_list("Three less common type of places:",pipeline,db)

 
    pipeline = [
      { "$match":{"population":{"$exists": "true", "$ne": "null"}} },
      { "$sort":  {"population":-1 } },
      { "$limit": 5}
    ]
    print_list("Top 5 most poulated places:",pipeline,db,False) 
