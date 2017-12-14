import pymongo
from pymongo import MongoClient
from pprint import pprint
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


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

def plot_data(all_data):
   

    fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(9, 5))

     
    axes[0].hist(all_data["population"],  histtype='barstacked')

    axes[0].set_title("Population histogram")

    axes[0].set_xlabel("Population")

    axes[0].set_ylabel("Locations count")

    index = np.arange(all_data["population"].count()) 
    axes[1].bar(x=index,
                height=all_data["population"],
                log=True  )

    axes[1].set_title("Population chart")

    axes[1].set_xlabel("Towns, cities, etc.")
    
    axes[1].set_ylabel("Population, log scale")
    
    plt.savefig('foo.png')
 
    return

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
      { "$limit": 6},
      { "$skip": 1}
    ]
    print_list("Top 5 most populated places:",pipeline,db,False) 

    pipeline = [
      { "$match":{"population":{"$exists": "true", "$ne": "null"}} },
      { "$sort":  {"population":-1 } },
      { "$skip": 1}
    ]
    alist = db.nodes.aggregate(pipeline)
    data = pd.DataFrame(list(alist))
    pprint(data.describe())
    data["population"] = pd.to_numeric(data["population"],errors="coerce")
    plot_data(data)

