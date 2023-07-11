import csv
import time
import arcpy

# Set ArcGIS Pro Project
aprx = arcpy.mp.ArcGISProject("C:/ArcGIS/WaSHI_Roadmap/WaSHI_Roadmap.aprx")

# Check if project is read only
if aprx.isReadOnly:
    print("Project is read only.")
    # Exit if read only
    sys.exit()

# Create map variable
mapx = aprx.listMaps("WaSHI_Roadmap")[0]

# Set gdb paths
SSURGO = "C:/ArcGIS/gSSURGO_WA/gSSURGO_WA.gdb/"
PROJECT = "C:/ArcGIS/WaSHI_Roadmap/WaSHI_Roadmap.gdb/"
SCRATCH = "C:/ArcGIS/WaSHI_Roadmap/scratch.gdb/"

# # Create scratch gdb for intermediate data
# if arcpy.Exists(SCRATCH) is True:
#     print("scratch.gdb already exists.")
# else:
#     arcpy.management.CreateFileGDB("C:/ArcGIS/WaSHI_Roadmap/",
#                                    "scratch.gdb")
#     print("Created scratch.gdb.")

# # Set overwrite to True
# arcpy.env.overwriteOutput = True

# # Start time
# T0 = time.perf_counter()

# # Copy map unit polygons and filter to only WA
# arcpy.env.workspace = SCRATCH
# arcpy.analysis.Select(SSURGO+"/MUPOLYGON",
#                       "mupolygon",
#                       "AREASYMBOL LIKE 'WA%'")
# # End time
# T1 = time.perf_counter()
# print("Copied MUPOLYGON to scratch.gdb and filtered map units to WA")
# print(f"in {round((T1-T0)/60, 2)} minutes.")

# # Start time
# T0 = time.perf_counter()

# # Project to NAD 1983 StatePlane Washington South FIPS 4602
# arcpy.management.Project(
#     'mupolygon',
#     'soils',
#     arcpy.SpatialReference(
#         "NAD 1983 HARN StatePlane Washington South FIPS 4602 (Meters)"
#     )
# )
# # End time
# T1 = time.perf_counter()

# print("Projected soils to NAD 1983 StatePlane Washington South FIPS 4602")
# print(f"in {round((T1-T0)/60, 2)} minutes.")

# # Start time
# T0 = time.perf_counter()

# # Copy tables
# arcpy.env.workspace = SSURGO

# for tbl in arcpy.ListTables():
#     tbl_use = ["component", "chorizon", "chtexturegrp", "chtexture", "Valu1"]
#     if tbl in tbl_use:
#         arcpy.conversion.TableToGeodatabase(tbl, SCRATCH)

# # Join tables to map unit polygons
# arcpy.env.workspace = SCRATCH

# # soils with component by MUKEY
# arcpy.management.JoinField(
#     in_data="soils",
#     in_field="MUKEY",
#     join_table="component",
#     join_field="mukey",
#     fields="""compname;compkind;majcompflag;taxclname;taxorder;taxsuborder;
#     taxgrtgroup;taxsubgrp;cokey;chkey""",
#     fm_option="NOT_USE_FM",
#     field_mapping=None
# )
# print("Joined soils with component by MUKEY.")

# # soils with chorizon by cokey
# arcpy.management.JoinField(
#     in_data="soils",
#     in_field="cokey",
#     join_table="chorizon",
#     join_field="cokey",
#     fields="chkey",
#     fm_option="NOT_USE_FM",
#     field_mapping=None
# )
# print("Joined soils with chorizon by cokey.")

# # soils with chtexturegrp by chkey
# arcpy.management.JoinField(
#     in_data="soils",
#     in_field="chkey",
#     join_table="chtexturegrp",
#     join_field="chkey",
#     fields="chtgkey",
#     fm_option="NOT_USE_FM",
#     field_mapping=None
# )
# print("Joined soils with chtexturegrp by chkey.")

# # soils with chtexture by chtgkey
# arcpy.management.JoinField(
#     in_data="soils",
#     in_field="chtgkey",
#     join_table="chtexture",
#     join_field="chtgkey",
#     fields="texcl; lieutex",
#     fm_option="NOT_USE_FM",
#     field_mapping=None
# )
# print("Joined soils with chtexture by chtgkey.")

# # soils with Valu1 by MUKEY
# arcpy.management.JoinField(
#     in_data="soils",
#     in_field="MUKEY",
#     join_table="Valu1",
#     join_field="mukey",
#     fields="aws0_30; soc0_30",
#     fm_option="NOT_USE_FM",
#     field_mapping=None
# )
# print("Joined soils with Valu1 by MUKEY.")

