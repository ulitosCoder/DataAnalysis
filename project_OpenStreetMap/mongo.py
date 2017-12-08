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

def plot_data(data):
   

    # Random test data
    np.random.seed(123)
    all_data = [np.random.normal(0, std, 100) for std in range(1, 4)]
    #pprint(all_data)
    all_data = data

    fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(9, 4))


     
    axes[0].hist(all_data, bins="auto", normed=1, histtype='bar', rwidth=0.8)
    plt.savefig('foo.png')
    return
# rectangular box plot
#    bplot1 = axes[0].boxplot(all_data,
#                         vert=True,   # vertical box aligmnent
#                         patch_artist=True)   # fill with color

# notch shape box plot
#    bplot2 = axes[1].boxplot(all_data,
#                         notch=True,  # notch shape
#                         vert=True,   # vertical box aligmnent
#                         patch_artist=True)   # fill with color

# fill with colors
    colors = ['pink', 'lightblue', 'lightgreen']
    for bplot in (bplot1, bplot2):
      for patch, color in zip(bplot['boxes'], colors):
        patch.set_facecolor(color)

# adding horizontal grid lines
    for ax in axes:
      ax.yaxis.grid(True)
      ax.set_xticks([y+1 for y in range(len(all_data))], )
      ax.set_xlabel('xlabel')
      ax.set_ylabel('ylabel')

# add x-tick labels
#    plt.setp(axes, xticks=[y+1 for y in range(len(all_data))],
#         xticklabels=['x1', 'x2', 'x3', 'x4'])

    plt.savefig('foo.png')
    #plt.show()

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
    print_list("Top 5 most poulated places:",pipeline,db,False) 

    pipeline = [
      { "$match":{"population":{"$exists": "true", "$ne": "null"}} },
      { "$sort":  {"population":-1 } },
      { "$skip": 1}
    ]
    alist = db.nodes.aggregate(pipeline)
    data = pd.DataFrame(list(alist))
    pprint(data.describe())
    #data["population"] = pd.to_numeric(data["population"],errors="coerce")
    #pprint(data["population"].head())
    #plot_data(data["population"].values)

