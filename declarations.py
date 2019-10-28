path_token = "input/TOKEN.json"
path_credentials = "input/credentials.json"
path_dataset = "input/dataset.json"
path_area_of_interest = "input/area_of_interest.json"

path_Ragnar_retrieved_results = "{}Ragnar_retrieved_results.json"
path_Kraken_retrieved_mapIds = "{}{}/Kraken_retrieved_mapIds.json"


headers = {'Content-Type': 'application/json'}

SK_output_files = {
            'imagery': {
                'raster': {'truecolor': 'truecolor.png', 'imagery': 'imagery.ski', 'analysis': 'analysis.geotiff',
                           'visualization': 'visualization.geotiff'},
                'vector': {'metadata': 'metadata.json'}
            },
            'cars': {
                'raster': {'cars': 'cars.png', 'trucks': 'trucks.png', 'segmentation': 'segmentation.ski',
                           'analysis': 'analysis.geotiff', 'visualization': 'visualization.geotiff'},
                'vector': {'detections': 'detections.geojson', 'metadata': 'metadata.json'}
            }
        }
