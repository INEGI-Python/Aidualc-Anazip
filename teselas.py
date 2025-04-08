"""
This script generates hexagonal tessellations from input shapefiles and calculates population totals for each hexagon. 
It also creates shapefiles for visualization and generates a web map.
Functions:
----------
shp(_a):
    Saves a GeoDataFrame to a shapefile.
clonar_poligonos(poligono, X, Y, cant):
    Clones a polygon multiple times by translating it along the X and Y axes.
genHexa(rectangulo):
    Generates a hexagon from a rectangular polygon by identifying its centroid and key vertices.
agrupaTeselas(base, centrosIniciales, CRS, **cant):
    Groups tessellations into hexagonal clusters based on initial centers and specified counts for directions.
obtenerPobTot(base, HexagonosDF):
    Calculates the total population for each hexagon by clipping the base data and adjusting for partial overlaps.
teselasIniciales(base, anc, CRS):
    Determines the initial tessellation centers based on the union of geometries and their centroids.
main(input):
    Main function to process the input shapefile, generate tessellations, calculate population totals, and create outputs.
Usage:
------
Run the script with the following command:
    python teselas.py --input <path_to_shapefile>
Arguments:
----------
--input : str
    Path to the input shapefile. The file must have a `.shp` extension.
Notes:
------
- The script assumes the input shapefile contains polygons with population data (`POBTOT`) and geometry.
- Outputs are saved as shapefiles in the `salida` directory.
- A web map is generated using the `WebMAP` function for visualization.
Dependencies:
-------------
- shapely
- geopandas
- matplotlib
- argparse
- pyInegi.generalizacion
"""
from  shapely.affinity import  translate
from pyInegi.generalizacion import WebMAP
from shapely.geometry import Point,Polygon
import geopandas as geo
import matplotlib.pyplot as plt
import argparse

""""
La función shp(_a) toma una lista _a como entrada y guarda un archivo shapefile. Aquí tienes un desglose:

def shp(_a):: Define una función llamada shp que acepta un argumento, _a. Se espera que _a sea una lista o tupla.
_a[0].to_file(f"salida/{_a[1]}.shp"): Esta es la parte principal de la función. Asume que el primer elemento de la lista _a (es decir, _a[0]) es un objeto (probablemente un GeoDataFrame u objeto similar con un método to_file). Llama al método to_file de este objeto para guardar los datos en un archivo shapefile. El nombre del archivo se construye usando un f-string:
"salida/": Especifica que el archivo se guardará en un directorio llamado "salida". Este directorio debe existir en la misma ubicación que el script de Python, de lo contrario, se producirá un error.
_a[1]: Toma el segundo elemento de la lista _a (es decir, _a[1]) y lo usa como el nombre base del archivo.
.shp: Añade la extensión ".shp" al nombre del archivo, que es la extensión estándar para los archivos shapefile.
En resumen, esta función toma una lista donde el primer elemento es un objeto con datos espaciales y el segundo elemento es el nombre deseado para el archivo shapefile. Guarda los datos espaciales en un archivo shapefile en el directorio "salida" con el nombre especificado.
"""

def shp(_a):
    _a[0].to_file(f"salida/{_a[1]}.shp")

    # Esta función toma un polígono como entrada y lo clona 'cant' veces, desplazando cada clon
    # por un factor de X en el eje x e Y en el eje y.
    # Utiliza una comprensión de lista para crear una lista de polígonos traducidos.
    # La función 'translate' se utiliza para desplazar el polígono original.
def clonar_poligonos(poligono,X,Y,cant):
    return  [translate(poligono, xoff=X*i, yoff=Y*i) for i in range(1, cant+1)]

