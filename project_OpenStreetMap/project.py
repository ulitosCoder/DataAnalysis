#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.cElementTree as ET
import pprint
import re
import codecs
import json
da_file = 'slp-cdvalles-map.osm'
da_file = 'sample.osm'
"""
http://overpass-api.de/api/map?bbox=-101.1700,21.2890,-98.5501,22.9356

-Find the number of tags and types
-k attributes to gte the number of users



Your task is to wrangle the data and transform the shape of the data
into the model we mentioned earlier. The output should be a list of dictionaries
that look like this:

{
"id": "2406124091",
"type: "node",
"visible":"true",
"created": {
          "version":"2",
          "changeset":"17206049",
          "timestamp":"2013-08-03T16:43:42Z",
          "user":"linuxUser16",
          "uid":"1219059"
        },
"pos": [41.9757030, -87.6921867],
"address": {
          "housenumber": "5157",
          "postcode": "60625",
          "street": "North Lincoln Ave"
        },
"amenity": "restaurant",
"cuisine": "mexican",
"name": "La Cabana De Don Luis",
"phone": "1 (773)-271-5176"
}

You have to complete the function 'shape_element'.
We have provided a function that will parse the map file, and call the function with the element
as an argument. You should return a dictionary, containing the shaped data for that element.
We have also provided a way to save the data in a file, so that you could use
mongoimport later on to import the shaped data into MongoDB. 

Note that in this exercise we do not use the 'update street name' procedures
you worked on in the previous exercise. If you are using this code in your final
project, you are strongly encouraged to use the code from previous exercise to 
update the street names before you save them to JSON. 

In particular the following things should be done:
- you should process only 2 types of top level tags: "node" and "way"
- all attributes of "node" and "way" should be turned into regular key/value pairs, except:
    - attributes in the CREATED array should be added under a key "created"
    - attributes for latitude and longitude should be added to a "pos" array,
      for use in geospacial indexing. Make sure the values inside "pos" array are floats
      and not strings. 
- if the second level tag "k" value contains problematic characters, it should be ignored
- if the second level tag "k" value starts with "addr:", it should be added to a dictionary "address"
- if the second level tag "k" value does not start with "addr:", but contains ":", you can
  process it in a way that you feel is best. For example, you might split it into a two-level
  dictionary like with "addr:", or otherwise convert the ":" to create a valid key.
- if there is a second ":" that separates the type/direction of a street,
  the tag should be ignored, for example:

<tag k="addr:housenumber" v="5158"/>
<tag k="addr:street" v="North Lincoln Avenue"/>
<tag k="addr:street:name" v="Lincoln"/>
<tag k="addr:street:prefix" v="North"/>
<tag k="addr:street:type" v="Avenue"/>
<tag k="amenity" v="pharmacy"/>

  should be turned into:

{...
"address": {
    "housenumber": 5158,
    "street": "North Lincoln Avenue"
}
"amenity": "pharmacy",
...
}

- for "way" specifically:

  <nd ref="305896090"/>
  <nd ref="1719825889"/>

should be turned into
"node_refs": ["305896090", "1719825889"]
"""


lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')
non_enslish_chars = re.compile(r'.*[^a-zA-Z\d\s].*',re.UNICODE)

CREATED = [ "version", "changeset", "timestamp", "user", "uid"]

problem_streets = []
problem_pos = []
problem_postcodes = []
problem_non_english = []


def shape_element(element):
  node = {
  "address": {},
  "created": {},
  "pos": [0.0, 0.0],
  "node_refs": []

  }


  if element.tag == "node" or element.tag == "way":
    
    node["type"] = element.tag

    attrs = element.attrib
    

    for atr in attrs:
      
      value = attrs[atr]
      if atr in CREATED:
        
        if 'created' not in node:
          node['created'] = {}
        
        node['created'][atr] = value

      elif atr in ["lat", "lon"]:
        
        if "pos" not in node.keys():
          node["pos"] = [0,0]

        try:
          if atr == "lat":
            node["pos"][0] = float(value)
          else:
            node["pos"][1] = float(value)
        except Exception as e:
          #error converting lat or long
          problem_pos.append( (atr,value) )
        


      else:                
        node[atr] = value

      children = element.findall("tag")
      if len(children):
        for child in children:
          
            chattrs = child.attrib
            k = chattrs['k']
            if k.find("addr:") != -1:
              if "address" not in node:
                print 'adr'
                node["address"] = {}

              kvalue = chattrs['v']

              if k.find("housenumber") != -1:
                node["address"]["housenumber"] = kvalue
              elif re.match(r"addr:street$", k):
                node["address"]["street"] = kvalue
                if problemchars.match(kvalue):
                  problem_streets.append(kvalue)
                elif (non_enslish_chars.match(kvalue) ):
                  problem_non_english.append(kvalue)
              elif re.match(r"addr:postcode$", k):
                try:
                  node["address"]["postcode"] = kvalue
                except Exception as e:
                  node["address"]["postcode"] = 0
                  problem_postcodes.append(kvalue)
                  
                

              

      children = element.findall("nd")
      if len(children):
        
        for child in children:
            chattrs = child.attrib

            if "node_refs" not in node.keys():
              node["node_refs"] = []

            ref = chattrs['ref']

            if ref not in node["node_refs"]:
              node["node_refs"].append( ref )
            

    return node

  else:
    return None


def process_map(file_in, pretty = False):
    # You do not need to change this file
    file_out = "{0}.json".format(file_in)
    data = []
    with codecs.open(file_out, "w") as fo:
        for _, element in ET.iterparse(file_in):
            el = shape_element(element)
            if el:
                data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")
    return data

def test():
    # NOTE: if you are running this code on your computer, with a larger dataset, 
    # call the process_map procedure with pretty=False. The pretty=True option adds 
    # additional spaces to the output, making it significantly larger.
    data = process_map(da_file, False)
    #pprint.pprint(data)
    

    for item in data:
      if item['address'] != {}:
        pprint.pprint( item )
        break
        
    print data[-1]["address"]
    #print data[-1]["node_refs"]
    print data[-1]["type"]
    
    print "problematic names"
    i = 1
    for item in problem_streets:
      print "{}. {}".format(i,item)
      i = i + 1

    print "problematic positions"
    i = 1
    for item in problem_pos:
      print "{}. {}".format(i,item)
      i = i + 1

    print "problematic post codes"
    i = 1
    for item in problem_pos:
      print "{}. {}".format(i,item)
      i = i + 1


    print "names with non english chars"
    i = 1
    for item in problem_non_english:
      print "{}. {}".format(i,item.encode('utf-8'))
      i = i + 1

if __name__ == "__main__":
    test()