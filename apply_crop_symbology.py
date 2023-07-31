import arcpy
from setup_project import aprx

# Import texture, AWS, and SOC symbology as group layer
def apply_crop_symbology():
    ''' Apply symbology to crop layers.
    '''
    layer_folder = 'C:/ArcGIS/WaSHI_Roadmap_2023/Layer_Files/'

    for lyr in mapx.listLayers('*Crops'):
        if mapx.name == 'WaSHI_Roadmap':
            sym_lyr = layer_folder + lyr.name + '.lyrx'
        else:
            sym_lyr = layer_folder + mapx.name + '_Crops.lyrx'
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
