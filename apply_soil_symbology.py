import arcpy
from setup_project import aprx

# Import texture, AWS, and SOC symbology as group layer
def apply_soil_symbology():
    ''' Apply symbology for AWS, SOC, and texture layers.
    '''
    layer_folder = 'C:/ArcGIS/WaSHI_Roadmap_2023/Layer_Files/'
    aws_lyr = layer_folder + 'AWS.lyrx'
    soc_lyr = layer_folder + 'SOC.lyrx'
    texture_lyr = layer_folder + 'Texture.lyrx'

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
