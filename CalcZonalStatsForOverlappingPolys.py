# Calculate Zonal Statistics for Overlapping Zones/Plygons
# Originally from: http://support.esri.com/technical-article/000011385
#
# Purpose:
# When using polygon features as the input zones in the Zonal Statistics as Table tool, the polygons cannot overlap. 
# Using Python, the tool's limitations can be overcome by iteratively processing each feature and then recombine the tables when done.
# In this version of the script, we are only returning the MAJORITY raster value in the polygon, this option can be changed on line 33.
#
# VARIABLES:
#       ws = PATH TO THE WORKSPACE 
#       DBF_dir = THE FILENAME (LAST PORTION) OF THE FILE CREATED FOR EACH POLYGON
#       fc = FEATURE CLASS CONTAING ZONES - SHOULD BE IN A FILE GEODATABASE
#       zoneField = FIELD NAME IN YOUR fc THAT CONTAINS THE ZONE ATTRIBUTIONS
#       raster = PATH AND NAME OF YOUR RASTER LAYER
#       zstat_table = LOCATION AND NAME OF THE FINAL TABLE
# 
# Modified by Dorn Moore - International Crane Foundation
# 2016-08-25


import arcpy, os, sys, string
from arcpy import env
from arcpy.sa import *
arcpy.CheckOutExtension("spatial") #checkout the spatial analyst extension

def CreateDirectory(DBF_dir):
    if not os.path.exists(DBF_dir):
        os.mkdir(DBF_dir)
        print "created directory {0}".format(DBF_dir)
        
def ZonalStasAsTable(fc,DBF_dir,raster,zoneField):
    
    for row in arcpy.SearchCursor(fc):
        lyr = "Zone_{0}_lyr".format(row.OBJECTID)
        tempTable = DBF_dir + os.sep + "zone_{0}.dbf".format(row.OBJECTID)
        out_layer=arcpy.MakeFeatureLayer_management(fc, lyr, "\"OBJECTID\" = {0}".format(row.OBJECTID))
        print "Creating layer {0}".format(lyr)
        
        #Removed the line below and made the feature layer about out_layer - this fixed issues.
        #out_layer = DBF_dir + os.sep + lyr + ".lyr"
        #arcpy.SaveToLayerFile_management(lyr, out_layer, "ABSOLUTE")
        ##print "Saved layer file"

        #Parameters for the ZonalStatisticsAsTable command.
        arcpy.gp.ZonalStatisticsAsTable_sa(out_layer, zoneField, raster, tempTable, "DATA", "ALL")
        print "Populating zonal stats for {0}".format(lyr)
    del row, lyr
        
def MergeTables(DBF_dir,zstat_table):
    arcpy.env.workspace = DBF_dir
    tableList = arcpy.ListTables()      
    arcpy.Merge_management(tableList,zstat_table)
    print "Merged tables. Final zonalstat table {0} created. Located at {1}".format(zstat_table,DBF_dir)
    del tableList

if __name__ == "__main__":

	# YOU NEED TO CHANGE THESE VARIABLES
    # Define the varables - change these to match your needs.
    ws = "c:\\Your\\WorkSpace\\Path"  #Workspace path 
    DBF_dir = ws + os.sep + "DBFile" #PATH for output dbf file
    # The feature class being the polygons you are analyzing should be in a FILE GEODATABASE
    fc = "c:\\Your\\Path\\to\\your\FileGeoDatabase.gdb\\Polygons" #Feature class containing zones
    zoneField = "YourZoneField" #Field to pull zones from for analysis
    raster = "c:\\Path\\and\\file\\for\\your\\raster" #Raster layer for analysis
    zstat_table = DBF_dir + os.sep + "Zonalstat.dbf" #output DBF file name
    
    # Ok, time to do the work!
    CreateDirectory(DBF_dir)
    ZonalStasAsTable(fc,DBF_dir,raster,zoneField)
    MergeTables(DBF_dir,zstat_table)