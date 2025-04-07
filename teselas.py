from  shapely.affinity import  translate
from pyInegi.generalizacion import WebMAP
from shapely.geometry import Point,Polygon
import geopandas as geo
import matplotlib.pyplot as plt
import argparse

def shp(_a):
    _a[0].to_file(f"salida/{_a[1]}.shp")

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
    return None


def agrupaTeselas(base,centroMain):
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
        #clones=clonar_poligonos(poligono=inicial.geometry.iloc[0],cant=23,X=ancho-30,Y=20)
        #clones.extend(clonar_poligonos(poligono=inicial.geometry.iloc[0],cant=23,X=-ancho+30,Y=-20))
        clones=clonar_poligonos(poligono=inicial.geometry.iloc[0],cant=23,X=ancho,Y=0)
        clones.extend(clonar_poligonos(poligono=inicial.geometry.iloc[0],cant=23,X=-ancho,Y=0))
        clones.append(inicial.geometry.iloc[0])
        copia = clones.copy()
        for c in copia:
            #clones.extend(clonar_poligonos(poligono=c,cant=15,X=-30,Y=(1.333*alto)-20))
            #clones.extend(clonar_poligonos(poligono=c,cant=15,X=30,Y=(-1.333*alto)+20))
            clones.extend(clonar_poligonos(poligono=c,cant=15,X=0,Y=alto*1.333))
            clones.extend(clonar_poligonos(poligono=c,cant=15,X=0,Y=-alto*1.333))
        clonesDF = geo.GeoDataFrame(geometry=clones,crs=CRS)
        join=base.sjoin(clonesDF,how="inner",lsuffix="_caller",rsuffix="_other")         
        join=join.dissolve(by="index__other",aggfunc="sum",method="unary")
        shp([join,"join"])    
        for j in join.geometry:
            Hexagonos.append(genHexa(j))
    return geo.GeoDataFrame(geometry=Hexagonos,crs=CRS)
    

def obtenerPobTot(base,HexagonosDF):
    baseClip = base.copy()
    areaBase = base.iloc[0].geometry.area
    HexagonosDF["POBTOT"] = 0
    for i,v in HexagonosDF.iterrows():
        if v.geometry is not None:
            clip = baseClip.clip(v.geometry)
            clip["area"] = clip.geometry.area
            pob_total = 0 
            for j,c in clip.iterrows():
                if c.geometry.geom_type == "Polygon":
                    if (areaBase*0.95) < c.geometry.area < (areaBase*1.05):
                        pob_total += c["POBTOT"]
                    else:
                        pob_total += c["POBTOT"]*0.5
            HexagonosDF.loc[i,"POBTOT"] = pob_total    
    shp([HexagonosDF,"HexagonosDF"])
    shp([baseClip,"baseClip"])



def main(input):
    base = geo.read_file(input,columns=["POBTOT","geometry"])
    base = base.to_crs(6372)
    base["ID"] = base.index+1
    base["vtx"]=base.geometry.count_coordinates()
    base = base[base["vtx"] == 5]
    base.dropna(inplace=True)
    buff = base.buffer(0)
    buffer=geo.GeoDataFrame(geometry=buff.geometry,crs=base.crs)
    buffer["ID"] = base["ID"]
    buffer["POBTOT"] = base["POBTOT"]
    buffer["vtx"] = base["vtx"]
    shp([buffer,"buffer"])
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
    shp([base,"base"])
    unirB = base.union_all().centroid
    pts=[unirB,Point(unirB.x+500,unirB.y)]
    centroB = geo.GeoSeries(data=pts,crs=CRS)
    b = [int(base[base.intersects(centroB.iloc[i])].index[0]-1) for i in range(2)]
    print(b)
    union = base.iloc[b].union_all()
    uDF = geo.GeoDataFrame(geometry=[union],crs=CRS)
    anchoUDF = float(uDF.geometry.bounds.maxx-uDF.geometry.bounds.minx)
    altoUDF = float(uDF.geometry.bounds.maxy-uDF.geometry.bounds.miny)
    centroMain = [union.centroid,Point(union.centroid.x-(anchoUDF*0.51),union.centroid.y+(altoUDF*1.98))]
    centroDF = geo.GeoDataFrame(geometry=centroMain,crs=CRS)
    shp([centroDF,"centroDF"])

    HexagonosDF = agrupaTeselas(base,centroMain)
    obtenerPobTot(base,HexagonosDF)

    WebMAP(datos=["salida/baseClip.shp","salida/HexagonosDF.shp","salida/centroDF.shp"],tipos=["POLYGON","POLYGON","POINT"],names=["Clip","Hexagonos","Centroide"],estilo=[dict(fillColor="#0000FF",color="black"),dict(fillColor="red",color="black"),dict(stroke=True,fillColor="#0000FF",color="#000000",fillOpacity=0.5,weight=1)],web=1)




if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Genera hexágonos a partir de teselas obtenidad de las cartas topograficas.")
    parser.add_argument("--input", type=str, required=True, help="Ruta del shapefile de entrada.")
    args = parser.parse_args()
    if not args.input.endswith(".shp"):
        raise ValueError("El archivo de entrada debe ser un shapefile (.shp)")
    main(args.input)