def genHexa(rectangulo):
    """
    Genera un hexágono a partir de un rectángulo (polígono) dado.

    Args:
        rectangulo (Polygon): Un objeto geométrico de tipo Polígono (rectángulo).

    Returns:
        Polygon: Un objeto Polígono que representa un hexágono, o None si no se puede generar.

    Descripción detallada:
    1.  Verifica si la geometría de entrada es un Polígono. Si no lo es, devuelve None.
    2.  Calcula el centroide del rectángulo.
    3.  Calcula la distancia desde el centroide a cada coordenada en el límite exterior del rectángulo.
        Almacena estas distancias junto con las coordenadas en un GeoDataFrame llamado 'distances'.
    4.  Ordena el GeoDataFrame 'distances' por la distancia al centroide.
    5.  Selecciona las 4 coordenadas más alejadas del centroide.
    6.  Elimina las 4 coordenadas más alejadas del conjunto original de coordenadas.
        Las coordenadas restantes se almacenan en 'coordHexa'.
    7.  Crea un Polígono (hexágono) utilizando las coordenadas restantes ('coordHexa') si hay al menos 6 coordenadas.
        Si hay menos de 6 coordenadas, devuelve None.
    """
    if rectangulo.geom_type == "Polygon":    
        centroide = rectangulo.centroid
        distances  = geo.GeoDataFrame( [{"data":centroide.distance(Point(coord)),"geometry":coord}  for coord in rectangulo.exterior.coords])
        ordenados = distances.sort_values(by="data")
        ordenados = ordenados.iloc[-4:].geometry
        coordHexa = distances["geometry"].drop(ordenados.index).values
        return Polygon(coordHexa) if len(coordHexa) >= 6 else None
    return None




    """
    Agrupa teselas (celdas) alrededor de centros iniciales para generar teselaciones hexagonales.

    Args:
        base (GeoDataFrame): GeoDataFrame que contiene las geometrías base para la teselación.
        centrosIniciales (list): Lista de geometrías (puntos) que sirven como centros iniciales para agrupar las teselas.
        CRS (str): Sistema de referencia de coordenadas (CRS) para las geometrías.
        **cant: Argumentos clave-valor que especifican la cantidad de clones a generar en diferentes direcciones (izquierda, derecha, arriba, abajo).

    Returns:
        GeoDataFrame: Un GeoDataFrame que contiene las geometrías de los hexágonos resultantes.

    Descripción detallada:
    1.  Crea una copia temporal del GeoDataFrame base.
    2.  Itera sobre cada centro inicial en 'centrosIniciales'.
    3.  Para cada centro:
        a.  Crea una copia del GeoDataFrame base.
        b.  Calcula la distancia de cada geometría en el GeoDataFrame base al centro actual.
        c.  Ordena las geometrías por distancia al centro.
        d.  Selecciona las 6 geometrías más cercanas (vecinos).
        e.  Disuelve (combina) las geometrías vecinas basándose en el vértice ('vtx').
        f.  Calcula el ancho y el alto del polígono disuelto.
        g.  Aplica un buffer negativo al polígono disuelto.
        h.  Clona el polígono inicial varias veces en las direcciones horizontal y vertical, según los parámetros 'cant'.
        i.  Crea un GeoDataFrame a partir de los polígonos clonados.
        j.  Realiza una unión espacial entre el GeoDataFrame base y el GeoDataFrame de clones.
        k.  Disuelve el resultado de la unión espacial.
        l.  Para cada geometría en el resultado disuelto, genera un hexágono utilizando la función 'genHexa' y lo añade a la lista 'Hexagonos'.
    4.  Crea un GeoDataFrame a partir de la lista de hexágonos generados y devuelve el GeoDataFrame.
    """
def agrupaTeselas(base,centrosIniciales,CRS,**cant):
    _tmp=base.copy()
    Hexagonos=[]
    for cenM in centrosIniciales:
        base = _tmp.copy()
        base["distancia"] = base["geometry"].distance(cenM)
        base_ordenada = base.sort_values(by="distancia")
        vecinos = base_ordenada.head(6)
        inicial = vecinos.dissolve(by="vtx")
        ancho = float(inicial.geometry.bounds.maxx-inicial.geometry.bounds.minx)
        alto = float(inicial.geometry.bounds.maxy-inicial.geometry.bounds.miny)
        inicial = inicial.buffer(ancho/-8)
        #clones=clonar_poligonos(inicial.geometry.iloc[0],ancho-30,20,cant.der)
        #clones.extend(clonar_poligonos(inicial.geometry.iloc[0],-ancho+30,-20,cant.izq))
        clones=clonar_poligonos(inicial.geometry.iloc[0],ancho,0,cant["der"])
        clones.extend(clonar_poligonos(inicial.geometry.iloc[0],-ancho,0,cant["izq"]))
        clones.append(inicial.geometry.iloc[0])
        copia = clones.copy()
        for c in copia:
            #clones.extend(clonar_poligonos(c,-30,(1.333*alto)-20,cant.arr))
            #clones.extend(clonar_poligonos(c,30,(-1.333*alto)+20,cant.aba))
            clones.extend(clonar_poligonos(c,0,alto*1.333,cant["arr"]))
            clones.extend(clonar_poligonos(c,0,-alto*1.333,cant["aba"]))
        clonesDF = geo.GeoDataFrame(geometry=clones,crs=CRS)
        shp([clonesDF,"clonesDF"])
        join=base.sjoin(clonesDF,how="inner",lsuffix="_caller",rsuffix="_other")         
        join=join.dissolve(by="index__other",aggfunc="sum",method="unary")
        shp([join,"join"])    
        for j in join.geometry:
            Hexagonos.append(genHexa(j))
    return geo.GeoDataFrame(geometry=Hexagonos,crs=CRS)
    

    """
    Calcula la población total para cada hexágono en HexagonosDF basándose en la intersección con la capa base.

    Args:
        base (GeoDataFrame): GeoDataFrame que contiene la información de población por área.
        HexagonosDF (GeoDataFrame): GeoDataFrame que contiene la geometría de los hexágonos.

    Returns:
        None: La función modifica el GeoDataFrame HexagonosDF directamente, añadiendo la columna 'POBTOT'.

    Proceso:
    1.  Crea una copia de la capa base para evitar modificaciones directas.
    2.  Calcula el área de la base (asumiendo que todas las geometrías en 'base' tienen la misma área).
    3.  Inicializa la columna 'POBTOT' en HexagonosDF con valor 0.0 para cada hexágono.
    4.  Itera sobre cada hexágono en HexagonosDF:
        a.  Realiza un clip (intersección) entre la capa base y el hexágono actual.
        b.  Calcula el área de cada polígono resultante del clip.
        c.  Inicializa la variable 'pob_total' a 0.
        d.  Itera sobre cada polígono resultante del clip:
            i.  Verifica si el polígono es de tipo "Polygon".
            ii. Comprueba si el área del polígono está dentro de un rango del 95% al 105% del área base original.
                Si está dentro del rango, asume que es un polígono completo y añade su población directamente a 'pob_total'.
                Si no está dentro del rango, asume que es un polígono parcial y añade la mitad de su población a 'pob_total'.
        e.  Asigna el valor calculado de 'pob_total' a la columna 'POBTOT' del hexágono actual en HexagonosDF.
    5.  Guarda HexagonosDF y baseClip en formato shapefile usando la función 'shp'.
    """
