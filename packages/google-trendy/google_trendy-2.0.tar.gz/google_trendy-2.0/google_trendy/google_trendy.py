import json
import requests 
from enum import Enum
from datetime import datetime, timezone
import bs4 as bs
from urllib.parse import quote
from dataclasses import dataclass
from typing import Union

explore_url = "https://trends.google.com/trends/explore?q=/m/02bh_v&date=now+7-d&geo=US"
daily_trend_url = "https://trends.google.com/trending/rss"

'''
Website Article
'''
class Article():
    def __init__(self, data):
        self.title = data['title']
        self.url = data['url']
        self.source = data['source']

    def __str__(self):
        return f"Article({self.title}, {self.source}, {self.url})"
    def __repr__(self):
        return f"Article({self.title}, {self.source}, {self.url})"
    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=False, indent=4)
'''
Daily Google Search Trend
'''
class DailyTrend:
    def __init__(self, title, traffic, desc=None, link=None):
        self.title = title
        self.desc = desc
        self.link = link
        self.traffic = int(traffic.strip("+").replace(",",""))
    
    def __str__(self):
        return f"DailyTrend(title={self.title}, traffic={self.traffic:,}, link={self.link})"
    def __repr__(self):
        return f"DailyTrend(title={self.title}, traffic={self.traffic:,}, link={self.link})"


class TrendIndex(Enum):
    TITLE = 0
    START = 3
    END = 4
    VOLUME = 6
    PERC_CHANGE = 8
    SIMILAR = 9
    ARTICLES = 11

@dataclass
class GTrend:
    title: str
    start: Union[int, float] 
    end: Union[int, float] 
    volume: int
    perc_change: int 
    similar: list[str] 
    articles: list 
    start_date: datetime = None 
    end_date: datetime = None 

    def __post_init__(self):
        self.start_date = datetime.fromtimestamp(self.start, tz=timezone.utc) if self.start is not None else None
        self.end_date = datetime.fromtimestamp(self.end, tz=timezone.utc) if self.end is not None else None

    def __repr__(self):
        return f"GTrend(title={self.title!r}, volume={self.volume}, start={self.start_date.strftime('%Y-%m-%d %H:%M')})"

'''
Google Trends class - used to get realtime and daily search trends
'''
class GoogleTrends():
    def __init__(self):
        self.decoder = json.JSONDecoder()
        self.trends = []
        self.trend_ids = []
        self.entities = set([])

    def _jsonify(self, data):
        data = data.split('\n')[1]
        json_data = self.decoder.decode(data)
        return json_data

    def _request(self, url, data):
        headers = {
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8"
        }
        
        res = requests.post(url, data=data, headers=headers)
        res.raise_for_status()
        
        text = res.content.decode('utf-8')
        cleaned = text.lstrip(")]}'\n")
        json_data = json.loads(json.loads(cleaned)[0][2])[1]
        return json_data

    def get_trends(self):
        url="https://trends.google.com/_/TrendsUi/data/batchexecute?rpcids=i0OFE" 
        payload = [
            [
                "i0OFE",
                '[null,null,"US",0,"en",24,1]',
                None,
                "generic"
            ]
        ]
        json_payload = json.dumps([payload])
        data = f"f.req={quote(json_payload)}"
        json_data = self._request(url, data)
        self.trends = []
        for trend in json_data:
            start = trend[TrendIndex.START.value][0] if trend[TrendIndex.START.value]is not None else None
            end = trend[TrendIndex.END.value][0] if trend[TrendIndex.END.value]is not None else None
            self.trends.append(GTrend(
                trend[TrendIndex.TITLE.value],
                start, 
                end,
                trend[TrendIndex.VOLUME.value],
                trend[TrendIndex.PERC_CHANGE.value],
                trend[TrendIndex.SIMILAR.value],
                trend[TrendIndex.ARTICLES.value]))
        
        self.trends.sort(key=lambda x: x.volume, reverse=True)
        return self.trends


    def daily_trends(self):
        res = requests.get(daily_trend_url)
        if (res.status_code != 200):
            raise RuntimeError("ERROR getting daily trends from Google")
        
        soup = bs.BeautifulSoup(res.content, "xml")
        items = soup.find_all('item')
        searches = []
        for item in items:
            searches.append(DailyTrend(item.find('title').text, item.find('ht:approx_traffic').text, link=item.find("link").text))

        searches.sort(key=lambda x: x.traffic, reverse=True)
        return searches
    
