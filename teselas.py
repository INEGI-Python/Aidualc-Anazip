import numpy as np
import geopandas as geo
from matplotlib import colormaps
import random
import  shapely as sh
from pyInegi.generalizacion import WebMAP
from shapely.geometry import Point
import os

def clonar_hexagono(**dire):
    shifted_hexagons = []
    for i in range(1, dire["cant"]+1):
        x_offset = dire["X"]*i
        y_offset =  dire["Y"]*i
        shifted_hexagon = sh.affinity.translate(dire["hexagono"], xoff=x_offset, yoff=y_offset)
        shifted_hexagons.append(shifted_hexagon)
    return shifted_hexagons

def generate_hexagon(polygon):
    _cant=31
    centroid = polygon.centroid
    distances = [centroid.distance(Point(coord)) for coord in polygon.exterior.coords]
    distances.sort()
    coordHexa = [coord for coord in polygon.exterior.coords if centroid.distance(Point(coord)) not in distances[-4:]]
    HexaBase = sh.Polygon(coordHexa)
    tmp=[HexaBase]    
    tmp.extend(clonar_hexagono(hexagono=HexaBase,cant=_cant,X=ancho,Y=2*alto))
    tmp.extend(clonar_hexagono(hexagono=HexaBase,cant=_cant,X=-ancho,Y=-2*alto))
    Hexagonos=[t for t in tmp]
    for h in tmp:
        Hexagonos.extend(clonar_hexagono(hexagono=h,cant=_cant,X=2*ancho,Y=0))
        Hexagonos.extend(clonar_hexagono(hexagono=h,cant=_cant,X=-2*ancho,Y=0))
    return Hexagonos

def ordenarGeo():
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


dirAct = os.getcwd()
print(dirAct)
os.chdir(f"{dirAct}/Aidualc-Anazip")
base = geo.read_file("CPV_9_cdmex/CPV_9_cdmex.shp",columns=["ID","POBTOT","geometry"])
base["vtx"]=base.geometry.count_coordinates()
ancho = base.geometry.iloc[0].bounds[2] - base.geometry.iloc[0].bounds[0]
alto = base.geometry.iloc[0].bounds[3] - base.geometry.iloc[0].bounds[1]   
CRS = base.crs.to_string()
print(CRS)
unirB = base.union_all().centroid
centros = [unirB,sh.affinity.translate(unirB, xoff=ancho, yoff=0)]
centroB = geo.GeoSeries(data=centros,crs="EPSG:4326")
tmp = [base[base.intersects(centroB.iloc[i])].index[0] for i in range(2)]
inicio=base.iloc[tmp]
union = inicio.union_all()
unionDF = geo.GeoDataFrame(geometry=[union], crs="EPSG:4326")
centroDF = geo.GeoDataFrame(geometry=[union.centroid], crs="EPSG:4326")
centro = centroDF["geometry"].iloc[0]
base["distancia"] = base["geometry"].distance(centro)
base_ordenada = base.sort_values(by="distancia")
vecinos = base_ordenada.head(6)
inicial=vecinos.dissolve(by="vtx")
hexas = generate_hexagon(inicial.geometry.iloc[0])
vecinos_hexagon = geo.GeoDataFrame(geometry=hexas, crs="EPSG:4326")


vecinos_hexagon.to_file("salida/vecinos_hexagon.shp")
vecinos.to_file("salida/vecinosDF.shp")
unionDF.to_file("salida/unionDF.shp")
centroDF.to_file("salida/centroDF.shp")


#print(res)
WebMAP(datos=["salida/vecinosDF.shp","salida/vecinos_hexagon.shp","salida/centroDF.shp"],tipos=["POLYGON","POLYGON","POINT"],names=["Vecinos","hexagono","Centroide"],estilo=[dict(fillColor="#FF0000",color="black"),dict(stroke=True,fillColor="#0000FF",color="#000000",fillOpacity=0.5,weight=1),dict(fillColor="#00FF00",color="white")],web=1)
