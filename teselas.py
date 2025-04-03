import numpy as np
from  shapely.affinity import  translate
from pyInegi.generalizacion import WebMAP
from shapely.geometry import Point,Polygon
import geopandas as geo
import matplotlib.pyplot as plt
import os

def shp(_a):
    eval(f"{_a}.to_file('salida/{_a}.shp')")

def clonar_hexagono(**_d):
    return  [translate(_d["hexagono"], xoff=_d["X"]*i, yoff=_d["Y"]*i) for i in range(1, _d["cant"]+1)]
    
def genHexa(rectangulo):
    centroide = rectangulo.centroid
    distances  = geo.GeoDataFrame( [{"data":centroide.distance(Point(coord)),"geometry":coord}  for coord in rectangulo.exterior.coords])
    coordHexa = [coord for coord in rectangulo.exterior.coords if centroide.distance(Point(coord)) not in distances[-4:]]
    return  Polygon(coordHexa)


    _cant=31
    tmp=[HexaBase]    
    tmp.extend(clonar_hexagono(hexagono=HexaBase,cant=_cant,X=ancho,Y=float(2*alto)))
    tmp.extend(clonar_hexagono(hexagono=HexaBase,cant=_cant,X=-ancho,Y=float(-2*alto)))
    Hexagonos=[t for t in tmp]
    for h in tmp:
        Hexagonos.extend(clonar_hexagono(hexagono=h,cant=_cant,X=float(2*ancho),Y=0))
        Hexagonos.extend(clonar_hexagono(hexagono=h,cant=_cant,X=float(-2*ancho),Y=0))
    return Hexagonos


base = geo.read_file("CPV_9_cdmex/CPV_9_cdmex.shp",columns=["ID","POBTOT","geometry"])
base = base.to_crs(6372)
base["vtx"]=base.geometry.count_coordinates()
base = base[base["vtx"] == 5]
cant= int(base.count().ID)
base["ID"]=base.index
base.sort_index(inplace=True)
CRS = base.crs.to_string()
base["ancho"]=base.geometry.bounds.maxx-base.geometry.bounds.minx
base["alto"]=base.geometry.bounds.maxy-base.geometry.bounds.miny
base["x"] = base.centroid.x
base["y"] = base.centroid.y
cenTmp= [Point(*p.xy) for p in base.centroid.geometry]
centroides = geo.GeoDataFrame(geometry=cenTmp,crs=CRS)
shp("centroides")
base.plot()

base["grupo"] = (base.index // 6) + 1

shp("base")
exas=genHexa(Polygon(([0,0],[0,2],[0,4],[0,6],[2,6],[4,6],[4,4],[4,2],[4,0],[2,0])))
hexagonos = geo.GeoDataFrame(geometry=[exas],crs=CRS)
hexagonos.plot()
plt.plot(hexagonos)
plt.show()
#exit()















#base.set_index("ancho",inplace=True)
#base.sort_index(inplace=True)
unirB = base.union_all().centroid
pts=[unirB,Point(unirB.x+488,unirB.y)]
centroB = geo.GeoSeries(data=pts,crs=CRS)
shp("centroB")
b = [int(base[base.intersects(centroB.iloc[0])].index[0])]
b.append(int(base[base.intersects(centroB.iloc[1])].index[0]))
print(b)
centros = base[base["ID"] == bó[0]]
centros.append(base[base["ID"] == b[1]])
print(centros)

shp("centros")
tmp = [int(base[base.intersects(centroB.iloc[i])].index[0]) for i in range(2)]

ezqui = base[base["ID"] == b[0]].geometry.bounds
ancho = float(ezqui[2] - ezqui[0])
alto = float(ezqui[3] - ezqui[1])   

union = centros.union_all()
print(union)
unionDF = geo.GeoDataFrame(geometry=[union],crs=CRS)
shp("unionDF")

centroDF = geo.GeoDataFrame(geometry=[union.centroid],crs=CRS)
shp("centroDF")
centro = centroDF["geometry"].iloc[0]
base["distancia"] = base["geometry"].distance(centro)
base_ordenada = base.sort_values(by="distancia")
vecinos = base_ordenada.head(6)
inicial = vecinos.dissolve(by="vtx")
shp("vecinos")
shp("inicial")
total_hexas = genHexa(inicial.geometry.iloc[0])   
teselas_hexagon = geo.GeoDataFrame(geometry=total_hexas,crs=CRS)
teselas_hexagon.sindex
join_teselas = teselas_hexagon.sjoin(base ,how="inner", lsuffix='_caller', rsuffix='_other')
print(join_teselas)

TESELAS=join_teselas.loc[:,["ID","POBTOT","geometry"]]
print(TESELAS)

TESELAS.to_file("salida/TESELAS.shp")
teselas_hexagon.to_file("salida/teselas_hexagon.shp")
vecinos.to_file("salida/vecinosDF.shp")
unionDF.to_file("salida/unionDF.shp")
centroDF.to_file("salida/centroDF.shp")

WebMAP(datos=["salida/TESELAS.shp","salida/teselas_hexagon.shp","salida/centroDF.shp","salida/miClip.shp"],tipos=["POLYGON","POLYGON","POINT","POLYGON"],names=["Vecinos","hexagono","Centroide","ClipBase"],estilo=[dict(fillColor="#FF0000",color="black"),dict(stroke=True,fillColor="#0000FF",color="#000000",fillOpacity=0.5,weight=1),dict(fillColor="#00FF00",color="white"),dict(fillColor="purple",color="red")],web=1)
