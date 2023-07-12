import csv
import time
import arcpy
from setup_project import (SCRATCH_GDB, SSURGO_GDB, PROJECT_GDB,
                           set_env,
                           aprx, mapx)

# Script start time
T0_SCRIPT = time.perf_counter()

# Start time
T0 = time.perf_counter()

# Copy map unit polygons and filter to only WA
set_env(SCRATCH_GDB, True)

arcpy.analysis.Select(SSURGO_GDB+'/MUPOLYGON',
                      'mupolygon',
                      "AREASYMBOL LIKE 'WA%'")
# End time
T1 = time.perf_counter()
print('Copied MUPOLYGON to scratch.gdb and filtered map units to WA')
print(f'    in {round((T1-T0)/60, 2)} minutes.')

# Start time
T0 = time.perf_counter()

# Project to NAD 1983 StatePlane Washington South FIPS 4602
arcpy.management.Project(
    'mupolygon',
    'soils',
    arcpy.SpatialReference(
        'NAD 1983 HARN StatePlane Washington South FIPS 4602 (Meters)'
    )
)
# End time
T1 = time.perf_counter()

print('Projected soils to NAD 1983 StatePlane Washington South FIPS 4602')
print(f'    in {round((T1-T0)/60, 2)} minutes.')

# Start time
T0 = time.perf_counter()

# Copy tables
set_env(SSURGO_GDB, True)

for tbl in arcpy.ListTables():
    tbl_use = ['component', 'chorizon', 'chtexturegrp', 'chtexture', 'Valu1']
    if tbl in tbl_use:
        arcpy.conversion.TableToGeodatabase(tbl, SCRATCH_GDB)

# Join tables to map unit polygons
set_env(SCRATCH_GDB, True)

# soils with component by MUKEY
arcpy.management.JoinField(
    in_data='soils',
    in_field='MUKEY',
    join_table='component',
    join_field='mukey',
    fields='''compname;compkind;majcompflag;taxclname;taxorder;taxsuborder;
    taxgrtgroup;taxsubgrp;cokey;chkey''',
    fm_option='NOT_USE_FM',
    field_mapping=None
)
print('Joined soils with component by MUKEY.')

# soils with chorizon by cokey
arcpy.management.JoinField(
    in_data='soils',
    in_field='cokey',
    join_table='chorizon',
    join_field='cokey',
    fields='chkey',
    fm_option='NOT_USE_FM',
    field_mapping=None
)
print('Joined soils with chorizon by cokey.')

# soils with chtexturegrp by chkey
arcpy.management.JoinField(
    in_data='soils',
    in_field='chkey',
    join_table='chtexturegrp',
    join_field='chkey',
    fields='chtgkey',
    fm_option='NOT_USE_FM',
    field_mapping=None
)
print('Joined soils with chtexturegrp by chkey.')

# soils with chtexture by chtgkey
arcpy.management.JoinField(
    in_data='soils',
    in_field='chtgkey',
    join_table='chtexture',
    join_field='chtgkey',
    fields='texcl; lieutex',
    fm_option='NOT_USE_FM',
    field_mapping=None
)
print('Joined soils with chtexture by chtgkey.')

# soils with Valu1 by MUKEY
arcpy.management.JoinField(
    in_data='soils',
    in_field='MUKEY',
    join_table='Valu1',
    join_field='mukey',
    fields='aws0_30; soc0_30',
    fm_option='NOT_USE_FM',
    field_mapping=None
)
print('Joined soils with Valu1 by MUKEY.')

# Concatenate texcl and lieutex
arcpy.management.CalculateField(
    in_table='soils',
    field='texcl_or_lieu',
    expression='concat(!texcl!, !lieutex!)',
    expression_type='PYTHON3',
    code_block='''
def concat(*args):
    sep = '-'
    return sep.join([i for i in args if i])''',
    field_type='TEXT',
)
print('Concatenated texcl and lieutex into new field: texcl_or_lieu.')

# Generalize texture for easier mapping based on USDA texture triangle
# Create dictionary from texture.csv
with open('C:/ArcGIS/WaSHI_Roadmap/texture.csv', 'r',
          encoding='utf-8-sig') as file:
    reader = csv.reader(file)
    texture_dict = {}
    for row in reader:
        texture_dict[row[0]] = row[1]

# Field calculator to match texture to dictionary
arcpy.management.CalculateField(
    in_table='soils',
    field='gentex',
    expression='createGentex(!texcl_or_lieu!)',
    expression_type='PYTHON3',
    code_block='''def createGentex(texcl_or_lieu):

    if texcl_or_lieu in texture_dict:
        gentex = texture_dict[texcl_or_lieu]
    else: gentex = 'Other'
    return gentex
'''
)
print('Created gentex field.')

