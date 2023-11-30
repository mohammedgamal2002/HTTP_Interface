from http.server import HTTPServer
import WebRequestHandler

if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", 2156), WebRequestHandler)
    server.serve_forever()