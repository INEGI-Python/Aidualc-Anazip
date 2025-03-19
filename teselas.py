import numpy as np
import geopandas as geo
import matplotlib.pyplot as plt

base = geo.read_file("n9_Shape/CPV_n9_CDMX_Datos.shp",columns=["geometry"],rows=10)
print(base.__geo_interface__["features"])
print(base.loc[:"geometry"].__geo_interface__)
