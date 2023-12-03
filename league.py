from config import Config
import requests
from datetime import datetime
import logging
from typing import Optional, List, Dict, Any

config = Config()


class RiotAPI:
    """Riot API class, handles all requests to the Riot API"""

    def __init__(self, config: Config, region: Optional[str] = "euw1") -> None:
        self.api_key = config.get("api_key")
        self.session = requests.Session()
        self.session.headers.update({"X-Riot-Token": self.api_key})
        self.region = region

    def get_summoner_id(self, summoner_name: str) -> Dict[str, str]:
        url = f"https://{self.region}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{summoner_name}"
        try:
            response = self.session.get(url)
            response.raise_for_status()
            data = response.json()
            return {
                "sum_id": data["id"],
                "account_id": data["accountId"],
                "puuid": data["puuid"],
            }
        except requests.RequestException as e:
            logging.error(f"Error getting summoner: {e}")
            return {}

    def get_matches(self, puuid: str, params: Dict[str, Any]) -> List[str]:
        url = f"https://europe.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids"
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logging.error(f"Error fetching matches: {e}")
            return []

    def get_match_info(self, match_id: str) -> dict:
        """
        Returns a dict with match info
        """
        url = f"https://europe.api.riotgames.com/lol/match/v5/matches/{match_id}"
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logging.error(f"Error fetching match info: {e}")
            return {}

    def get_match_timeline(self, match_id: str) -> dict:
        """
        Returns a dict with match timeline
        """
        url = (
            f"https://europe.api.riotgames.com/lol/match/v5/matches/{match_id}/timeline"
        )
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logging.error(f"Error fetching match timeline: {e}")
            return {}


class League:
    """
    The League class represents a League of Legends summoner and provides methods
    to retrieve summoner-specific information from the Riot Games API. It uses the
    RiotAPI class to handle the actual API requests"""

    def __init__(self, summoner_name: str, api: RiotAPI) -> None:
        self.api = api
        summoner_data = self.api.get_summoner_id(summoner_name)
        self.sum_id = summoner_data.get("sum_id", "")
        self.account_id = summoner_data.get("account_id", "")
        self.puuid = summoner_data.get("puuid", "")

    def get_matches(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        queue_id: Optional[int] = None,
        type: Optional[str] = None,
        start: Optional[int] = 0,
        count: Optional[int] = 10,
    ) -> List[str]:
        """
        Returns a list of match ids for the given summoner
        """
        params = {}
        if start_date is not None:
            start_date = self.date_2_epoch(start_date)
            params["startTime"] = start_date
        if end_date is not None:
            end_date = self.date_2_epoch(end_date)
            params["endTime"] = end_date
        if queue_id is not None:
            params["queue"] = queue_id
        if type is not None:
            params["type"] = type
        if start is not None:
            params["start"] = start
        if count is not None:
            params["count"] = count

        return self.api.get_matches(self.puuid, params)

    def get_match_info(self, match_id: str) -> dict:
        """
        Returns a dict with match info
        """
        return self.api.get_match_info(match_id)

    def get_match_timeline(self, match_id: str) -> dict:
        """
        Returns a dict with match timeline
        """
        return self.api.get_match_timeline(match_id)

    @staticmethod
    def date_2_epoch(date: str) -> int:
        """
        Converts a date string to epoch time
        """
        return int(datetime.strptime(date, "%Y-%m-%d").timestamp())

    @staticmethod
    def epoch_2_date(epoch: int) -> str:
        """
        Converts a epoch time to a date string
        """
        return datetime.fromtimestamp(epoch).strftime("%Y-%m-%d")
