import time

import arcpy
from apply_soil_symbology import apply_soil_symbology
from setup_project import PROJECT_GDB, aprx, mapx

# Script start time
T0_SCRIPT = time.perf_counter()

# Start time
T0 = time.perf_counter()

# Clip soils to each focus area
for lyr in mapx.listLayers('*_Crops'):
    name = lyr.name[:lyr.name.index('_Crops')] + '_Soils'
    arcpy.analysis.Clip('soils', lyr, name)
    print(f'Clipped soils to {lyr.name}.')

# Calculate acres for each soils layer
def calculate_acres(feature_class):
    '''Calculate acres for each soil layer.

    Keyword arguments:
    feature_class -- the name of the fc to calculate ares.
    '''
    arcpy.management.CalculateField(
        in_table = feature_class,
        field = 'Acres',
        expression = '!Shape.area@acres!',
        expression_type = 'PYTHON3',
        code_block = '',
        field_type = 'FLOAT',
        enforce_domains = 'NO_ENFORCE_DOMAINS'
)

# Pause to give time for locks to release
time.sleep(3)

for fc in arcpy.ListFeatureClasses('*_Soils'):
    calculate_acres(fc)
    # Add new clipped fc to map and save project
    mapx.addDataFromPath(PROJECT_GDB + fc)
    aprx.save()
    print(f'Calculated acres for {fc}.')

# End time
T1 = time.perf_counter()
print('Clipped all focus areas and calculated acres in')
print(f'    {round((T1-T0)/60, 2)} minutes.')

# Start time
T0 = time.perf_counter()

# Create new fc for AWS, SOC, and texture
for lyr in mapx.listLayers('*_Soils'):
    # AWS
    name_aws = lyr.name[:lyr.name.index('_Soils')] + '_AWS'
    arcpy.management.CopyFeatures(lyr, name_aws)
    arcpy.management.DeleteField(name_aws, ['aws0_30', 'Acres'], 'KEEP_FIELDS')
    # Add new fc to map and save project
    mapx.addDataFromPath(PROJECT_GDB + name_aws)
    print(f'Created new feature class {name_aws}.')

    # SOC
    name_soc = lyr.name[:lyr.name.index('_Soils')] + '_SOC'
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
for lyr in mapx.listLayers('*Soils'):
    mapx.removeLayer(lyr)

for fc in arcpy.ListFeatureClasses('*Soils'):
    arcpy.management.Delete(fc)

# End time
T1 = time.perf_counter()
print('Exported AWS, SOC, and Texture as new fcs')
print(f'    in {round((T1-T0)/60, 2)} minutes.')

# Start time
T0 = time.perf_counter()

apply_soil_symbology()

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

print('Run set_field_properties script in ArcGIS Pro Python Window.')
# It doesn't work in VSCode...

print('Check that symbology included popup formatting!')
# Otherwise manually configure popups according to configure_popups.html.

print('Then run group_layers.py.')
