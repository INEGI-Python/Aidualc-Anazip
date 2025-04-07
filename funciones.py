import geopandas as gpd
import numpy as np

def actualizar_pobtot(gdf):
    """
    Actualiza el valor del campo POBTOT en un GeoDataFrame.

    Args:
        gdf: GeoDataFrame con un campo llamado POBTOT.

    Returns:
        GeoDataFrame con el campo POBTOT actualizado.
    """
    gdf_copy = gdf.copy()
    
    # Genera valores aleatorios entre 1 y 7777 para las filas donde POBTOT > 0
    random_values = np.random.randint(1, 7778, size=len(gdf_copy[gdf_copy['POBTOT'] > 0]))
    
    # Asigna los valores aleatorios al campo POBTOT
    gdf_copy.loc[gdf_copy['POBTOT'] > 0, 'POBTOT'] = random_values

    return gdf_copy

base = actualizar_pobtot(gpd.read_file("CPV_9_cdmex/div500.shp"))
print(base.head())
base.to_file("CPV_9_cdmex/div500_pobtot.shp", driver="ESRI Shapefile")