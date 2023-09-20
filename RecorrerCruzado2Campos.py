import arcpy

espaciodetrabajo_1=r"D:\A2023\RetomaLineaCosta\Test_ScriptLC_20Jul23\Geodatas\Capa_Prueba_14Sep.gdb\Datos"
fcPuntos_1="AngulosFinales"
arcpy.env.workspace =espaciodetrabajo_1
workspace=arcpy.env.workspace
arcpy.env.overwriteOutput = True
fc = fcPuntos_1
inicio = "OBJECTID"
fin= "NEAR_FID"
field1_list = [row[0] for row in arcpy.da.SearchCursor(fcPuntos_1, ["OBJECTID"])]
field2_list = [row[0] for row in arcpy.da.SearchCursor(fcPuntos_1, ["NEAR_FID"])]
lista=[]
index = 0
counter = 1 

##def my_function():
##    print("Hello from a function")
arcpy.MakeFeatureLayer_management(fc, "fc_Lyr")
#arcpy.CalculateField_management(in_table="AngulosFinales", field="ID", expression="!OBJECTID!", expression_type="PYTHON_9.3", code_block="")


# Create update cursor for feature class
datos = arcpy.SearchCursor(fcPuntos_1)
dato_field = inicio

lyrfile = fcPuntos_1
result = arcpy.GetCount_management(lyrfile)
print('{} has {} records'.format(lyrfile, result[0])) ##Te devuelve el numero de elementos que contiene el feature class
for row in datos:
    
    
    #Get ID of datos
    datos_ID = row.getValue(dato_field)
    print datos_ID
    with arcpy.da.UpdateCursor(fc, ["ID"]) as updater:
        #for row in updater:
        for row in updater:
           
            if index<=len(field1_list)-6:# el -4 se va a cambiar dependiedo de cuantos renglones quieras comparar,se incremento a 6
                        
                
                n0 = field1_list[index]
                print "n0 " + str(n0)
                n1 = field2_list[index]
                print "n1 " + str(n1)
                n2 = field1_list[index+1]
                print "n2 " + str(n2)
                n3 = field2_list[index+1] 
                print "n3 " + str(n3)
                n4 = field1_list[index+2]
                print "n4 " + str(n4)
                n5 = field2_list[index+2]
                print "n5 " + str(n5)
                n6 = field1_list[index+3]
                print "n6 " + str(n6)
                n7 = field2_list[index+3]
                print "n7 " + str(n7)
                n8 = field1_list[index+4]
                print "n8 " + str(n8)
                n9 = field2_list[index+4]
                print "n9 " + str(n9)

                if n6==n1 and n4==n3 and n4==n7:
                    print "Son iguales and n6==n1 and n4==n3 and n4==n7  "  + str(n6)+ " "+ str(n4) 
                    lista.append(n6)
                    lista.append(n4)
                           
                if n0==n7 and n6==n1 and n2==n5 and n4==n3:
                    print "Son iguales n0==n7 and n6==n1 and n2==n5 and n4==n3 "  + str(n0)+ " "+ str(n2)+" "+ str(n4)+" "+ str(n6)
                    lista.append(n0)
                    lista.append(n2)
                    lista.append(n4)
                    lista.append(n6)

                if n0!=n7 and n6==n1 and n2==n5 and n4==n3:
                    print "Son iguales n0!=n7 and n6!=n1 and n2==n5 and n4==n3 "  + str(n0)+ " "+ str(n2)+" "+ str(n4)+" "+ str(n6)
                    lista.append(n0)
                    lista.append(n2)
                    lista.append(n4)
                    lista.append(n6)

                if n0==n7 and n6!=n1 and n2==n5 and n4==n3:

                    print "Son iguales n0==n7 and n6!=n1 and n2==n5 and n4==n3 "  + str(n0)+ " "+ str(n2)+" "+ str(n4)+" "+ str(n6)
                    lista.append(n0)
                    lista.append(n2)
                    lista.append(n4)
                    lista.append(n6)
                else:
                    
                    #print "no son iguales"  + str(n1) +" != "+ str(n2) 
                    counter+=1
                updater.updateRow([counter])
                index+=1

            else:
                updater.updateRow([counter])
                break
print lista

for i in lista:
    print i
    query= "OBJECTID = {}". format(i) 

    arcpy.SelectLayerByAttribute_management("fc_Lyr", "ADD_TO_SELECTION", query )
arcpy.CopyFeatures_management("fc_Lyr", "datos_cruzados04_Sep")

print "Termine"


##my_function()
