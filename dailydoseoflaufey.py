from spotify import Spotify
from random import randint
from flask import Flask, render_template, jsonify

app = Flask(__name__, template_folder="/Users/samshin/Downloads/Projects/dailydoesoflaufey")
api = Spotify()

#gets id for laufey

@app.route("/")
def laufey():
    laufey_id = api.get_artist_id("Laufey", api).reqresult

    laufey_albums = api.get_albums(laufey_id,api).reqresult
    random_album_id = laufey_albums[randint(0,len(laufey_albums)-1)]

    laufey_tracks = api.get_tracks(random_album_id, api).reqresult
    random_track = laufey_tracks[randint(0,len(laufey_tracks)-1)]

    embed = api.get_embed(random_track).reqresult
    iframe = embed["iframe_url"]
    
    return render_template("index.html",iframe=iframe)

if __name__ == "__main__":
    app.run(debug=True)