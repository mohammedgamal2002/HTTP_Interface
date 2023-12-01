# webapp.py
import json

from functools import cached_property
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qsl, urlparse

import firebase_admin
from firebase_admin import db, credentials

class WebRequestHandler(BaseHTTPRequestHandler):

    @cached_property
    def url(self):
        return urlparse(self.path)

    @cached_property
    def query_data(self):
        return dict(parse_qsl(self.url.query))

    @cached_property
    def post_data(self):
        content_length = int(self.headers.get("Content-Length", 0))
        return self.rfile.read(content_length)

    @cached_property
    def form_data(self):
        return dict(parse_qsl(self.post_data.decode("utf-8")))

    @cached_property
    def cookies(self):
        return SimpleCookie(self.headers.get("Cookie"))

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(self.get_response().encode("utf-8"))

    def do_POST(self):
        self.do_GET()

        return json.dumps({
            "State": "Measurments Recieved",
        })
    
    def get_response(self, direction = "null"):
        return json.dumps(
            {
                "path": self.url.path,
                "query_data": self.query_data,
                "post_data": self.post_data.decode("utf-8"),
                "form_data": self.form_data,
                "cookies": {
                    name: cookie.value
                    for name, cookie in self.cookies.items()
                },
            }
        )

class MeasurementsManager(WebRequestHandler):
    cred = credentials.Certificate("Communication interface\Firebase_interface\\firebase_files\serviceAccountKey.json")
    firebase_admin.initialize_app(cred, {"databaseURL": "https://homebase-d10c7-default-rtdb.firebaseio.com/"})
    def do_POST(self):
        WebRequestHandler.do_POST(self)
        speed, distance = self.read_measurements()
        self.speed = speed
        self.distance = distance
        self.update_measurements(speed, distance)
        return json.dumps({
            "State": "Measurments Recieved",
        })
        
    def read_measurements(self):
        print(self.form_data)
        speed = None
        distance = None
        if "speed" in self.form_data:
            speed = self.form_data.get("speed")
            print(f'speed = {speed}')
        if "distance" in self.form_data:
            distance = self.form_data.get("distance")
            print(f'distance = {distance}')
        return speed, distance

    def update_measurements(self,speed,distance):
        db.reference("/").update({"speed":speed})
        db.reference("/").update({"distance":distance})



if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", 2156), MeasurementsManager)
    server.serve_forever()