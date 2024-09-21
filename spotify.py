import os
from dotenv import load_dotenv
from requests import get, post
import base64
import json
import urllib.parse

class Spotify:

    load_dotenv()
    __client_id = os.getenv("CLIENT_ID")
    __client_secret = os.getenv("CLIENT_SECRET")
    
    def __init__(self, method=None, result=None):
        self.__token = Spotify.__get_token(self.__client_id,self.__client_secret)
        self.__auth = {"Authorization": "Bearer " + self.__token}

        if method and result:
            self.function = method
            self.reqresult = result

    @property
    def __token(self):
        return self._token
    
    @__token.setter
    def __token(self, jsonresult):
        if not jsonresult:
            raise ValueError("No result given")
        
        if "error" in jsonresult:
            raise KeyError(jsonresult["error_description"])
        
        if not "access_token" in jsonresult:
            raise ValueError("Invalid result")
        
        self._token = jsonresult["access_token"]

    @property
    def reqresult(self):
        return self._reqresult
    
    @reqresult.setter
    def reqresult(self, result):
        if "error" in result:
            raise ValueError(result["error_description"])
        
        match self.function:
            case "get_artist_id":
                self._reqresult = result["artists"]["items"][0]["id"]

            case "get_albums":   
                self._reqresult = []
                for n in result["items"]:
                    self._reqresult.append(n["id"])

            case "get_tracks":
                self._reqresult = []
                for n in result["items"]:
                    self._reqresult.append(n["external_urls"]["spotify"])

            case "get_embed":
                self._reqresult = result

            case _:
                raise KeyError("No such function found")
    
    @staticmethod
    def __get_token(client_id,client_secret):
        url = "https://accounts.spotify.com/api/token"
        auth_string = client_id + ":" + client_secret
        auth_bytes = auth_string.encode("utf-8")
        auth_b64 = str(base64.b64encode(auth_bytes), "utf-8")
        headers ={
            "Authorization": "Basic " + auth_b64,
            "Content-Type": "application/x-www-form-urlencoded"
        }
        body = {"grant_type": "client_credentials"}
        result = post(url,data=body,headers=headers)
        json_result = json.loads(result.content)

        return json_result
    
    @classmethod
    def get_artist_id(cls, name, session):
        query = urllib.parse.quote(name)
        url = f"https://api.spotify.com/v1/search?q={query}&type=artist&limit=1"
        header = session.__auth
        result = get(url,headers=header)
        json_result = json.loads(result.content)

        return cls("get_artist_id", json_result)
    
    @classmethod
    def get_albums(cls, artist_id, session):
        url = f"https://api.spotify.com/v1/artists/{artist_id}/albums?include_groups=album%2Csingle%2Cappears_on&limit=50"
        header = session.__auth
        result = get(url,headers=header)
        json_result = json.loads(result.content)

        return cls("get_albums", json_result)
    
    @classmethod
    def get_tracks(cls, album_id, session):

        url = f"https://api.spotify.com/v1/albums/{album_id}/tracks?limit=50"
        header = session.__auth
        result = get(url,headers=header)
        json_result = json.loads(result.content)
        
        return cls("get_tracks", json_result)
    
    @classmethod
    def get_embed(cls, track_url):
        url = f"https://open.spotify.com/oembed?url={urllib.parse.quote(track_url)}"
        result = get(url)
        json_result = json.loads(result.content)

        return cls("get_embed", json_result)


if __name__ == "__main__":

    api = Spotify()
    id = api.get_artist_id("Laufey", api)
    album = api.get_albums(id.reqresult,api)
    tracks = api.get_tracks(album.reqresult[0], api)
    embed = api.get_embed(tracks.reqresult[0])

    with open("html.json", "w") as file:
        file.write(json.dumps(embed.reqresult,indent=4))