def obtenerPobTot(base,HexagonosDF):
    baseClip = base.copy()
    areaBase = base.iloc[0].geometry.area
    HexagonosDF["POBTOT"] = 0.0
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


def teselasIniciales(base,anc,CRS):
    """
    Calcula dos puntos iniciales para la generación de teselas basados en una geometría base.

    Args:
        base: Un objeto GeoSeries que representa la geometría base para la teselación.
        anc: Un valor numérico que representa un ancho de referencia.
        CRS: Un sistema de coordenadas de referencia (CRS).

    Returns:
        Una lista que contiene dos objetos Point:
        - El centroide de la unión de las teselas base seleccionadas.
        - Un punto desplazado desde el centroide, usado como referencia para la creación de nuevas teselas.
    """
    # Calcula el centroide de la unión de todas las geometrías en 'base'.
    unirB = base.union_all().centroid
    # Crea dos puntos: el centroide calculado y otro punto desplazado 'anc' unidades hacia la derecha.
    pts=[unirB,Point(unirB.x+anc,unirB.y)]
    # Crea un GeoSeries a partir de estos puntos, asignándole el CRS especificado.
    centroB = geo.GeoSeries(data=pts,crs=CRS)
    # Identifica las teselas en 'base' que intersectan con cada uno de los puntos en 'centroB'.
    # Obtiene los índices de estas teselas y los almacena en una lista 'b'.
    # Se resta 1 a cada índice.
    b = [int(base[base.intersects(centroB.iloc[i])].index[0]-1) for i in range(2)]
    # Une las geometrías de las teselas seleccionadas (indexadas por 'b') en una sola geometría.
    union = base.iloc[b].union_all()
    # Crea un GeoDataFrame a partir de la geometría unida, asignándole el CRS especificado.
    uDF = geo.GeoDataFrame(geometry=[union],crs=CRS)
    # Calcula el ancho del rectángulo delimitador (bounding box) de la geometría unida.
    anchoUDF = float(uDF.geometry.bounds.maxx-uDF.geometry.bounds.minx)
    # Calcula el alto del rectángulo delimitador de la geometría unida.
    altoUDF = float(uDF.geometry.bounds.maxy-uDF.geometry.bounds.miny)
    # Devuelve una lista conteniendo:
    # - El centroide de la geometría unida.
    # - Un nuevo punto, desplazado desde el centroide.
    #   El desplazamiento es de la mitad del ancho hacia la izquierda y el doble del alto hacia arriba.
    return  [union.centroid,Point(union.centroid.x-(anchoUDF*0.5),union.centroid.y+(altoUDF*2))]
    


