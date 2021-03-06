#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.cElementTree as ET
import pprint
import re
import codecs
import json


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

abreviations_map = {
  "Av."   : "Avenida",
  "Prol." : "Prolongacion",
  "Blvd." : "Boulevard",
  "Cd."   : "Ciudad",
  "Dr."   : "Doctor",
  "esq."   : "esquina",
  "Esq."   : "esquina",
  "Gral. Blas Escontría" : "General Blas Escontría"
}

names_map = {
  "Vicente C. Salazar"  : "Vicente Calle Salazar",
  "Francisco I. Madero" : "Francisco Ignacio Madero",
  "Pedro J. Méndez"     : "Pedro José Méndez"

}

#Regular expression for abbreviatons
abrev = re.compile(r'[ ]*[a-zA-Z]+\.')

# Regular expression to match lower case names and under score
lower = re.compile(r'^([a-z]|_)*$')

# Regular expression to match lower case names and colon
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')

# Regular expression to find problematic characters
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\.\t\r\n]')

# Regular expression to find non english language characters, excluding 
# whitespace
non_enslish_chars = re.compile(r'.*[^a-zA-Z\d\s].*',re.UNICODE)

CREATED = [ "version", "changeset", "timestamp", "user", "uid"]

# list to store problematic street names
problem_streets = []

# list to store incorrect cordinates
problem_pos = []

# list to store problematic post codes
problem_postcodes = []

# list to store names with non english characters
problem_non_english = []

#list to store names with abreviations
abreviated_names = []

def process_attributes(node, element):

  
  attrs = element.attrib
  for atr in attrs:
    
    value = attrs[atr]
    if atr in CREATED:  
      #get attributes that will be inside the 'created' field
      node["created"][atr] = value
    elif atr in ["lat", "lon"]:
      #get the position coordinates
      
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
      #print "key: {}, value: {}".format(atr, node[atr])


  return node

def process_tag(node, element):
  """
    This function proves the 'tag' children of a node tag, these children 
  provide details of the nodes as name  of the settlement

  """

  children = element.findall("tag")
  
  if len(children) <= 0:
    return node
  

  for child in children:
    
    childs_attrs = child.attrib
    k = childs_attrs['k']
    kvalue = childs_attrs['v']

    if k.find("addr:") != -1:
      #gets the addres details of a node

      if k.find("housenumber") != -1:
        #get house nomber
          node["address"]["housenumber"] = kvalue

      elif re.match(r"addr:street$", k):
        #get street name
        
          
        if problemchars.findall(kvalue):
          #check if name has any problematic characters
          #print "prob char {}".format(kvalue.encode("utf-8"))
          problem_streets.append(kvalue)

        elif (non_enslish_chars.match(kvalue) ):
          #check if the street name contains non english characters
          problem_non_english.append(kvalue)

        if kvalue.find('.') != -1:
          #check if the name has any abreviation for:
          # Avenida, Ciudad, Boulevard, Prolongacion
          abreviated_names.append(kvalue)

          print "abr char {}".format(kvalue.encode("utf-8"))
          #replace abbreviated person names
          if kvalue in abreviations_map:
            kvalue = abreviations_map[kvalue]

          #replace street types abbreviations
          ablist = abrev.findall(kvalue)
          print ablist
          for abr in ablist:
            abr = abr.strip()
            if abr in abreviations_map:
              kvalue = kvalue.replace(abr,abreviations_map[abr])
              
          print "final: {}".format(kvalue.encode("utf-8"))
          node["address"]["street"] = kvalue

      elif re.match(r"addr:postcode$", k):
        try:
          node["address"]["postcode"] = int(kvalue)
        except Exception as e:
          node["address"]["postcode"] = 0
          problem_postcodes.append(kvalue)
          print "bad post: {}".format(kvalue)

          if kvalue == "Lomas 2a":
            node["address"]["postcode"] = 78210

    elif k == "place":
      #gets the type of place of the node
      node["place"] = kvalue

    elif k == "is_in":
      #gets the type of place of the node
      node["is_in"] = kvalue

    elif k == "population":
      #gets the type of place of the node
      node["population"] = int(kvalue)

    elif k == "name":
      #gets the type of place of the node
      node["name"] = kvalue

  return node

def shape_element(element):
  """
  This function get elements from the XML pasting, only process 'node' and
'way' tags. The function populates the dictionary defined below so it can be
imported to a MongoDB NO-SQL database.
  Also the function will try to find problematic post codes, streen names and
coordinates.

  Returns:
   None if the tag is not a node tag or a way tag, otherwsie a populated
   node dictionary
  """

 #node dictionary 
 #individual tags will be used to populate this dictionary so it can be imported
 #to a MongoDB
  node = {
  "address": {},
  "created": {},
  "pos": [0.0, 0.0],
  "node_refs": []
  }


  #only process node and way tags
  if element.tag != "node" and element.tag != "way":
    return None

      
  node["type"] = element.tag

  #process the tag atributes
  node = process_attributes(node, element)

  #process the tag children
  node = process_tag(node, element)

  #process de nd children
  children = element.findall("nd")
  if len(children):
    
    for child in children:
        childs_attrs = child.attrib

        if "node_refs" not in node.keys():
          node["node_refs"] = []

        ref = childs_attrs['ref']

        if ref not in node["node_refs"]:
          node["node_refs"].append( ref )
          

  return node




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
    da_file = 'slp-cdvalles-map.osm'
    #da_file = 'sample.osm'

    data = process_map(da_file, False)
           
    
    print "problematic names"
    i = 1
    for item in problem_streets:
      print "{}. {}".format(i,item.encode('utf-8'))
      i = i + 1

    print "problematic positions"
    i = 1
    for item in problem_pos:
      print "{}. {}".format(i,item)
      i = i + 1

    print "problematic post codes"
    i = 1
    for item in problem_postcodes:
      print "{}. {}".format(i,item.encode('utf-8'))
      i = i + 1

    print "names with non english chars"
    i = 1
    for item in problem_non_english:
      print "{}. {}".format(i,item.encode('utf-8'))
      i = i + 1

    print "names with abreviations"
    i = 1
    for item in abreviated_names:
      print "{}. {}".format(i,item.encode('utf-8'))
      i = i + 1

if __name__ == "__main__":
    test()