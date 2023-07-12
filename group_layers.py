from setup_project import (aprx, mapx)

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
