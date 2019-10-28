import os
import requests
from datetime import datetime as dt
from utilities import *
from tasks import Task
from termcolor import \
    colored  # https://pypi.org/project/termcolor/ # print(colored("XXX", color='magenta', on_color='on_green'))


class KrakenMap:
    def __init__(self, map_type, loop, path_Ragnar_retrieved_results, path_area_of_interest, path_RESULTS):
        self.KRAKEN_URL = "https://spaceknow-kraken.appspot.com/kraken/release/"
        self.available_scenes = read_json(path_Ragnar_retrieved_results)
        self.area_of_interest = read_json(path_area_of_interest)
        self.pipelineId = {}
        self.loop = loop
        self.map_type = map_type
        self.retr_mapIds = {}
        self.path_RESULTS = path_RESULTS
        self.params = {
            # 'force_download': 1,
            # 'download_unclipped': 1
        }
        print(colored("Kraken map retrieval object created: {}".format(self.map_type), color='white', attrs=['bold']))

    def initialize(self, dates):
        print(colored("Kraken map initialization start", color='blue'))

        URL = self.KRAKEN_URL + self.map_type + '/geojson/initiate'
        init = Task(self.loop)

        scenes_in_range = {}
        all_payloads = {}

        dto = dt.strptime((dates['to'][:10]), "%Y-%m-%d")
        dfrom = dt.strptime((dates['from'][:10]), "%Y-%m-%d")

        found = False
        when_are_maps_available = []
        for idx, band in enumerate(self.available_scenes['results']):
            date = dt.strptime((band['datetime'][:10]), "%Y-%m-%d")
            if dfrom < date < dto:
                scenes_in_range[len(scenes_in_range)] = band
                all_payloads[len(all_payloads)] = dict({
                    'sceneId': band['sceneId'],
                    'extent': self.area_of_interest
                })
                when_are_maps_available.append(str(date)[:10])
                found = True
        assert found, print(colored("No map available in the selected period: {}".format(dates), color='red'))
        print(colored("Maps available in the following dates: {}".format(when_are_maps_available), color='blue'))
        write_json(scenes_in_range, self.path_RESULTS + 'Ragnar_retrieved_results_in_dates.json')
        start = time.time()
        search = init.do_the_task(URL, headers, json.dumps(all_payloads), repeat=True)
        print(colored("Time to init Kraken: {}".format(time.time() - start), color='blue'))

        pipelines = dict()
        for idx in search:
            assert search[idx].get('pipelineId'), \
                print(colored("Error, Kraken map initialization failed: {}".format(str(search[idx])), color='red'))
            pipelines[idx] = dict(pipelineId=search[idx]['pipelineId'])

        result = init.wait_till_resolved(headers, json.dumps(pipelines), True)
        assert result == 'RESOLVED', \
            print(colored("Error, Kraken map initialization failed: {}".format(result), color='red'))

        print(colored("Kraken map initialization OK", color='green'))
        return pipelines

    def retrieve(self, pipelines):
        print(colored("Kraken mapId retrieval start", color='blue'))

        URL = self.KRAKEN_URL + self.map_type + '/geojson/retrieve'

        retr = Task(self.loop)
        retrieved = retr.do_the_task(URL, headers,
                                     json.dumps(pipelines), True)

        result = retr.wait_till_resolved(headers, json.dumps(pipelines), True)
        for idx in retrieved:
            assert retrieved[idx].get('mapId'), \
                print(colored("Error, Kraken mapId retrieval failed: {}".format(retrieved[idx]), color='red'))

        self.retr_mapIds = retrieved
        os.makedirs(self.path_RESULTS + self.map_type, exist_ok=True)
        write_json(self.retr_mapIds, self.path_RESULTS + self.map_type + "/Kraken_retrieved_mapIds.json")
        print(colored("Kraken mapId retrieval OK, mapIds written to file {}".format(
            self.path_RESULTS + self.map_type + "/Kraken_retrieved_mapIds.json"), color='green'))

    def download(self, path_mapIds, SK_output_files):
        print(colored("Kraken data download start", color='blue'))

        map_Ids = read_json(path_mapIds)

        for mapp in map_Ids:
            path = self.path_RESULTS + str(self.map_type) + '/mapId_' + str(mapp)
            os.makedirs(path, exist_ok=True)
            tile_list = []
            for tile_n, tile in enumerate(map_Ids[mapp]['tiles']):
                tile_list.append([tile[1], tile[2]])
                tile_name = str(tile[1]) + '_' + str(tile[2])
                path01 = path + '/' + tile_name
                os.makedirs(path01, exist_ok=True)
                print(colored("Downloading: Map type: {}, MapId: {}, tile: {}".format(self.map_type, mapp, tile_name),
                              color='blue'))
                for outputs in SK_output_files[self.map_type]:
                    path02 = path01 + '/' + outputs
                    os.makedirs(path02, exist_ok=True)
                    for output_file in SK_output_files[self.map_type][outputs]:
                        file_name = SK_output_files[self.map_type][outputs][output_file]
                        zoom = str(tile[0])
                        URL = "https://spaceknow-kraken.appspot.com/kraken/grid/" \
                              + str(map_Ids[str(mapp)]['mapId']) + "/-/" \
                              + zoom + "/" \
                              + str(tile[1]) + "/" \
                              + str(tile[2]) + "/" \
                              + file_name

                        down = requests.get(URL, params=self.params)
                        if down.status_code == 200:
                            with open(path02 + '/' + file_name, 'wb') as f:
                                for chunk in down.iter_content(1024):
                                    f.write(chunk)
                            print(colored("OK ", color='green'), end='')
                        else:
                            print(colored('Error at: Map type: {} MapId: {}, tile: {}, file: {}, status_code {}'
                                          .format(self.map_type, mapp, tile_name, file_name, down.status_code),
                                          color='red'))

                print()
            write_json(tile_list, path + '/tile_list.json')


if __name__ == "__main__":

    import asyncio
    from authorization import Authorization

    # In order to run you must have valid Token and Ragnar data in the files,
    # run ragnar.py separately or run main.py

    loop = asyncio.get_event_loop()

    # Authorization ->
    auth = Authorization(loop)
    if not (auth.check_token(path_token)):
        auth.request_token(path_credentials)
    # Authorization <-

    path_RESULTS = set_output_path()
    # dates = {"from": "2018-01-01", "to": "2018-06-30"}
    dates = set_search_dates()

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

    loop.close()
