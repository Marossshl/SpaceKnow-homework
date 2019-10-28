import asyncio
import json
import time
from aiohttp import ClientSession
import utilities
from termcolor import colored # https://pypi.org/project/termcolor/ # print(colored("XXX", color='magenta', on_color='on_green'))


class Task:
    def __init__(self, loop):
        self.loop = loop
        self.STATUS_URL = "https://spaceknow-tasking.appspot.com/tasking/get-status"


    async def do_the_request(self, url, headers, data):
        async with ClientSession() as session:
            async with session.request(url=url, method='post', data=data, headers=headers) as resp:
                response_dtr = await resp.json()
                response_dtr['status_code'] = resp.status
        await session.close()
        return response_dtr

    async def define_task(self, tasks, _task_result):
        for res in asyncio.as_completed(tasks):
            response_dt = await res
            _task_result[len(_task_result)] = response_dt

    def do_the_task(self, url, headers, data, repeat=False):
        task_result = {}

        if repeat:
            coros = list()
            payload = json.loads(data)
            coros = [self.do_the_request(url, headers, json.dumps(payload[str(idx)])) for idx in payload]

        else:
            coros = [self.do_the_request(url, headers, data) for i in range(1)]
        task = asyncio.ensure_future(self.define_task(coros, task_result))
        self.loop.run_until_complete(task)
        return task_result

    def get_status(self, headers, pipelineId, repeat=False):
        stat = self.do_the_task(self.STATUS_URL, headers, pipelineId, repeat)
        return stat

    def wait_till_resolved(self, headers, pipelineId, repeat=False):
        while True:
            stat = self.get_status(headers, pipelineId, repeat)
            status_all_tasks = utilities.go_through_all(stat)
            print(colored("Tasks in a set are: {}".format(status_all_tasks), color='blue'))
            assert status_all_tasks != 'FAILED',\
                    print(colored("Error in pipeline, some individual tasks FAILED", color='red'))

            if status_all_tasks == 'RESOLVED':
                break
            else:
                time.sleep(1)
        return status_all_tasks