def main(input):
    # Lee un archivo geográfico (shapefile, GeoJSON, etc.) especificado por 'input' utilizando la biblioteca 'geopandas' (importada como 'geo').
    # Solo se cargan las columnas 'POBTOT' (población total) y 'geometry' (geometría de las entidades).
    base = geo.read_file(input,columns=["POBTOT","geometry"])
    # Cambia el sistema de coordenadas (CRS) del GeoDataFrame 'base' al EPSG 6372. Esto asegura que todas las geometrías estén en el mismo sistema de referencia para cálculos espaciales.
    base = base.to_crs(6372)
    # Crea una nueva columna llamada 'ID' en el GeoDataFrame 'base' y asigna el índice de cada fila a esta columna.
    base["ID"] = base.index
    # Crea una nueva columna llamada 'vtx' en el GeoDataFrame 'base' y asigna el número de vértices de cada geometría a esta columna.
    base["vtx"]=base.geometry.count_coordinates()
    # Calcula el ancho de cada geometría (la diferencia entre la coordenada máxima y mínima en el eje x) y lo asigna a la columna 'ancho'.
    base["ancho"]=base.geometry.bounds.maxx-base.geometry.bounds.minx
    # Calcula el ancho promedio de todas las geometrías en 'base'.
    anchoProm = sum(base["ancho"])/base.count().ID
    # Obtiene la representación en formato de cadena del sistema de coordenadas de referencia (CRS) del GeoDataFrame 'base'.
    CRS = base.crs.to_string()
    # Guarda el GeoDataFrame 'base' como un archivo shapefile llamado "base.shp" en la carpeta "salida".
    shp([base,"base"])
    #######################################################################
    #                                                                                                                                          #
    #######################################################################
    # Llama a la función 'teselasIniciales' para calcular los centros iniciales para la generación de teselas (hexágonos).
    # Utiliza el GeoDataFrame 'base', el ancho promedio calculado ('anchoProm') y el CRS como argumentos.
    centrosIniciales = teselasIniciales(base,anchoProm,CRS)
    # Llama a la función 'agrupaTeselas' para agrupar las teselas alrededor de los centros iniciales.
    # Utiliza el GeoDataFrame 'base', los centros iniciales, el CRS y parámetros adicionales para controlar la cantidad de teselas en cada dirección (derecha, izquierda, arriba, abajo).
    HexagonosDF = agrupaTeselas(base,centrosIniciales,CRS,der=23,izq=23,arr=15,aba=15)
    # Llama a la función 'obtenerPobTot' para calcular la población total dentro de cada hexágono en 'HexagonosDF'.
    # Utiliza el GeoDataFrame 'base' y 'HexagonosDF' como argumentos.
    obtenerPobTot(base,HexagonosDF)
    # Crea un nuevo GeoDataFrame llamado 'centrosDF' a partir de los centros iniciales calculados.
    # Asigna el CRS correspondiente. Este GeoDataFrame se crea solo con el fin de crear un shapefile
    centrosDF = geo.GeoDataFrame(geometry=centrosIniciales,crs=CRS)
    # Guarda el GeoDataFrame 'centrosDF' como un archivo shapefile llamado "centroDF.shp" en la carpeta "salida".
    shp([centrosDF,"centroDF"])

    # Llama a la función 'WebMAP' para crear un mapa web interactivo utilizando los shapefiles generados.
    # Define las capas a incluir en el mapa, sus tipos de geometría, nombres y estilos visuales.
    # El parámetro 'web=1' indica que el mapa debe mostrarse en el navegador web.
    WebMAP(datos=["salida/baseClip.shp","salida/HexagonosDF.shp","salida/centroDF.shp"],tipos=["POLYGON","POLYGON","POINT"],names=["Clip","Hexagonos","Centroide"],estilo=[dict(fillColor="#0000FF",color="black"),dict(fillColor="red",color="black"),dict(stroke=True,fillColor="#0000FF",color="#000000",fillOpacity=0.5,weight=1)],web=1)




if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Genera hexágonos a partir de teselas obtenidad de las cartas topograficas.")
    parser.add_argument("--input", type=str, required=True, help="Ruta del shapefile de entrada.")
    args = parser.parse_args()
    if not args.input.endswith(".shp"):
        raise ValueError("El archivo de entrada debe ser un shapefile (.shp)")

    main(args.input)







    ##########################################################################
    #          codigo en caso que las teselas tengan una inclinacion con respecto al ecuardor        #
    ##########################################################################
    #                                                                                                                                                #
    # base = base[base["vtx"] == 5]                                                                                                #
    # base.dropna(inplace=True)                                                                                                    # 
    # buff = base.buffer(0)
    # buffer=geo.GeoDataFrame(geometry=buff.geometry,crs=base.crs)
    # buffer["ID"] = base["ID"]
    # buffer["POBTOT"] = base["POBTOT"]
    # buffer["vtx"] = base["vtx"]
    # shp([buffer,"buffer"])
    # del base
    # base=buffer.copy()
    # base.sindex
    # cant= int(base.count().ID)
    # base["ID"] = [i for i in range(1,cant+1)]
    # base["ID"] = base["ID"].astype(int)
    # base["_id"] = base["ID"]
    # base.set_index("ID",inplace=True)
    # base.sort_index(inplace=True)
    # base["alto"]=base.geometry.bounds.maxy-base.geometry.bounds.miny
    #
    ################################################################
