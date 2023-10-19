import requests
import json
from types import SimpleNamespace
from typing import TypeVar, Generic, Optional, Dict
from collections import namedtuple
from pydantic import BaseModel


T = TypeVar('T')

class WaiiHttpClient(Generic[T]):
    instance = None

    def __init__(self, url: str = 'http://localhost:9859/api/', apiKey: str = ''):
        if WaiiHttpClient.instance is not None:
            raise Exception("This class is a singleton!")
        else:
            WaiiHttpClient.instance = self
        self.url = url
        self.apiKey = apiKey
        self.timeout = 150000000
        self.scope = ''
        self.orgId = ''
        self.userId = ''

    @classmethod
    def get_instance(cls, url: str = 'http://localhost:9859/api/', apiKey: str = ''):
        if cls.instance is None:
            cls.instance = WaiiHttpClient(url, apiKey)
        return cls.instance

    def set_scope(self, scope: str):
        self.scope = scope

    def get_scope(self):
        return self.scope

    def set_org_id(self, orgId: str):
        self.orgId = orgId

    def set_user_id(self, userId: str):
        self.userId = userId

    def common_fetch(
            self, 
            endpoint: str,
            params: Dict,
            cls: BaseModel = None,
            need_scope: bool = True,
        ) -> Optional[T]:

        if need_scope:
            if not self.scope or self.scope.strip() == '':
                raise Exception("You need to activate connection first, use `WAII.Database.activate_connection(...)`")
            params['scope'] = self.scope
        params['org_id'] = self.orgId
        params['user_id'] = self.userId

        headers = {'Content-Type': 'application/json'}
        response = requests.post(self.url + endpoint, headers=headers, data=json.dumps(params, default=vars), timeout=self.timeout/1000)  # timeout is in seconds

        if response.status_code != 200:
            try:
                error = response.json()
                raise Exception(error.get('detail', ''))
            except json.JSONDecodeError:
                raise Exception(response.text)
        try:
            if cls:
                result: T = cls(**response.json())
            else:
                result: T = json.loads(response.text, object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))
            #result.__class__ = typing_inspect.get_bound(T)
            #result: T = json.loads(response.text, object_hook=lambda d: T(**d))
            return result
        except json.JSONDecodeError:
            raise Exception("Invalid response received.")
