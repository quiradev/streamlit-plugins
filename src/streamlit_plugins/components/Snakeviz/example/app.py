import asyncio
import concurrent
import json
import re
import time

import aiohttp
import requests
import streamlit as st
from aiohttp import ClientTimeout
from requests.adapters import HTTPAdapter
from urllib3 import Retry
from functools import wraps, partial

from streamlit_plugins.components.Snakeviz import st_snakeviz

# make it look nice from the start
st.set_page_config(layout='wide', initial_sidebar_state='collapsed')


class API:
    def __init__(self, url, asynchronus: bool = False, protocol=None, host=None, port=None):
        if url:
            self._url_base = url
        else:
            self._url_base = (
                    protocol + "://" +
                    host + ":" + port
            )
        self._session = None
        self._asynchronus = asynchronus
        if asynchronus:
            # A session context manager usage is not mandatory but await session.close()
            # method should be called in this case
            # Otras formas de interpretarlo
            # https://docs.aiohttp.org/en/stable/client_quickstart.html
            # self._session = aiohttp.ClientSession()
            # self._session = self._async_requests_retry_session()
            # self._session = self._async_requests_retry_session()
            # Para configurar ssl
            # https://docs.aiohttp.org/en/stable/client_advanced.html#ssl-control-for-tcp-sockets

            self._timeout = ClientTimeout(total=5*60, connect=1, sock_connect=None, sock_read=None)

            # Se parchea el metodo read con el correspondiente async
            self.read = self._read_async

        else:
            self._session = self._sync_requests_retry_session()
            # self._session.config['keep_alive'] = False
            # Se parchea el metodo read con el correspondiente sync
            self.read = self._read_sync

            # (connect timeout, read timeout)
            self._timeout = (0.5, 3)

    def _sync_requests_retry_session(self, total_retry=3, read_retry=3, connect_retry=3, backoff_factor=0.3, status_forcelist=(500, 502, 504)):
        """
        Solo realizara la politica de reintentos cuando se obtenga un status de la variable status_forcelist
        :param retries: Politica de reintentos -> (total, read, connect)
        :param backoff_factor:
        :param status_forcelist:
        :return:
        """
        self._session = self._session or requests.Session()
        retry_strategy = Retry(
            total=total_retry,
            read=read_retry,
            connect=connect_retry,
            backoff_factor=backoff_factor,
            status_forcelist=status_forcelist,
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self._session.mount('http://', adapter)
        self._session.mount('https://', adapter)
        return self._session

    def _async_requests_retry_session(self, total_retry=3, read_retry=3, connect_retry=3, backoff_factor=0.3, status_forcelist=(500, 502, 504)):
        """
        Solo realizara la politica de reintentos cuando se obtenga un status de la variable status_forcelist
        :param retries: Politica de reintentos -> (total, read, connect)
        :param backoff_factor:
        :param status_forcelist:
        :return:
        """
        # retry_options = ExponentialRetry(attempts=total_retry)  # , statuses=status_forcelist)
        # self._session = RetryClient(raise_for_status=False, retry_options=retry_options)
        #
        session = aiohttp.ClientSession()

        return session

    def _read_sync(self, query, endpoint="", headers=None):

        res_dict = self._perform_sync_request(url=f"{self._url_base}/{endpoint}", headers=headers, params=query)
        return res_dict

    async def _read_async(self, query, endpoint="", headers=None):
        res_dict = await self._perform_async_request(url=f"{self._url_base}/{endpoint}", headers=headers, params=query)
        return res_dict

    def update(self, query, **kwargs):
        pass

    def create(self, query, **kwargs):
        pass

    def delete(self, query, **kwargs):
        pass

    def _perform_sync_request(self, url, params=None, headers=None):
        r = self._session.get(url=url, params=params, headers=headers, timeout=self._timeout)
        r = r.json()

        res = json.loads(json.dumps(r, ensure_ascii=False))
        return res

    async def _perform_async_request(self, url, params=None, headers=None):
        # To disable canonicalization use encoded=True parameter for URL construction:
        # await session.get(
        #     URL('http://example.com/%30', encoded=True))
        # Passing params overrides encoded=True, never use both options.
        # session = self._async_requests_retry_session()
        session = self._async_requests_retry_session()
        async with session.get(url=url, params=params, headers=headers) as r:
            # print(f"Got response [{r.status}] for URL: {url}")
            r.raise_for_status()
            r = await r.json()
        await session.close()

        res = json.loads(json.dumps(r, ensure_ascii=False))

        return res

    async def _close_async_session(self):
        await self._session.close()

    def _close_sync_session(self):
        if self._session is not None:
            self._session.close()

    def __del__(self):
        if not self._asynchronus:
            self._close_sync_session()


def _get_async(func, loop=None, executor=None):
    @wraps(func)
    async def run(*args, _loop=None, _executor=None, **kwargs):
        if _loop is None:
            raise Exception
        pfunc = partial(func, *args, **kwargs)
        return await _loop.run_in_executor(_executor, pfunc)
    return partial(run, _loop=loop, _executor=executor)


def make_request_async_asyncio(_several_apis, **kwargs):
    def _run_request():
        return api.read({}, endpoint=api_data["endpoint_test"], headers=api_data["headers"])

    for key, api_data in _several_apis.items():
        futures = []
        loop = asyncio.new_event_loop()
        executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=6,
        )
        async_func = _get_async(_run_request, loop=loop, executor=executor)
        api = API(api_data["api"])

        for x in range(api_data["repeat"]):
            futures.append(async_func())

        async def _multiple_futures(_futures):
            return await asyncio.gather(*_futures)
        responses = loop.run_until_complete(_multiple_futures(futures))

        print("RESPONSES", len(responses))
        all_data = []
        for res in responses:
            # Append task
            all_data.append(res)
            # Search task
            re.findall(api_data["search_regex"], json.dumps(res))
            # Print task
            print(res)
            # Sleep task
            time.sleep(api_data["sleep_sec"])


several_apis = {
    "dog_api": {
        "api": "https://api.thedogapi.com/v1",
        "endpoint_test": "images/search",
        "headers": None,
        "repeat": 20,
        "sleep_sec": 0.01,
        "search_regex": "weight"
    },
    "dad_joke": {
        "api": "https://icanhazdadjoke.com/",
        "endpoint_test": "",
        "headers": {"Accept": "application/json"},
        "repeat": 20,
        "sleep_sec": 0.01,
        "search_regex": "[?!]"
    }
}

st_snakeviz(
    "request_async_asyncio_profiling", make_request_async_asyncio, several_apis
)
