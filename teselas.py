import numpy as np
import geopandas as geo
import matplotlib.pyplot as plt
from matplotlib import colormaps
import random
import  shapely as sh
from pyInegi.generalizacion import WebMAP


Linea= sh.LineString(v)

color = list(colormaps)[random.randint(0,len(list(colormaps))-1)]

base = geo.read_file("CPV_9_cdmex/CPV_9_cdmex.shp",columns=["ID","POBTOT","geometry"])
CRS = base.crs.to_string()
enumerar = base.index
base["ordenada"]=base.geometry.centroid.y
base["absisa"]=base.geometry.centroid.x
base["vtx"]=base.geometry.count_coordinates()
cant=enumerar[-1]+1
base.set_index(["ordenada","absisa"],  inplace=True)
base.sort_index(inplace=True,ascending=[False,True])
base["ID"]=enumerar
base.reset_index(drop=True,inplace=True)
base.set_index("ID",inplace=True)
base.where(base["vtx"]==5,inplace=True)
base.dropna(inplace=True)
base.reset_index() 
cont = int((base.loc[ : ,"vtx"].count())/2)

tmp = base.iloc[cont:cont+2]["geometry"].values
XXX  = tmp[0]+tmp[1]
print(XXX)
lineaDF = geo.GeoDataFrame(geometry=[sh.LineString(XXX)], crs=CRS )
posDF = base.iloc[cont:cont+2]["geometry"].values
posDF = geo.GeoDataFrame(geometry=posDF.unary_union,crs=CRS)
centro = posDF.centroid
centroDF = geo.GeoDataFrame(geometry=[centro],crs=CRS)
vecinos = geo.sjoin_nearest(centroDF,base,how="inner", max_distance=0.002)

# for i in range(1,cont+1):
# 	base.iloc[i-1]["ID"]=i
# 	for c in base.iloc[i-1].geometry.__geo_interface__["coordinates"][0]:
# 		print(c,end=" , ")
	

centroDF.to_file("centroDF.shp")
lineaDF.to_file("posDF.shp")

#print(res.iloc[0])

#print(res)
WebMAP(datos=["centroDF.shp","posDF.shp"],tipos=["POINT","LINESTRING"],names=["Centroide","Teselas CDMX"],color=["#FF0000","#00FF00"],web=1,rows=None)
