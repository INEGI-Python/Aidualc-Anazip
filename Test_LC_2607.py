import arcpy
import os
##import RecorrerCruzado2Campos
espaciodetrabajo_1=r"D:\A2023\RetomaLineaCosta\Test_ScriptLC_20Jul23\Geodatas\Capa_Prueba_14Sep.gdb\Datos"
fcPuntos_1="fcPuntos_CF1708_1"
arcpy.env.workspace =espaciodetrabajo_1
workspace=arcpy.env.workspace
arcpy.env.overwriteOutput = True
inicio = "ID"
fin= "NEAR_FID"
field= ['OBJECTID','NEAR_FID']
ptPuertos=[]
mi_lista = []
suma =1
resta = 1
arcpy.MakeFeatureLayer_management(fcPuntos_1, "fcPuntos_1_Layer")




datos = arcpy.SearchCursor(fcPuntos_1)
dato_field = inicio
for row in datos:
    #Get ID of datos
    datos_ID = row.getValue(dato_field)
##    print datos_ID

    # Create search cursor for looping through the trees
    datos_NF = arcpy.SearchCursor(fcPuntos_1)
    dato_field2 = fin

    for row2 in datos_NF:
        
        # Get FID of tree
        Near_FID = row2.getValue(dato_field2)
##        print Near_FID
            

##        
        if Near_FID == datos_ID:
     #       print "Near es: "+ str(Near_FID)
            mi_lista.append(Near_FID)
repeticiones = {}

for n in mi_lista:
    if mi_lista.count(n) != 1:
        if n in repeticiones :
            repeticiones[n] += 2
        else:
            repeticiones[n] = 0
print(repeticiones)
v = repeticiones.keys()
print v
 
for i in v:
    print i
    
    query= "ID = {}". format(i) +" or "+ " NEAR_FID= {}". format(i)
    #query = inicio + " = " + str( i) +" or "+ fin + " = " + str( i)
    print query
    
    arcpy.SelectLayerByAttribute_management("fcPuntos_1_Layer", "ADD_TO_SELECTION", query )
    
arcpy.CopyFeatures_management("fcPuntos_1_Layer","fcPuntos_CF1708_2")
##if arcpy.Exists("fcPuntos_CF1708_1"):
##    arcpy.MakeFeatureLayer_management(fcPuntos_1, "fcPuntos_1_Lyr")
##    arcpy.SelectLayerByLocation_management("fcPuntos_1_Lyr", "INTERSECT","fcPuntos_CF1708_1","", "NEW_SELECTION", "NOT_INVERT")
##    arcpy.DeleteFeatures_management("fcPuntos_1_Lyr")

##RecorrerCruzado2Campos.my_function(workspace,inicio,fin,field,mi_lista)

print "Termine"
    
