import arcpy
from setup_project import (PROJECT_GDB, NRAS_URL,
                           aprx, mapx)

from apply_crop_symbology import apply_crop_symbology

# Create feature classes from 2022 WSDA crop map service for
# each Roadmap Focus Area
CROP_URL = NRAS_URL + 'WSDACrop_2022/MapServer/0'

def create_crop_map(name, sql):
    '''Select polygons from the WSDA Ag Land Use rest service
    and create a map.

    Keyword arguments:
    name -- the name of the resulting feature class
    sql -- the sql statement used to select the polygons
    '''
    # Create feature class by extracting polygons from rest service
    arcpy.analysis.Select(CROP_URL,
                          name,
                          sql
                          )
    # Add fc to map
    mapx.addDataFromPath(PROJECT_GDB + name)
    # Save project
    aprx.save()
    # Print a success message
    if arcpy.Exists(name):
        print(f'Successfully created {name}.')

# Columbia Basin Irrigated
create_crop_map(
    'CBI_Crops',
    '''Irrigation <> 'None'
    AND CropGroup NOT IN ('Commercial Tree', 'Developed', 'Flower Bulb',
    'Green Manure', 'Melon', 'Other', 'Shellfish', 'Turfgrass')
    AND County IN ('Adams', 'Benton', 'Kittitas', 'Grant', 'Franklin',
    'Walla Walla', 'Yakima')
    AND CropGroup IS NOT NULL'''
)

# Columbia Basin Irrigated Potato
create_crop_map(
    'CBIP_Crops',
    '''Irrigation <> 'None'
    And CropType  = 'Potato'
    And County IN ('Adams', 'Benton', 'Franklin', 'Kittitas', 'Grant',
    'Walla Walla', 'Yakima')'''
)

# Dryland
create_crop_map(
    'Dryland_Crops',
    '''Irrigation = 'None'
    AND CropType IN ('Wheat', 'Wheat Fallow', 'Pea, Dry', 'Oat', 'Canola',
    'Barley', 'Triticale', 'Bean, Garbanzo', 'Lentil')
    AND County IN ('Okanogan', 'Benton', 'Klickitat', 'Chelan', 'Yakima',
    'Kittitas', 'Lincoln', 'Adams', 'Douglas', 'Grant', 'Franklin', 'Stevens',
    'Ferry', 'Spokane', 'Pend Oreille', 'Asotin', 'Walla Walla', 'Whitman',
    'Garfield', 'Columbia')'''
)

# Grape
create_crop_map(
    'Grape_Crops',
    '''CropType IN ('Grape, Juice', 'Grape, Wine')
    AND County IN ('Adams', 'Asotin', 'Benton', 'Chelan', 'Columbia',
    'Douglas', 'Ferry', 'Franklin', 'Garfield', 'Grant', 'Kittitas',
    'Klickitat', 'Lincoln', 'Okanogan', 'Pend Oreille', 'Spokane', 'Stevens',
    'Walla Walla', 'Yakima', 'Whitman')'''
)

# NW Annual
create_crop_map(
    'Northwest_Annual_Crops',
    '''County IN ('Snohomish', 'Whatcom', 'Skagit')
    AND CropGroup IN ('Seed', 'Vegetable', 'Hay/Silage', 'Flower Bulb',
    'Cereal Grain')'''
)

# Raspberry
create_crop_map(
    'Caneberry_Crops',
    "CropType = 'Caneberry'"
)

# Tree Fruit
create_crop_map(
    'Tree_Fruit_Crops',
    '''County IN ('Adams', 'Asotin', 'Benton', 'Chelan', 'Columbia', 'Douglas',
    'Ferry', 'Franklin', 'Garfield', 'Grant', 'Kittitas', 'Klickitat',
    'Lincoln', 'Okanogan', 'Pend Oreille', 'Spokane', 'Stevens', 'Walla Walla',
    'Whitman', 'Yakima')
    AND CropType IN ('Apple', 'Apricot', 'Cherry', 'Nectarine/Peach', 'Pear',
    'Plum')'''
)

# Western Diversified
create_crop_map(
    'Western_Diversified_Crops',
    '''CropType = 'Market Crops'
    And County IN ('Clallam', 'Clark', 'Cowlitz', 'Grays Harbor', 'Island',
    'Jefferson', 'King', 'Kitsap', 'Lewis', 'Mason', 'Pacific', 'Pierce',
    'San Juan', 'Skagit', 'Skamania', 'Snohomish', 'Thurston', 'Wahkiakum',
    'Whatcom')'''
)

apply_crop_symbology()

# Save the project
aprx.save()

# Remove file locks
del aprx

print('Now run create_soils_maps.py.')
