import pandas as pd
import requests
import xml.etree.ElementTree as ET
from abc import ABC, abstractmethod, ABCMeta


class Fetcher(metaclass=ABCMeta):

    @abstractmethod
    def fetch(self, url: str) -> pd.DataFrame:
        raise NotImplementedError()

class TitleFetcher(Fetcher):
    def fetch(self, url: str) -> pd.DataFrame:
        base_url = 'https://stats.bis.org/api/v2/data/dataflow/BIS'
        resolved_url = f'{base_url}/{url}'
        print(f'Getting URL: {resolved_url}')
        response = requests.get(f'{base_url}/{url}')

        xml = response.content.decode("utf-8") 
        root = ET.fromstring(xml)
        obs_elems = [elem.attrib for elem in root.findall(".//Obs")]

        if len(obs_elems) == 0:
            print(f'Returned no data for url {resolved_url}')
            return None

        series = root.findall(".//Series")
        title = series[0].get("TITLE")
        data = [(obs.get("TIME_PERIOD"), obs.get("OBS_VALUE"), title) for obs in obs_elems]
        
        df = pd.DataFrame(data, columns = ['Date', 'Value', 'Description'])
        print(f'Returned {len(df.index)} rows for {title}')

        return df

class GenericFetcher(Fetcher):
    def fetch(self, url: str) -> pd.DataFrame:
        base_url = 'https://stats.bis.org/api/v2/data/dataflow/BIS'
        resolved_url = f'{base_url}/{url}'
        print(f'Getting URL: {resolved_url}')
        response = requests.get(f'{base_url}/{url}')

        xml = response.content.decode("utf-8") 
        root = ET.fromstring(xml)
        obs_elems = [elem.attrib for elem in root.findall(".//Obs")]

        if len(obs_elems) == 0:
            print(f'Returned no data for url {resolved_url}')
            return None

        data = [(obs.get("TIME_PERIOD"), obs.get("OBS_VALUE")) for obs in obs_elems]
        
        df = pd.DataFrame(data, columns = ['Date', 'Value'])
        print(f'Returned {len(df.index)} rows for {url}')
        return df


