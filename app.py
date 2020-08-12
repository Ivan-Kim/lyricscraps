import os
import requests
from bs4 import BeautifulSoup
import re
import urllib.parse
from flask import Flask, render_template, jsonify, request, make_response

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

KAKAOAPI = os.environ["KAKAOAPI"]
YOUTUBEAPI = os.environ["YOUTUBEAPI"]

@app.route("/")
def index():
    if request.method == "POST":
        query = request.form.get("query")
    else:
        return render_template("index.html")

@app.route("/search/<query>")
def search(query):
    r = requests.get(f'https://www.googleapis.com/youtube/v3/search?part=snippet&type=video&maxResults=10&q={query}&key={YOUTUBEAPI}')
    response = r.json()
    videoID = response["items"][0]["id"]["videoId"]
    videoTitle = response["items"][0]["snippet"]["title"]
    newlink = f"https://www.youtube.com/embed/{videoID}"
    print(newlink)
    print(videoTitle)
    return make_response(jsonify({
        "link": newlink,
        "title": urllib.parse.quote_plus(videoTitle)
    }), 200)

@app.route("/update/<query>")
def update(query):
    # search japanese lyrics result from uta-net (site with pretty much biggest collection of japanese lyrics)
    search = "site%3Auta-net.com+" + query
    line = f"https://www.google.com/search?q={search}"
    print(line)
    page = requests.get(line)
    soup = BeautifulSoup(page.text, "html.parser")
    links = soup.findAll("a")
    for link in links:
        link_href = link.get('href')
        if "url?q=" in link_href and not "webcache" in link_href:
            parsed = link.get('href').split("?q=")[1].split("&sa=U")[0]
            # return link that matches desired link pattern
            if re.match("https://www.uta-net.com/song", parsed) or re.match("https://www.uta-net.com/movie", parsed):
                print(parsed)
                original = scrap(parsed)
                return make_response(jsonify({"original": original, "translated": translate(original)}), 200)
            else:
                return make_response(jsonify({"original": "no lyrics found", "translated": "no lyrics translated"}), 200)

# scrap lyrics from uta-net.com
def scrap(url):
    page = requests.get(url)
    html = BeautifulSoup(page.text, 'html.parser')
    if re.match("https://www.uta-net.com/song/", url):
        lyrics = html.find('div', {"id": "kashi_area"}).get_text("\n")
    elif re.match("https://www.uta-net.com/movie/", url):
        lyrics = html.find('p', {"id": "flash_area"}).get_text("\n")
    else:
        print("no lyrics found")
        return
    print(lyrics)
    lyrics = lyrics.strip()
    return lyrics

# use kakao translate api to transalte japanese -> korean
def translate(lyrics):
    r = requests.get(f'https://kapi.kakao.com/v1/translation/translate', params={'query': lyrics, 'src_lang': 'jp', 'target_lang': 'kr'}, headers={'Authorization': f'KakaoAK {KAKAOAPI}'})
    response = r.json()
    lines = response["translated_text"]
    translated = []
    for line in lines:
        translated.append(*line)
    result = "\n".join(translated)
    print(result)
    return result

if __name__ == "__main__":
    app.run()
