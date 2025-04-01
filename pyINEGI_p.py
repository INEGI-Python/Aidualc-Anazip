
from pyInegi.generalizacion import reducePuntos as rP
from datetime import datetime as dt
import geopandas as gpd






def porMientras():
	rP.ReducePuntos(gdb="LocalidadesPoligonoCentroide/LocalidadesPoligonoCentroide.shp",feat="_",camp="Jerarquia:1,geografico:1,num_hab:0".split(","),dist=5000,ver=1)



def shape2geojson(shapefile_path):
	gdf = gpd.read_file(shapefile_path)
	CRS = gdf.crs.to_string()
	gdf=gdf.to_crs(CRS)
	geojson_path = shapefile_path.replace("entrada","salida").replace("shp","geojson")
	gdf.to_file(geojson_path, driver="GeoJSON")
	return dt.today()




for a  in  ["entrada/PaisExtranjeroOK.shp", "entrada/EstadosPagina.shp", "entrada/NombresPuntoAbreviados.shp"]:
	print(shape2geojson(a))



