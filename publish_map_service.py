import os
import time
import arcpy
from setup_project import mapx
from credentials import SD_FOLDER, CREDS_PATH

# Script start time
T0_SCRIPT = time.perf_counter()

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
sddraft = arcpy.sharing.CreateSharingDraft(
    'STANDALONE_SERVER',
    'MAP_SERVICE',
    SERVICE_NAME,
    m
    )

sddraft.targetServer = CREDS_PATH
sddraft.overwriteExistingService = True
sddraft.credits = """
    WSDA Agricultural Land Use Mapping Program (2022); 
    USDA NRCS gSSURGO Washington Database (2022)
    """
sddraft.summary = """
    Geospatial data layers for the Washington Soil Health Roadmap
    (https://soilhealth.wsu.edu/washington-state-soil-health-roadmap/)
    """
sddraft.tags = 'NRAS, WSDA, soils, crops, agriculture'
sddraft.serverFolder = 'NRAS'

# Create Service Definition Draft file
sddraft.exportToSDDraft(SDDRAFT_OUTPUT_FILENAME)

# Start time
T0 = time.perf_counter()

# Stage Service
print('Start staging')
arcpy.server.StageService(SDDRAFT_OUTPUT_FILENAME,
                          SD_OUTPUT_FILENAME)

# End time
T1 = time.perf_counter()
print(f'Staged in {round((T1-T0)/60, 2)} minutes.')

# Start time
T0 = time.perf_counter()

# Publish to server
print('Start uploading')
arcpy.server.UploadServiceDefinition(SD_OUTPUT_FILENAME,
                                     CREDS_PATH)
# End time
T1 = time.perf_counter()
print(f'Published in {round((T1-T0)/60, 2)} minutes.')

# Script end time
T1_SCRIPT = time.perf_counter()
print(f'Script finished in {round((T1_SCRIPT-T0_SCRIPT)/60, 2)} minutes.')