# Export soils feature class to project gdb
arcpy.conversion.FeatureClassToGeodatabase(
    Input_Features = 'soils',
    Output_Geodatabase = PROJECT_GDB
)
print('Exported soils to WaSHI Roadmap project gdb.')

# Switch workspace
set_env(PROJECT_GDB, True)

# Calculate acres
arcpy.management.CalculateGeometryAttributes(
    in_features = 'soils',
    geometry_property = 'Acres AREA',
    area_unit = 'ACRES'
)
print('Calculated Acres in soils fc.')

# End time
T1 = time.perf_counter()
print(f'Copied, joined, and exported soils in {round((T1-T0)/60, 2)} minutes.')

# Start time
T0 = time.perf_counter()

# Clip soils to each focus area
for lyr in mapx.listLayers('*_Crops'):
    print(lyr.name)
    name = lyr.name[:lyr.name.index('_Crops')] + '_Soils'
    arcpy.analysis.Clip('soils', lyr, name)
    # Add new clipped fc to map and save project
    mapx.addDataFromPath(PROJECT_GDB + name)
    aprx.save()
    print(f'Clipped soils to {lyr.name}.')

# End time
T1 = time.perf_counter()
print(f'Clipped all focus areas in {round((T1-T0)/60, 2)} minutes.')

# Start time
T0 = time.perf_counter()

# Create new fc for AWS, SOC, and texture
for lyr in mapx.listLayers('*_Soils'):
    # AWS
    name_aws = lyr.name[:lyr.name.index('_Soils')] + '_AWS_0_30cm'
    arcpy.management.CopyFeatures(lyr, name_aws)
    arcpy.management.DeleteField(name_aws, ['aws0_30', 'Acres'], 'KEEP_FIELDS')
    # Add new fc to map and save project
    mapx.addDataFromPath(PROJECT_GDB + name_aws)
    print(f'Created new feature class {name_aws}.')

    # SOC
    name_soc = lyr.name[:lyr.name.index('_Soils')] + '_SOC_0_30cm'
    arcpy.management.CopyFeatures(lyr, name_soc)
    arcpy.management.DeleteField(name_soc, ['soc0_30', 'Acres'], 'KEEP_FIELDS')
    # Add new fc to map and save project
    mapx.addDataFromPath(PROJECT_GDB + name_soc)
    print(f'Created new feature class {name_soc}.')

    # Texture
    name_texture = lyr.name[:lyr.name.index('_Soils')] + '_Texture'
    arcpy.management.CopyFeatures(lyr, name_texture)
    arcpy.management.DeleteField(name_texture,
                                 ['texcl_or_lieu', 'gentex', 'Acres'],
                                 'KEEP_FIELDS')
    # Add new fc to map and save project
    mapx.addDataFromPath(PROJECT_GDB + name_texture)
    print(f'Created new feature class {name_texture}.')
    aprx.save()

# Remove layers that end in '_Soils'
for lyr in mapx.listLayers('*_Soils'):
    mapx.removeLayer(lyr)

# End time
T1 = time.perf_counter()
print('Exported AWS, SOC, and Texture as new fcs')
print(f'    in {round((T1-T0)/60, 2)} minutes.')

# Start time
T0 = time.perf_counter()

# Import texture, AWS, and SOC symbology as group layer
mapx.createGroupLayer('soil_symbology')
SYM_LYR = arcpy.mp.LayerFile(r'C:/ArcGIS/WaSHI_Roadmap/Texture_SOC_AWS.lyrx')
mapx.addLayerToGroup(
    mapx.listLayers('soil_symbology')[0],
    SYM_LYR)

# Apply texture symbology
for lyr in mapx.listLayers('*_Texture'):
    if lyr.isFeatureLayer:
        print(lyr)
        arcpy.management.ApplySymbologyFromLayer(
            lyr,
            SYM_LYR.listLayers('Texture')[0]
            )

# Apply AWS symbology
for lyr in mapx.listLayers('*_AWS*'):
    if lyr.isFeatureLayer:
        print(lyr)
        arcpy.management.ApplySymbologyFromLayer(
            lyr,
            SYM_LYR.listLayers('AWS')[0]
            )

# Apply SOC symbology
for lyr in mapx.listLayers('*_SOC*'):
    if lyr.isFeatureLayer:
        print(lyr)
        arcpy.management.ApplySymbologyFromLayer(
            lyr,
            SYM_LYR.listLayers('SOC')[0]
            )

# Remove symbology lyrs
for lyr in mapx.listLayers('soil_symbology'):
    mapx.removeLayer(lyr)

# End time
T1 = time.perf_counter()
print('Applied symbology to soils layers.')
print(f'in {round((T1-T0)/60, 2)} minutes.')

# Save project
aprx.save()

# Remove lock file
del aprx

# Script end time
T1_SCRIPT = time.perf_counter()
print(f'Script finished in {round((T1_SCRIPT-T0_SCRIPT)/60, 2)} minutes.')
