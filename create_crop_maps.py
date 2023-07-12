import sys
import arcpy

# Set ArcGIS Pro Project
aprx = arcpy.mp.ArcGISProject("C:/ArcGIS/WaSHI_Roadmap/WaSHI_Roadmap.aprx")

# Check if project is read only
if aprx.isReadOnly:
    print("Project is read only.")
    # Exit if read only
    sys.exit()

# Set gdb path and workspace
PROJECT = "c:/ArcGIS/WaSHI_Roadmap/WaSHI_Roadmap.gdb/"
arcpy.env.workspace = PROJECT

# Set overwrite to True
arcpy.env.overwriteOutput = True

# Create map
aprx.createMap("WaSHI_Roadmap", "Map")
mapx = aprx.listMaps("WaSHI_Roadmap")[0]

# NRAS REST Services
NRAS_URL = "https://fortress.wa.gov/agr/gis/wsdagis/rest/services/NRAS/"

# Create feature classes from 2022 WSDA crop map service for
# each Roadmap Focus Area
CROP_URL = NRAS_URL + "WSDACrop_2022/MapServer/0"

def create_crop_map(name, sql):
    """Select polygons from the WSDA Ag Land Use rest service
    and create a map.

    Keyword arguments:
    name -- the name of the resulting feature class
    sql -- the sql statement used to select the polygons
    """
    # Create feature class by extracting polygons from rest service
    arcpy.analysis.Select(CROP_URL,
                          name,
                          sql
                          )
    # Add fc to map
    mapx.addDataFromPath(PROJECT + name)
    # Save project
    aprx.save()
    # Print a success message
    if arcpy.Exists(name):
        print(f"Successfully created {name}.")

# Columbia Basin Irrigated
create_crop_map(
    "CBI_Crops",
    """Irrigation <> 'None'
    AND CropGroup NOT IN ('Commercial Tree', 'Developed', 'Flower Bulb',
    'Green Manure', 'Melon', 'Other', 'Shellfish', 'Turfgrass')
    AND County IN ('Adams', 'Benton', 'Kittitas', 'Grant', 'Franklin',
    'Walla Walla', 'Yakima')
    AND CropGroup IS NOT NULL"""
)

# Columbia Basin Irrigated Potato
create_crop_map(
    "CBIP_Crops",
    """Irrigation <> 'None'
    And CropType  = 'Potato'
    And County IN ('Adams', 'Benton', 'Franklin', 'Kittitas', 'Grant',
    'Walla Walla', 'Yakima')"""
)

# Dryland
create_crop_map(
    "Dryland_Crops",
    """Irrigation = 'None'
    AND CropType IN ('Wheat', 'Wheat Fallow', 'Pea, Dry', 'Oat', 'Canola',
    'Barley', 'Triticale', 'Bean, Garbanzo', 'Lentil')
    AND County IN ('Okanogan', 'Benton', 'Klickitat', 'Chelan', 'Yakima',
    'Kittitas', 'Lincoln', 'Adams', 'Douglas', 'Grant', 'Franklin', 'Stevens',
    'Ferry', 'Spokane', 'Pend Oreille', 'Asotin', 'Walla Walla', 'Whitman',
    'Garfield', 'Columbia')"""
)

# Grape
create_crop_map(
    "Grape_Crops",
    """CropType IN ('Grape, Juice', 'Grape, Wine')
    AND County IN ('Adams', 'Asotin', 'Benton', 'Chelan', 'Columbia',
    'Douglas', 'Ferry', 'Franklin', 'Garfield', 'Grant', 'Kittitas',
    'Klickitat', 'Lincoln', 'Okanogan', 'Pend Oreille', 'Spokane', 'Stevens',
    'Walla Walla', 'Yakima', 'Whitman')"""
)

# NW Annual
create_crop_map(
    "Northwest_Annual_Crops",
    """County IN ('Snohomish', 'Whatcom', 'Skagit')
    AND CropGroup IN ('Seed', 'Vegetable', 'Hay/Silage', 'Flower Bulb',
    'Cereal Grain')"""
)

# Raspberry
create_crop_map(
    "Caneberry_Crops",
    "CropType = 'Caneberry'"
)

