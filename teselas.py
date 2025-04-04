import numpy as np
from  shapely.affinity import  translate
from pyInegi.generalizacion import WebMAP
from shapely.geometry import Point,Polygon,MultiPolygon,LineString
from shapely.ops import split
import geopandas as geo
import matplotlib.pyplot as plt
import os

def shp(_a):
    eval(f"{_a}.to_file('salida/{_a}.shp')")

def clonar_poligonos(**_d):
    return  [translate(_d["poligono"], xoff=_d["X"]*i, yoff=_d["Y"]*i) for i in range(1, _d["cant"]+1)]
    
def genHexa(rectangulo):
    if rectangulo.geom_type == "Polygon":    
        centroide = rectangulo.centroid
        distances  = geo.GeoDataFrame( [{"data":centroide.distance(Point(coord)),"geometry":coord}  for coord in rectangulo.exterior.coords])
        ordenados = distances.sort_values(by="data")
        ordenados = ordenados.iloc[-4:].geometry
        coordHexa = distances["geometry"].drop(ordenados.index).values
        return Polygon(coordHexa) if len(coordHexa) >= 6 else None

def separarGeom(v):
    print(v.geometry.geom_type)
    return v if v.geometry.geom_type == "Polygon" else None

    # if v.geom_type == "Polygon":
    #     return Polygon([v.exterior.coords[i] for i in range(len(v.exterior.coords)) if i%2==0])
    # else:
    #     return None


base = geo.read_file("CPV_9_cdmex/CPV_9_cdmex.shp",columns=["ID","POBTOT","geometry"])
base = base.to_crs(6372)
base["vtx"]=base.geometry.count_coordinates()
base = base[base["vtx"] == 5]
base.dropna(inplace=True)
buff = base.buffer(0)
buffer=geo.GeoDataFrame(geometry=buff.geometry,crs=base.crs)
buffer["ID"] = base["ID"]
buffer["POBTOT"] = base["POBTOT"]
buffer["vtx"] = base["vtx"]
shp("buffer")
del base
base=buffer.copy()
base.sindex
cant= int(base.count().ID)
base["ID"] = [i for i in range(1,cant+1)]
base["ID"] = base["ID"].astype(int)
base["_id"] = base["ID"]
base.set_index("ID",inplace=True)
base.sort_index(inplace=True)
CRS = base.crs.to_string()
base["ancho"]=base.geometry.bounds.maxx-base.geometry.bounds.minx
base["alto"]=base.geometry.bounds.maxy-base.geometry.bounds.miny
base["x"] = base.centroid.x
base["y"] = base.centroid.y
cen=base.centroid.geometry
centroides = geo.GeoDataFrame(data=[{"_id":i} for i in range(cen.count())],geometry=cen,crs=CRS)
shp("base")
unirB = base.union_all().centroid
pts=[unirB,Point(unirB.x+488,unirB.y)]
centroB = geo.GeoSeries(data=pts,crs=CRS)
b = [int(base[base.intersects(centroB.iloc[i])].index[0]-1) for i in range(2)]
print(b)
union = base.iloc[b].union_all()
uDF = geo.GeoDataFrame(geometry=[union],crs=CRS)
anchoUDF = float(uDF.geometry.bounds.maxx-uDF.geometry.bounds.minx)
altoUDF = float(uDF.geometry.bounds.maxy-uDF.geometry.bounds.miny)
centroMain = [union.centroid,Point(union.centroid.x-(anchoUDF*0.51),union.centroid.y+(altoUDF*1.98))]
centroDF = geo.GeoDataFrame(geometry=centroMain,crs=CRS)
shp("centroDF")

_tmp=base.copy()
Hexagonos=[]
for cenM in centroMain:
    base = _tmp.copy()
    base["distancia"] = base["geometry"].distance(cenM)
    base_ordenada = base.sort_values(by="distancia")
    vecinos = base_ordenada.head(6)
    inicial = vecinos.dissolve(by="vtx")
    ancho = float(inicial.geometry.bounds.maxx-inicial.geometry.bounds.minx)
    alto = float(inicial.geometry.bounds.maxy-inicial.geometry.bounds.miny)
    inicial = inicial.buffer(ancho/-8)
    clones=clonar_poligonos(poligono=inicial.geometry.iloc[0],cant=23,X=ancho-30,Y=20)
    clones.extend(clonar_poligonos(poligono=inicial.geometry.iloc[0],cant=23,X=-ancho+30,Y=-20))
    clones.append(inicial.geometry.iloc[0])
    copia = clones.copy()
    for c in copia:
        clones.extend(clonar_poligonos(poligono=c,cant=15,X=-30,Y=(1.333*alto)-20))
        clones.extend(clonar_poligonos(poligono=c,cant=15,X=30,Y=(-1.333*alto)+20))
    clonesDF = geo.GeoDataFrame(geometry=clones,crs=CRS)
    join=base.sjoin(clonesDF,how="inner",lsuffix="_caller",rsuffix="_other")         
    join=join.dissolve(by="index__other",aggfunc="sum",method="unary")
    shp("join")
    
    for j in join.geometry:
        Hexagonos.append(genHexa(j))
HexagonosDF = geo.GeoDataFrame(geometry=Hexagonos,crs=CRS)
#hexa_Lineas = geo.GeoDataFrame(geometry=HexagonosDF.boundary,crs=CRS)
lineas = []
for hexa in HexagonosDF.geometry:
    if hexa is not None and hexa.geom_type == "Polygon":
        coords = list(hexa.exterior.coords)
        for i in range(len(coords) - 1):
            lineas.append(LineString([coords[i], coords[i + 1]]))
hexa_Lineas = geo.GeoDataFrame(geometry=lineas, crs=CRS)
shp("hexa_Lineas")
shp("HexagonosDF")


baseClip = base.copy()
for i,v in baseClip.iterrows():
    cortar = [v.geometry]
    salida =[]
    j=0
    print(f"Poligono_{i}")
    while len(cortar) > 0:
        poly = cortar.pop()
        print(f"Geometria_{j}")
        lines = hexa_Lineas.loc[(hexa_Lineas.geometry.contains(poly)) & (~hexa_Lineas.geometry.touches(poly))]
        print(lines)
        if len(lines.index) > 0:
            cortar_poly = split(poly,hexa_Lineas.geometry.iloc[0])
            cortar += [p for p in cortar_poly.geoms]
        else:
            salida.append(poly)
        j+=1
        print(len(cortar))
        if len(cortar) == 0:
            break
     
    baseClip.iloc[i].geometry = MultiPolygon(salida)




shp("baseClip")


WebMAP(datos=["salida/baseClip.shp","salida/hexa_Lineas.shp","salida/HexagonosDF.shp","salida/centroDF.shp"],tipos=["POLYGON","LINE","POLYGON","POINT"],names=["Clip","Overlay","Hexagonos","Centroide"],estilo=[dict(fillColor="#0000FF",color="black"),dict(fillColor="purple",color="red"),dict(fillColor="red",color="black"),dict(stroke=True,fillColor="#0000FF",color="#000000",fillOpacity=0.5,weight=1)],web=1)
