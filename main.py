import asyncio
from authorization import Authorization
from ragnar import ImageSearch
from kraken import KrakenMap
from processing import Processing
from utilities import *
from declarations import *


loop = asyncio.get_event_loop()

path_RESULTS = set_output_path()
dates = set_search_dates()

# Authorization ->
auth = Authorization(loop)
if not (auth.check_token(path_token)):
    auth.request_token(path_credentials)
# Authorization <-


# Ragnar Image Search ->
print(colored("# Ragnar Image Search ->", color='white', attrs=['bold']))
image_search = ImageSearch(loop, path_dataset, path_area_of_interest, path_RESULTS)
pipelineId = image_search.initialize()
image_search.retrieve(pipelineId)
Ragnar_retrieved_results = image_search.retr_results
# Ragnar Image Search <-


# Kraken Map Search ->
map_type = "cars"
cars = KrakenMap(map_type, loop, path_Ragnar_retrieved_results.format(path_RESULTS), path_area_of_interest,
                 path_RESULTS)
cars_pipes = cars.initialize(dates)
cars.retrieve(cars_pipes)
cars.download(path_Kraken_retrieved_mapIds.format(path_RESULTS, map_type), SK_output_files)

map_type = "imagery"
imagery = KrakenMap(map_type, loop, path_Ragnar_retrieved_results.format(path_RESULTS), path_area_of_interest,
                    path_RESULTS)
imagery_pipes = imagery.initialize(dates)
imagery.retrieve(imagery_pipes)
imagery.download(path_Kraken_retrieved_mapIds.format(path_RESULTS, map_type), SK_output_files)
# Kraken Map Search <-

# Counting, Stitching, Combining ->
process = Processing(path_RESULTS)
process.count_cars()
process.stitch_images('cars.png')
process.stitch_images('truecolor.png')
process.combine_imgs(path_RESULTS+"imagery", path_RESULTS+"cars")
# Counting, Stitching, Combining <-

loop.close()