# Tree Fruit
create_crop_map(
    "Tree_Fruit_Crops",
    """County IN ('Adams', 'Asotin', 'Benton', 'Chelan', 'Columbia', 'Douglas',
    'Ferry', 'Franklin', 'Garfield', 'Grant', 'Kittitas', 'Klickitat',
    'Lincoln', 'Okanogan', 'Pend Oreille', 'Spokane', 'Stevens', 'Walla Walla',
    'Whitman', 'Yakima')
    AND CropType IN ('Apple', 'Apricot', 'Cherry', 'Nectarine/Peach', 'Pear',
    'Plum')"""
)

# Western Diversified
create_crop_map(
    "Western_Diversified_Crops",
    """CropType = 'Market Crops'
    And County IN ('Clallam', 'Clark', 'Cowlitz', 'Grays Harbor', 'Island',
    'Jefferson', 'King', 'Kitsap', 'Lewis', 'Mason', 'Pacific', 'Pierce',
    'San Juan', 'Skagit', 'Skamania', 'Snohomish', 'Thurston', 'Wahkiakum',
    'Whatcom')"""
)

# Set layer and symbology variables
for lyr in mapx.listLayers():
    # These crop maps are visualized by crop group instead of crop type
    cropGroup = ["CBI_Crops", "Northwest_Annual_Crops"]

    if lyr.isFeatureLayer:
        sym = lyr.symbology
        hasRenderer = hasattr(sym, "renderer")

        if hasRenderer is True and lyr.name not in [*cropGroup, "counties"]:
            sym.updateRenderer("UniqueValueRenderer")
            sym.renderer.fields = ["CropType"]
            sym.renderer.groups[0].heading = "Crop Type"
            lyr.symbology = sym
            print(f"Updated {lyr.name} renderer.")

        elif hasRenderer is True and lyr.name in cropGroup:
            sym.updateRenderer("UniqueValueRenderer")
            sym.renderer.fields = ["CropGroup"]
            sym.renderer.groups[0].heading = "Crop Group"
            lyr.symbology = sym
            print(f"Updated {lyr.name} renderer.")

# Columbia Basin Irrigated
cbi = mapx.listLayers("CBI_Crops")[0]
cbi_sym = cbi.symbology

for itm in cbi_sym.renderer.groups[0].items:
    itm.symbol.outlineColor = {"RGB": [0, 0, 0, 0]}

    if itm.label == "Berry":
        itm.symbol.color = {'RGB': [230, 0, 169, 100]}

    if itm.label == "Cereal Grain":
        itm.symbol.color = {'RGB': [255, 234, 190, 100]}

    if itm.label == "Hay/Silage":
        itm.symbol.color = {'RGB': [76, 115, 0, 100]}

    if itm.label == "Herb":
        itm.symbol.color = {'RGB': [0, 92, 230, 100]}

    if itm.label == "Nursery":
        itm.symbol.color = {'RGB': [205, 102, 102, 100]}

    if itm.label == "Oilseed":
        itm.symbol.color = {'RGB': [230, 230, 0, 100]}

    if itm.label == "Orchard":
        itm.symbol.color = {'RGB': [255, 0, 0, 100]}

    if itm.label == "Pasture":
        itm.symbol.color = {'RGB': [163, 255, 115, 100]}

    if itm.label == "Seed":
        itm.symbol.color = {'RGB': [68, 137, 112, 100]}

    if itm.label == "Vegetable":
        itm.symbol.color = {'RGB': [137, 68, 68, 100]}

    if itm.label == "Vineyard":
        itm.symbol.color = {'RGB': [169, 0, 230, 100]}

    cbi.symbology = cbi_sym
    print(f"Updated {itm.label} color to {itm.symbol.color}.")

# Columbia Basin Irrigated Potato
cbp = mapx.listLayers("CBIP_Crops")[0]
cbp_sym = cbp.symbology

for itm in cbp_sym.renderer.groups[0].items:
    itm.symbol.outlineColor = {"RGB": [0, 0, 0, 0]}

    if itm.label == "Potato":
        itm.symbol.color = {'RGB': [168, 56, 0, 100]}

    cbp.symbology = cbp_sym
    print(f"Updated {itm.label} color to {itm.symbol.color}.")

# Dryland
dry = mapx.listLayers("Dryland_Crops")[0]
dry_sym = dry.symbology