# # Concatenate texcl and lieutex
# arcpy.management.CalculateField(
#     in_table="soils",
#     field="texcl_or_lieu",
#     expression="concat(!texcl!, !lieutex!)",
#     expression_type="PYTHON3",
#     code_block="""
# def concat(*args):
#     sep = "-"
#     return sep.join([i for i in args if i])""",
#     field_type="TEXT",
# )
# print("Concatenated texcl and lieutex into new field: texcl_or_lieu.")

# # Generalize texture for easier mapping based on USDA texture triangle
# # Create dictionary from texture.csv
# with open("C:/ArcGIS/WaSHI_Roadmap/texture.csv", "r",
#           encoding="utf-8-sig") as file:
#     reader = csv.reader(file)
#     texture_dict = {}
#     for row in reader:
#         texture_dict[row[0]] = row[1]

# # Field calculator to match texture to dictionary
# arcpy.management.CalculateField(
#     in_table="soils",
#     field="gentex",
#     expression="createGentex(!texcl_or_lieu!)",
#     expression_type="PYTHON3",
#     code_block="""def createGentex(texcl_or_lieu):

#     if texcl_or_lieu in texture_dict:
#         gentex = texture_dict[texcl_or_lieu]
#     else: gentex = "Other"
#     return gentex
# """
# )
# print("Created gentex field.")

# # Export soils feature class to project gdb
# arcpy.conversion.FeatureClassToGeodatabase(
#     Input_Features = "soils",
#     Output_Geodatabase = PROJECT
# )
# print("Exported soils to WaSHI Roadmap project gdb.")

# # Switch workspace
# arcpy.env.workspace = PROJECT
# arcpy.env.overwriteOutput = True

# # Calculate acres
# arcpy.management.CalculateGeometryAttributes(
#     in_features = "soils",
#     geometry_property = "Acres AREA",
#     area_unit = "ACRES"
# )
# print("Calculated Acres in soils fc.")

# # End time
# T1 = time.perf_counter()
# print("Copied, joined, and exported soils in")
# print(f"{round((T1-T0)/60, 2)} minutes.")

arcpy.env.workspace = PROJECT
arcpy.env.overwriteOutput = True

# Start time
T0 = time.perf_counter()

# Clip soils to each focus area
for lyr in mapx.listLayers("*_Crop*"):
    name = lyr.name[:lyr.name.index("_Crop")] + "_Soils"
    arcpy.analysis.Clip("soils", lyr, name)
    # Add new clipped fc to map and save project
    mapx.addDataFromPath(PROJECT + name)
    aprx.save()
    print(f"Clipped soils to {lyr.name}.")

# End time
T1 = time.perf_counter()
print(f"Clipped all focus areas in {round((T1-T0)/60, 2)} minutes.")

# Start time
T0 = time.perf_counter()

# Create new fc for AWS, SOC, and texture
for lyr in mapx.listLayers("*_Soils"):
    # AWS
    name_aws = lyr.name[:lyr.name.index("_Soils")] + "_AWS_0_30cm"
    arcpy.management.CopyFeatures(lyr, name_aws)
    arcpy.management.DeleteField(name_aws, ["aws0_30", "Acres"], "KEEP_FIELDS")
    # Add new fc to map and save project
    mapx.addDataFromPath(PROJECT + name_aws)
    print(f"Created new feature class {name_aws}.")

    # SOC
    name_soc = lyr.name[:lyr.name.index("_Soils")] + "_SOC_0_30cm"
    arcpy.management.CopyFeatures(lyr, name_soc)
    arcpy.management.DeleteField(name_soc, ["soc0_30", "Acres"], "KEEP_FIELDS")
    # Add new fc to map and save project
    mapx.addDataFromPath(PROJECT + name_soc)
    print(f"Created new feature class {name_soc}.")

    # Texture
    name_texture = lyr.name[:lyr.name.index("_Soils")] + "_Texture"
    arcpy.management.CopyFeatures(lyr, name_texture)
    arcpy.management.DeleteField(name_texture,
                                 ["texcl_or_lieu", "gentex", "Acres"],
                                 "KEEP_FIELDS")
    # Add new fc to map and save project
    mapx.addDataFromPath(PROJECT + name_texture)
    print(f"Created new feature class {name_texture}.")
    aprx.save()

# Remove layers that end in "_Soils"
for lyr in mapx.listLayers("*_Soils"):
    mapx.removeLayer(lyr)

# End time
T1 = time.perf_counter()
print("Exported AWS, SOC, and Texture as new fcs")
print(f"in {round((T1-T0)/60, 2)} minutes.")

# Remove lock file
del aprx

# Next step is to apply symbology, publish rest service, 
# generate maps and dashboards!
