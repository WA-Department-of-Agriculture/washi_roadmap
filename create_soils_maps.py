import csv
import time

import arcpy

from setup_project import (PROJECT_GDB, SCRATCH_GDB, SSURGO_GDB,
                           set_env, aprx, mapx)

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

# Project to NAD 1983 HARN StatePlane Washington South FIPS 4602 (Meters)
arcpy.management.Project(
    'mupolygon',
    'soils',
    arcpy.SpatialReference(
        'NAD 1983 HARN StatePlane Washington South FIPS 4602 (Meters)'
    )
)
# End time
T1 = time.perf_counter()

print('Projected soils to NAD 1983 HARN StatePlane Washington South')
print(f'    FIPS 4602 (Meters) in {round((T1-T0)/60, 2)} minutes.')

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

# Replace blanks in texcl_or_lieu with 'No Data'
arcpy.management.CalculateField(
    in_table='soils',
    field='texcl_or_lieu',
    expression='replaceBlank(!texcl_or_lieu!)',
    expression_type='PYTHON3',
    code_block='''
def replaceBlank(texcl_or_lieu):
    if texcl_or_lieu == '':
        return 'No Data'
    else: return texcl_or_lieu''',
    field_type='TEXT',
)
print("Replaced blanks in texcl_or_lieu with 'No Data'.")

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

# Set field aliases
field_dict = {
    'texcl_or_lieu': 'Texture or Surface Description',
    'gentex': 'Textural Group',
    'aws0_30': 'AWS (mL per 0-30 cm)',
    'soc0_30': 'SOC (g per 0-30 cm)'
}

for field in arcpy.ListFields('soils'):
    if field.name in field_dict:
        arcpy.management.AlterField('soils', field.name,
                                    new_field_alias = field_dict[field.name])
        print(f'Updated alias for {field.name}')

# Export soils feature class to project gdb
arcpy.conversion.FeatureClassToGeodatabase(
    Input_Features = 'soils',
    Output_Geodatabase = PROJECT_GDB
)
print('Exported soils to WaSHI Roadmap project gdb.')

# Add new soils fc to map
mapx.addDataFromPath(PROJECT_GDB + 'soils')

# Save
aprx.save()
del aprx

# Script end time
T1_SCRIPT = time.perf_counter()
print(f'Script finished in {round((T1_SCRIPT-T0_SCRIPT)/60, 2)} minutes.')

print('Now run create_soils_subsets.py.')
