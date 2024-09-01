#!/usr/bin/env python
import codecs
import csv
import sqlite3
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import geodatasets

try:
    # Python 3
    from urllib.request import urlopen
except ImportError:
    # Python 2
    from urllib2 import urlopen

# The URL to the collection (as comma-separated values).
collection_url = "http://geoserver-portal.aodn.org.au/geoserver/wfs?typeName=imos:aatams_biologging_shearwater_data&SERVICE=WFS&outputFormat=csv&REQUEST=GetFeature&VERSION=1.0.0&userId=Guest"

# Fetch data...
response = urlopen(collection_url)

# Iterate on data...
csvfile = csv.DictReader(codecs.iterdecode(response, 'utf-8'))
#for row in csvfile:
#    print(row)

def setup_db():
    try:
        con = sqlite3.connect('Shearwater.db') # trying out putting the DB in memory to reduce clean-up
        cur = con.cursor()
        cur.execute("""
            CREATE TABLE Shearwater (
            AnimalID int,
            Date date,
            Time time,
            Long float,
            Lat float
            );
        """)
        res = cur.execute("SELECT name FROM sqlite_master")
        print(res.fetchone())
    except sqlite3.Error as e:
        print(e)

def load_data(cur, data):
    for row in data:
        datetime = row['timestamp'].split("T")
        #print(datetime)
        #print(type(row['animal_id']))
        sqlinsert = "INSERT INTO Shearwater VALUES(?,?,?,?,?)"
        cur.execute(sqlinsert, (row['animal_id'], datetime[0], datetime[1], row['longitude'], row['latitude']))

if __name__ == '__main__':
    setup_db()
    con = sqlite3.connect('Shearwater.db')
    cur = con.cursor()
    load_data(cur, csvfile)
    uniqueBirdIDs = cur.execute("""
        SELECT DISTINCT AnimalID
        FROM Shearwater;
    """).fetchall()
    uniqueBirdIDs = [ x[0] for x in uniqueBirdIDs ]
    print(uniqueBirdIDs)
    query = "SELECT * FROM Shearwater;"
    df = pd.read_sql(query, con)
    geometry = [Point(xy) for xy in zip(df['Long'], df['Lat'])]
    geo_df = gpd.GeoDataFrame(df, crs="EPSG:4326", geometry=geometry)
    world = gpd.read_file(geodatasets.data.naturalearth.land['url'])
    colours = cm.rainbow(np.linspace(0,1), len(uniqueBirdIDs))
    
    for i, c in zip(uniqueBirdIDs, colours):
        geo_df[geo_df['AnimalID'] == i].plot(ax=world.plot(figsize=(10,6)),
                                                markersize=20,
                                                color = c,
                                                marker='o',
                                                label=i)
