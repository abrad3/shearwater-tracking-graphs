#!/usr/bin/env python
import codecs
import csv
import sqlite3
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import matplotlib.pyplot as plt
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
    query = "SELECT * FROM Shearwater;"


    #street_map = gpd.read_file('shapefiles-antarctica/Expert-defined-Bioregions/Bioregions_V2_PS.shp')
    df = pd.read_sql(query, con)
    geometry = [Point(xy) for xy in zip(df['Long'], df['Lat'])]
    geo_df = gpd.GeoDataFrame(df, crs="EPSG:4326", geometry=geometry)
    #street_map.plot(ax=ax, alpha=0.4, color='grey')
    world = gpd.read_file(geodatasets.data.naturalearth.land['url'])
    geo_df[geo_df['AnimalID'] == "15-2012"].plot(ax=world.plot(figsize=(10,6)),
                                                markersize=20,
                                                color='blue',
                                                marker='o',
                                                label='15-2012')
    plt.show()