for itm in dry_sym.renderer.groups[0].items:
    itm.symbol.outlineColor = {"RGB": [0, 0, 0, 0]}

    if itm.label == "Wheat":
        itm.symbol.color = {'RGB': [186, 129, 74, 100]}

    if itm.label == "Wheat Fallow":
        itm.symbol.color = {'RGB': [255, 235, 175, 100]}

    if itm.label == "Barley":
        itm.symbol.color = {'RGB': [252, 146, 31, 100]}

    if itm.label == "Bean, Garbanzo":
        itm.symbol.color = {'RGB': [158, 85, 156, 100]}

    if itm.label == "Pea, Dry":
        itm.symbol.color = {'RGB': [167, 198, 54, 100]}

    if itm.label == "Canola":
        itm.symbol.color = {'RGB': [255, 222, 62, 100]}

    if itm.label == "Lentil":
        itm.symbol.color = {'RGB': [247, 137, 216, 100]}

    if itm.label == "Oat":
        itm.symbol.color = {'RGB': [230, 76, 0, 100]}

    if itm.label == "Triticale":
        itm.symbol.color = {'RGB': [60, 175, 153, 100]}

    dry.symbology = dry_sym
    print(f"Updated {itm.label} color to {itm.symbol.color}.")

# Grape
gra = mapx.listLayers("Grape_Crops")[0]
gra_sym = gra.symbology

for itm in gra_sym.renderer.groups[0].items:
    itm.symbol.outlineColor = {"RGB": [0, 0, 0, 0]}

    if itm.label == "Grape, Wine":
        itm.symbol.color = {'RGB': [196, 66, 69, 100]}

    if itm.label == "Grape, Juice":
        itm.symbol.color = {'RGB': [76, 0, 115, 100]}

    gra.symbology = gra_sym
    print(f"Updated {itm.label} color to {itm.symbol.color}.")

# NW Annual
nwa = mapx.listLayers("Northwest_Annual_Crops")[0]
nwa_sym = nwa.symbology

for itm in nwa_sym.renderer.groups[0].items:
    itm.symbol.outlineColor = {"RGB": [0, 0, 0, 0]}

    if itm.label == "Hay/Silage":
        itm.symbol.color = {'RGB': [76, 115, 0, 100]}

    if itm.label == "Cereal Grain":
        itm.symbol.color = {'RGB': [255, 234, 190, 100]}

    if itm.label == "Vegetable":
        itm.symbol.color = {'RGB': [137, 68, 68, 100]}

    if itm.label == "Seed":
        itm.symbol.color = {'RGB': [68, 137, 112, 100]}

    if itm.label == "Flower Bulb":
        itm.symbol.color = {'RGB': [255, 255, 115, 100]}

    nwa.symbology = nwa_sym
    print(f"Updated {itm.label} color to {itm.symbol.color}.")

# Raspberry
ras = mapx.listLayers("Caneberry_Crops")[0]
ras_sym = ras.symbology

for itm in ras_sym.renderer.groups[0].items:
    itm.symbol.outlineColor = {"RGB": [0, 0, 0, 0]}

    if itm.label == "Caneberry":
        itm.symbol.color = {'RGB': [230, 0, 169, 100]}

    ras.symbology = ras_sym
    print(f"Updated {itm.label} color to {itm.symbol.color}.")

# Tree Fruit
trf = mapx.listLayers("Tree_Fruit_Crops")[0]
trf_sym = trf.symbology

for itm in trf_sym.renderer.groups[0].items:
    itm.symbol.outlineColor = {"RGB": [0, 0, 0, 0]}

    if itm.label == "Apple":
        itm.symbol.color = {'RGB': [255, 0, 0, 100]}

    if itm.label == "Apricot":
        itm.symbol.color = {'RGB': [255, 211, 127, 100]}

    if itm.label == "Cherry":
        itm.symbol.color = {'RGB': [255, 175, 237, 100]}

    if itm.label == "Nectarine/Peach":
        itm.symbol.color = {'RGB': [253, 127, 111, 100]}

    if itm.label == "Pear":
        itm.symbol.color = {'RGB': [76, 230, 0, 100]}

    if itm.label == "Plum":
        itm.symbol.color = {'RGB': [132, 0, 168, 100]}

    trf.symbology = trf_sym
    print(f"Updated {itm.label} color to {itm.symbol.color}.")

# Western WA Diversified
wwd = mapx.listLayers("Western_Diversified_Crops")[0]
wwd_sym = wwd.symbology

for itm in wwd_sym.renderer.groups[0].items:
    itm.symbol.outlineColor = {"RGB": [0, 0, 0, 0]}

    if itm.label == "Market Crops":
        itm.symbol.color = {'RGB': [237, 81, 81, 100]}

    wwd.symbology = wwd_sym
    print(f"Updated {itm.label} color to {itm.symbol.color}.")

# Save the project
aprx.save()

# Remove file locks
del aprx
