import arcpy
from setup_project import aprx, LAYER_FOLDER

# Import texture, AWS, and SOC symbology as group layer
def apply_crop_symbology():
    ''' Apply symbology to crop layers.
    '''
    for lyr in mapx.listLayers('*Crops'):
        if mapx.name == 'WaSHI_Roadmap':
            sym_lyr = LAYER_FOLDER + lyr.name + '.lyrx'
        else:
            sym_lyr = LAYER_FOLDER + mapx.name + '_Crops.lyrx'
        if lyr.isFeatureLayer:
            arcpy.management.ApplySymbologyFromLayer(
            lyr,
            sym_lyr
            )

for mapx in aprx.listMaps():
    apply_crop_symbology()

# Save project
aprx.save()

# Remove lock file
del aprx
