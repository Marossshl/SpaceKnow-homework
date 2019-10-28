from utilities import *
from tasks import Task
from termcolor import colored # https://pypi.org/project/termcolor/ # print(colored("XXX", color='magenta', on_color='on_green'))
from declarations import *


class ImageSearch:
    def __init__(self, loop, path_dataset, path_area_of_interest, path_RESULTS):
        self.RAGNAR_URL = "https://spaceknow-imagery.appspot.com/"
        self.dataset = read_json(path_dataset)
        self.area_of_interest = read_json(path_area_of_interest)
        self.imagery = self.dataset
        self.imagery["extent"] = self.area_of_interest
        self.pipelineId = {}
        self.retr_results = {}
        self.path_RESULTS = path_RESULTS
        self.loop = loop
        print(colored("Ragnar image search object created:", color='white', attrs=['bold']))

    def initialize(self):
        print(colored("Ragnar image search initialization start", color='blue'))
        init = Task(self.loop)
        search = init.do_the_task(self.RAGNAR_URL+"/imagery/search/initiate", headers, json.dumps(self.imagery))

        assert search[0].get('pipelineId'),\
            print(colored("Error, Ragnar image search failed: {}".format(str(search[0])), color='red'))

        result = init.wait_till_resolved(headers, json.dumps({"pipelineId": search[0]['pipelineId']}))
        assert result == 'RESOLVED',\
            print(colored("Error, Ragnar image search failed, pipelineId: {}".format(result), color='red'))

        self.pipelineId = search[0]['pipelineId']
        print(colored("Ragnar image search initialization OK", color='green'))
        return search[0]['pipelineId']

    def retrieve(self, pipelineId):
        print(colored("Ragnar image search retrieval start", color='blue'))
        retr = Task(self.loop)
        retrieved = retr.do_the_task(self.RAGNAR_URL+"/imagery/search/retrieve", headers,
                                     json.dumps({"pipelineId": pipelineId}))
        assert retrieved[0].get('results'), print(colored("Error, Ragnar image retrieval failed", color='red'))
        self.retr_results = retrieved[0]
        print(colored("Ragnar image search retrieval OK, metadata saved to:\n{}"
                      .format(self.path_RESULTS), color='green'))
        write_json(self.retr_results, self.path_RESULTS + "Ragnar_retrieved_results.json")


if __name__ == "__main__":
    import asyncio
    from authorization import Authorization

    loop = asyncio.get_event_loop()

    # In order to run you must have valid Token in the files,
    # run main.py or uncomment Authorization:

    # Authorization ->
    auth = Authorization(loop)
    if not (auth.check_token(path_token)):
        auth.request_token(path_credentials)
    # Authorization <-

    path_RESULTS = set_output_path()
    image_search = ImageSearch(loop, path_dataset, path_area_of_interest, path_RESULTS)
    pipelineId = image_search.initialize()
    image_search.retrieve(pipelineId)
    Ragnar_retrieved_results = image_search.retr_results

    loop.close()
