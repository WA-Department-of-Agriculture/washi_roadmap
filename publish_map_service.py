import os
import time
import arcpy
from setup_project import PROJECT_GDB, aprx, mapx
from credentials import SD_FOLDER, CREDS_PATH

# Script start time
T0_SCRIPT = time.perf_counter()

# Start time
T0 = time.perf_counter()

# Create publish gdb in the GIS shared drive
# so data may be referenced rather than copied to the server
PUBLISH_FOLDER = r'//Agrfloly01/WSDA_GIS/DATA/PublishSpace/CommonData/NRAS/Soils/'
PUBLISH_NAME = '2023_WaSHI_Roadmap.gdb'
PUBLISH_GBD = os.path.join(PUBLISH_FOLDER, PUBLISH_NAME)

if arcpy.Exists(PUBLISH_GBD) is True:
    print(f'{PUBLISH_NAME} aready exists.')
else:
    arcpy.management.CreateFileGDB(PUBLISH_FOLDER,
                                   PUBLISH_NAME)
    print(f'Created {PUBLISH_NAME}.')

print('Started copying project gdb to publish gdb at', time.strftime("%x %X"))
# Copy project gdb to publish gdb
arcpy.management.Copy(PROJECT_GDB, PUBLISH_GBD)

print('Started changing project connection at', time.strftime("%x %X"))
# Change data source from project to publish gdb
aprx.updateConnectionProperties(PROJECT_GDB, PUBLISH_GBD)

aprx.save()

# End time
T1 = time.perf_counter()
print(f'Updated gdb from project to publish in {round((T1-T0)/60, 2)} minutes.')

# Set output file names
OUTDIR = SD_FOLDER
SERVICE_NAME = 'WaSHI_Roadmap_2023'
SSDRAFT_FILENAME = SERVICE_NAME + '.sddraft'
SDDRAFT_OUTPUT_FILENAME = os.path.join(OUTDIR, SSDRAFT_FILENAME)
SD_FILENAME = SERVICE_NAME + '.sd'
SD_OUTPUT_FILENAME = os.path.join(OUTDIR, SD_FILENAME)

# Reference map to publish
m = mapx

# Create MapServiceDraft and set metadata and server folder properties
print('Started creating map sd at', time.strftime("%x %X"))

sddraft = arcpy.sharing.CreateSharingDraft(
    'STANDALONE_SERVER',
    'MAP_SERVICE',
    SERVICE_NAME,
    m
    )

sddraft.targetServer = CREDS_PATH
sddraft.copyDataToServer = True
sddraft.overwriteExistingService = True
sddraft.credits = """WSDA Agricultural Land Use Mapping Program (2022);
USDA NRCS gSSURGO Washington Database (2022)"""
sddraft.summary = """Geospatial data layers for the Washington Soil Health Roadmap
(https://soilhealth.wsu.edu/washington-state-soil-health-roadmap/)"""
sddraft.tags = 'WaSHI, NRAS, WSDA, WSU, soils, crops, agriculture'
sddraft.serverFolder = 'NRAS'

# Create Service Definition Draft file
sddraft.exportToSDDraft(SDDRAFT_OUTPUT_FILENAME)

# Start time
T0 = time.perf_counter()

# Stage Service
print('Started staging at', time.strftime("%x %X"))
arcpy.server.StageService(SDDRAFT_OUTPUT_FILENAME,
                          SD_OUTPUT_FILENAME)

# End time
T1 = time.perf_counter()
print(f'Staged in {round((T1-T0)/60, 2)} minutes.')

# Start time
T0 = time.perf_counter()

# Publish to server
print('Started uploading at', time.strftime("%x %X"))
arcpy.server.UploadServiceDefinition(SD_OUTPUT_FILENAME,
                                     CREDS_PATH)
# End time
T1 = time.perf_counter()
print(f'Published in {round((T1-T0)/60, 2)} minutes.')

# Script end time
T1_SCRIPT = time.perf_counter()
print(f'Script finished in {round((T1_SCRIPT-T0_SCRIPT)/60, 2)} minutes.')

del aprx

print('Last script to run: create_webmaps.py!')
