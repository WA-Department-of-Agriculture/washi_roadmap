import sys
import arcpy

# Set gdb paths
SSURGO_GDB = 'C:/ArcGIS/gSSURGO_WA/gSSURGO_WA.gdb/'
PROJECT_GDB = 'C:/ArcGIS/WaSHI_Roadmap_2023/WaSHI_Roadmap_2023.gdb/'
SCRATCH_GDB = 'C:/ArcGIS/WaSHI_Roadmap_2023/scratch.gdb/'

# Set layer folder path
LAYER_FOLDER = 'C:/ArcGIS/WaSHI_Roadmap_2023/Layer_Files/'

# NRAS REST Service URL
NRAS_URL = 'https://fortress.wa.gov/agr/gis/wsdagis/rest/services/NRAS/'

def set_env(gdb: str, overwrite: bool):
    '''Set arcpy environment

    Keyword arguments:
    gdb -- file path to the file geodatabase to set as environment
    overwrite -- True/False if you want functions to overwrite existing fc
    '''
    arcpy.env.workspace = gdb
    arcpy.env.overwriteOutput = overwrite

set_env(PROJECT_GDB, True)

# Set ArcGIS Pro Project
aprx = arcpy.mp.ArcGISProject('C:/ArcGIS/WaSHI_Roadmap_2023/WaSHI_Roadmap_2023.aprx')

# Check if project is read only
if aprx.isReadOnly:
    print('Project is read only.')
    # Exit if read only
    sys.exit()

# Create scratch gdb for intermediate data
if arcpy.Exists(SCRATCH_GDB) is True:
    print('scratch.gdb already exists.')
else:
    arcpy.management.CreateFileGDB('C:/ArcGIS/WaSHI_Roadmap_2023/',
                                   'scratch.gdb')
    print('Created scratch.gdb.')

# Assign roadmap map to variable or create map if it doesn't already exist
roadmap = aprx.listMaps('WaSHI_Roadmap')

if len(roadmap) == 1:
    mapx = roadmap[0]
    print('WaSHI_Roadmap already exists.')
elif len(roadmap) == 0:
    aprx.createMap('WaSHI_Roadmap', 'Map')
    mapx = aprx.listMaps('WaSHI_Roadmap')[0]
    print('Created WaSHI_Roadmap.')
