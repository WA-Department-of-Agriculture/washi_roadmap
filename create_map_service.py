import sys
import time
import arcpy

# Script start time
T0_SCRIPT = time.perf_counter()

# Set ArcGIS Pro Project
aprx = arcpy.mp.ArcGISProject("C:/ArcGIS/WaSHI_Roadmap/WaSHI_Roadmap.aprx")

# Set gdb path and workspace
PROJECT = "c:/ArcGIS/WaSHI_Roadmap/WaSHI_Roadmap.gdb/"
arcpy.env.workspace = PROJECT

# Set overwrite to True
arcpy.env.overwriteOutput = True

# Check if project is read only
if aprx.isReadOnly:
    print("Project is read only.")
    # Exit if read only
    sys.exit()

# Create map variable
mapx = aprx.listMaps("WaSHI_Roadmap")[0]

# Group layers by focus group

def group_lyrs(group_name):
    """
    Create group layer for focus group. Then add layers with group_name 
    prefix to the new group layer and remove the ungrouped layer.

    Keyword arguments:
    group_name -- The name of new group layer that is also the prefix to the 
                  layers to be moved into the newly created group layer.
    """
    mapx.createGroupLayer(group_name)
    for lyrx in mapx.listLayers(group_name + "*"):
        if lyrx.isFeatureLayer:
            mapx.addLayerToGroup(mapx.listLayers(group_name)[0], lyrx)
            mapx.removeLayer(lyrx)

groups = ["CBI", "CBIP", "Dryland", "Grape", "Northwest_Annual",
          "Caneberry", "Tree_Fruit", "Western_Diversified"]

for group in groups:
    group_lyrs(group)

# Save project
aprx.save()

# Remove lock file
del aprx

# Script end time
T1_SCRIPT = time.perf_counter()
print(f"Script finished in {round((T1_SCRIPT-T0_SCRIPT)/60, 2)} minutes.")
