from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from itertools import count
import json
import logging
import os
import shutil
import time
import concurrent
import requests
from tenacity import retry, stop_after_attempt
from tqdm import tqdm
import yaml
from sports31.logging_config import setup_logger
from timer1101 import rootTimer as timer

# print(os.getcwd())
from sports31.crawl.coros_type import type2name, overlooked, type2file

# from crawling_coros.sporttype import type2name


logger = setup_logger(__name__)
retry_time = 10
timer.outputfunc = logger.info


class Crawler:
    def __init__(self, configdict):
        # SETTING
        self.headers = configdict["headers"]
        #
        self.cookies = {
            # "CPL-coros-token": f"{self.headers['accessToken']}",
            # "CPL-coros-region": "2",
        }
        self.get_userid()
        self.get_activities()
        self.results = []

    @retry(stop=stop_after_attempt(retry_time))
    def get_userid(self):
        url = r"https://teamcnapi.coros.com/account/query"
        r = requests.get(url, headers=self.headers, cookies=self.cookies)
        response_json = r.json()
        if "data" not in response_json:
            logging.error(f"请更新token后再次尝试, {response_json=}")
            raise PermissionError()
        userId = response_json["data"]["userId"]
        logger.info(f"{userId=}")
        self.userId = userId
        return userId

    @retry(stop=stop_after_attempt(retry_time))
    def get_activities(self):
        url = r"https://teamcnapi.coros.com/activity/query"

        ret = []
        for i in count(1):
            params = {"size": 20, "pageNumber": i, "modeList": ""}
            r = requests.get(
                url, params=params, headers=self.headers, cookies=self.cookies
            )
            response_json = r.json()
            data = response_json["data"]
            if "dataList" not in data:
                break
            activities = data["dataList"]
            ret.extend(activities)
        logger.info(f"总活动数量: {len(ret)}")
        # logger.info(f"活动: {ret}")
        self.activities = ret
        return ret

    def create_file(self, labelId, sportType, fileType):
        # NOTE coros使用了阿里云服务。coros的gpx文件是动态生成的，先访问activity-detail才能生成gpx文件。
        url = f"https://teamcnapi.coros.com/activity/detail/download"
        params = {"labelId": labelId, "sportType": sportType, "fileType": fileType}
        r = requests.post(
            url, params=params, headers=self.headers, cookies=self.cookies
        )
        if r.status_code != 200:
            logger.error(f"{r.status_code=}")
            logger.info(f"{r.json()}")
            return None
        url = json.loads(r.content)["data"]["fileUrl"]
        # time.sleep(3)
        return url

    def delete_file(self, labelId, sportType, fileType):
        url = f"https://oss.coros.com/gpx/{self.userId}/{labelId}.gpx"
        logger.info(f"{url=}")
        params = {"labelId": labelId, "sportType": sportType, "fileType": fileType}
        r = requests.delete(
            url, params=params, headers=self.headers, cookies=self.cookies
        )
        if r.status_code != 200:
            # if r.status_code == 200:
            logger.error(f"{r.status_code=}")
            logger.info(f"{r.text}")
            return None
        return r.json()

    @retry(stop=stop_after_attempt(retry_time))
    def download_file(self, local_path, labelId, sportType, fileType):
        url = self.create_file(labelId, sportType, fileType)
        time.sleep(1)
        # url = rf"https://oss.coros.com/gpx/{self.userId}/{labelId}.gpx"
        with requests.get(
            url, stream=True, headers=self.headers, cookies=self.cookies
        ) as r:
            if r.status_code != 200:
                logger.error(f"{r.status_code=} in {labelId=} {local_path}")
                return None
            with open(local_path, "wb") as f:
                shutil.copyfileobj(r.raw, f)
        logger.debug(f"{labelId=} {local_path}")
        return local_path

    def generate_task(self, dictionary, fileType):
        OVERLOOKED = "overlooked"
        DOWNLOADED = "downloaded"
        DOWNLOADING = "downloading"
        counter = {
            DOWNLOADING: 0,
            DOWNLOADED: 0,
            OVERLOOKED: 0,
        }
        args_list = []
        typecnt = defaultdict(int)
        for activite in self.activities:
            labelId = activite["labelId"]
            sportType = activite["sportType"]
            typecnt[sportType] += 1
            if fileType == 1 and sportType in overlooked:
                # logger.info(
                #     f"ignore活动, \
                #     运动类型：{type2name[sportType]},  \
                #     运动类型编号：{sportType} {labelId=}."
                # )
                counter[OVERLOOKED] += 1
                # logger.info(f"忽略活动 {type2name[sportType]}, {activite}")
                logger.debug(f"忽略活动 {type2name[sportType]}")
                continue
            path = f"{dictionary}/{labelId}.{type2file[fileType]}"
            if os.path.exists(path):
                counter[DOWNLOADED] += 1
                # logger.info(f"之前已经下载活动 {activite}")
                continue
            args_list.append((path, labelId, sportType, fileType))
            counter[DOWNLOADING] += 1
        namecnt = {type2name.get(k, k): v for k, v in typecnt.items()}
        # logger.info(f"{typecnt}")
        logger.info(f"{namecnt}")
        logger.info(f"{counter}")
        return args_list

    def crawl(self, dictionary, fileType):
        task_list = self.generate_task(dictionary, fileType)
        report = {"dowload": 0, "error": 0}
        total = len(task_list)
        with ThreadPoolExecutor(max_workers=8) as executor, tqdm(total=total) as pbar:
            futures = [executor.submit(self.download_file, *args) for args in task_list]
            for future in concurrent.futures.as_completed(futures):
                if future.result() is not None:
                    report["dowload"] += 1
                else:
                    report["error"] += 1
                pbar.update(1)
        logger.info(report)


def get_configdict(token):
    return {"headers": {"accessToken": token}}


def crawl(configdict, directory, fileType):
    logger.info(f"{directory=}")
    crawler = Crawler(configdict)
    # crawler.create_file(466416257514635285, 900, 1)
    # crawler.delete_file(466416257514635285, 900, 1)
    crawler.crawl(directory, fileType)
    logger.success(f"Finished.")


def defaultmain():
    configpath = r"./config/crawler_config.yaml"
    with open(configpath, "r", encoding="utf8") as file:
        # configdict = yaml.load(file.read(), Loader=yaml.FullLoader)
        configdict = yaml.safe_load(file)

    # dictionary = r"E:\sports_data\tom\gpx"
    # dictionary = r"E:\my gpx\li_coros"
    # dictionary = r"E:\sports_data\test"

    dictionary = r"./localdata/tom/fit"
    crawl(configdict, dictionary, 4)

    # dictionary = r"./localdata/yanny/fit"
    # main(configpath, dictionary, 4)

    #!! 截至到2025年3月1日 coros gpx文件依然有错误
    # dictionary = r"./localdata/tom/gpx"
    # main(configpath, dictionary, 1)


if __name__ == "__main__":
    defaultmain()
