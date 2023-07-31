import arcpy
from setup_project import aprx, LAYER_FOLDER

# Import texture, AWS, and SOC symbology as group layer
def apply_soil_symbology():
    ''' Apply symbology for AWS, SOC, and texture layers.
    '''
    aws_lyr = LAYER_FOLDER + 'AWS.lyrx'
    soc_lyr = LAYER_FOLDER + 'SOC.lyrx'
    texture_lyr = LAYER_FOLDER + 'Texture.lyrx'

# Apply texture symbology
    for lyr in mapx.listLayers('*Texture'):
        if lyr.isFeatureLayer:
            arcpy.management.ApplySymbologyFromLayer(
            lyr,
            texture_lyr,
            symbology_fields="VALUE_FIELD gentex gentex"
            )

# Apply AWS symbology
    for lyr in mapx.listLayers('*AWS'):
        if lyr.isFeatureLayer:
            arcpy.management.ApplySymbologyFromLayer(
            lyr,
            aws_lyr,
            symbology_fields="VALUE_FIELD aws0_30 aws0_30"
            )

# Apply SOC symbology
    for lyr in mapx.listLayers('*SOC'):
        if lyr.isFeatureLayer:
            arcpy.management.ApplySymbologyFromLayer(
            lyr,
            soc_lyr,
            symbology_fields="VALUE_FIELD soc0_30 soc0_30"
            )

for mapx in aprx.listMaps():
    apply_soil_symbology()

# Save project
aprx.save()

# Remove lock file
del aprx
