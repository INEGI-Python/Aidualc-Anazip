import numpy as np
import geopandas as geo
import  shapely as sh
from pyInegi.generalizacion import WebMAP
from shapely.geometry import Point,Polygon,LineString
import os

def clonar_hexagono(**dire):
    shifted_hexagons = []
    for i in range(1, dire["cant"]+1):
        x_offset = dire["X"]*i
        y_offset =  dire["Y"]*i
        shifted_hexagon = sh.affinity.translate(dire["hexagono"], xoff=x_offset, yoff=y_offset)
        shifted_hexagons.append(shifted_hexagon)
    return shifted_hexagons

def generate_hexagon(polygon,ancho,alto):
    _cant=31
    centroid = polygon.centroid
    distances = [centroid.distance(Point(coord)) for coord in polygon.exterior.coords]
    distances.sort()
    coordHexa = [coord for coord in polygon.exterior.coords if centroid.distance(Point(coord)) not in distances[-4:]]
    print(coordHexa)
    HexaBase = Polygon(coordHexa)
    tmp=[HexaBase]    
    tmp.extend(clonar_hexagono(hexagono=HexaBase,cant=_cant,X=ancho,Y=float(2*alto)))
    tmp.extend(clonar_hexagono(hexagono=HexaBase,cant=_cant,X=-ancho,Y=float(-2*alto)))
    Hexagonos=[t for t in tmp]
    for h in tmp:
        Hexagonos.extend(clonar_hexagono(hexagono=h,cant=_cant,X=float(2*ancho),Y=0))
        Hexagonos.extend(clonar_hexagono(hexagono=h,cant=_cant,X=float(-2*ancho),Y=0))
    return Hexagonos


dirAct = os.getcwd()
print(dirAct)
#os.chdir(f"{dirAct}/Aidualc-Anazip")
base = geo.read_file("CPV_9_cdmex/CPV_9_cdmex.shp",columns=["ID","POBTOT","geometry"])
base["vtx"]=base.geometry.count_coordinates()
ancho = float(base.geometry.iloc[0].bounds[2] - base.geometry.iloc[0].bounds[0])
alto = float(base.geometry.iloc[0].bounds[3] - base.geometry.iloc[0].bounds[1])   
base.to_crs(epsg=4326,inplace=True)
CRS = base.crs.to_string()
print(CRS)
unirB = base.union_all().centroid
centros = [unirB,sh.affinity.translate(unirB, xoff=ancho, yoff=0)]
centroB = geo.GeoSeries(data=centros,crs=CRS)
tmp = [base[base.intersects(centroB.iloc[i])].index[0] for i in range(2)]
union =base.iloc[tmp].union_all()

unionDF = geo.GeoDataFrame(geometry=[union],crs=CRS)
centroDF = geo.GeoDataFrame(geometry=[union.centroid],crs=CRS)

centro = centroDF["geometry"].iloc[0]
base["distancia"] = base["geometry"].distance(centro)
base.to_crs(epsg=4326,inplace=True)
base_ordenada = base.sort_values(by="distancia")
vecinos = base_ordenada.head(6)
inicial = vecinos.dissolve(by="vtx")
#inicial.set_precision(16)
total_hexas = generate_hexagon(inicial.geometry.iloc[0],ancho,alto)
teselas_hexagon = geo.GeoDataFrame(geometry=total_hexas,crs=CRS)
miClip = teselas_hexagon.boundary.clip(base)
miClipDF = geo.GeoDataFrame(geometry=[miClip.iloc[543]],crs=CRS)
vecinoClip=vecinos.clip(miClipDF)

#lineasDF = geo.GeoDataFrame(geometry=miClip.union_all() ,crs="EPSG:4326")
#partidos = geo.overlay(base,lineasDF , how='intersection')

miClip.to_file("salida/miClip.shp")

vecinoClip.to_file("salida/vecinosClip.shp")
teselas_hexagon.to_file("salida/teselas_hexagon.shp")
vecinos.to_file("salida/vecinosDF.shp")
unionDF.to_file("salida/unionDF.shp")
centroDF.to_file("salida/centroDF.shp")


#print(res)
WebMAP(datos=["salida/vecinosClip.shp","salida/vecinos_hexagon.shp","salida/centroDF.shp","salida/miClip.shp"],tipos=["POLYGON","POLYGON","POINT","POLYGON"],names=["Vecinos","hexagono","Centroide","ClipBase"],estilo=[dict(fillColor="#FF0000",color="black"),dict(stroke=True,fillColor="#0000FF",color="#000000",fillOpacity=0.5,weight=1),dict(fillColor="#00FF00",color="white"),dict(fillColor="purple",color="red")],web=1)
