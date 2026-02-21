logo: str = """

SSSSSSSSSSSSSSSSSSSSSSSSSSSSSS       WWWWWWWW                    WWWWWWWW       SSSSSSSSSSSSSSSSSSSSSSSSSSSSSS
SSSSSSSSSSSSSSSSSSSSSSSSSSSSSS       WWWWWWWW                    WWWWWWWW       SSSSSSSSSSSSSSSSSSSSSSSSSSSSSS
SSSSSSSSSSSSSSSSSSSSSSSSSSSSSS       WWWWWWWW                    WWWWWWWW       SSSSSSSSSSSSSSSSSSSSSSSSSSSSSS
SSSSSSSS                             WWWWWWWW                    WWWWWWWW       SSSSSSSS
SSSSSSSS                             WWWWWWWW                    WWWWWWWW       SSSSSSSS
SSSSSSSS                             WWWWWWWW                    WWWWWWWW       SSSSSSSS
SSSSSSSS                             WWWWWWWW                    WWWWWWWW       SSSSSSSS
SSSSSSSS                             WWWWWWWW                    WWWWWWWW       SSSSSSSS
SSSSSSSSSSSSSSSSSSSSSSSSSSSSSS       WWWWWWWW      WWWWWWWW      WWWWWWWW       SSSSSSSSSSSSSSSSSSSSSSSSSSSSSS
SSSSSSSSSSSSSSSSSSSSSSSSSSSSSS       WWWWWWWW      WWWWWWWW      WWWWWWWW       SSSSSSSSSSSSSSSSSSSSSSSSSSSSSS
SSSSSSSSSSSSSSSSSSSSSSSSSSSSSS       WWWWWWWW      WWWWWWWW      WWWWWWWW       SSSSSSSSSSSSSSSSSSSSSSSSSSSSSS
                      SSSSSSSS       WWWWWWWW      WWWWWWWW      WWWWWWWW                             SSSSSSSS
                      SSSSSSSS       WWWWWWWW      WWWWWWWW      WWWWWWWW                             SSSSSSSS
                      SSSSSSSS       WWWWWWWW      WWWWWWWW      WWWWWWWW                             SSSSSSSS
                      SSSSSSSS       WWWWWWWW      WWWWWWWW      WWWWWWWW                             SSSSSSSS
                      SSSSSSSS       WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW                             SSSSSSSS
SSSSSSSSSSSSSSSSSSSSSSSSSSSSSS       WWWWWWWWWWWWWWWWW  WWWWWWWWWWWWWWWWW       SSSSSSSSSSSSSSSSSSSSSSSSSSSSSS
SSSSSSSSSSSSSSSSSSSSSSSSSSSSSS       WWWWWWWWWWWWWWWW    WWWWWWWWWWWWWWWW       SSSSSSSSSSSSSSSSSSSSSSSSSSSSSS
SSSSSSSSSSSSSSSSSSSSSSSSSSSSSS       WWWWWWWWWWWWWWW      WWWWWWWWWWWWWWW       SSSSSSSSSSSSSSSSSSSSSSSSSSSSSS

==============================================================================================================

SSSSSSSSSSSS   EEEEEEEEEEEE   RRRRRRRRR      VVV         VVV   EEEEEEEEEEEE   RRRRRRRRR
SSSSSSSSSSSS   EEEEEEEEEEEE   RRRRRRRRR      VVV         VVV   EEEEEEEEEEEE   RRRRRRRRR
SSS            EEE            RRR      RRR   VVV         VVV   EEE            RRR      RRR
SSS            EEE            RRR      RRR   VVV         VVV   EEE            RRR      RRR
SSS            EEE            RRR      RRR   VVV         VVV   EEE            RRR      RRR
SSSSSSSSSSSS   EEEEEEEEEEEE   RRRRRRRRR      VVV         VVV   EEEEEEEEEEEE   RRRRRRRRR
SSSSSSSSSSSS   EEEEEEEEEEEE   RRRRRRRRR       VVV       VVV    EEEEEEEEEEEE   RRRRRRRRR
         SSS   EEE            RRRRRR           VVV     VVV     EEE            RRRRRR
         SSS   EEE            RRR   RRR         VVV   VVV      EEE            RRR   RRR
         SSS   EEE            RRR     RRR        VVV VVV       EEE            RRR     RRR
SSSSSSSSSSSS   EEEEEEEEEEEE   RRR      RRR        VVVVV        EEEEEEEEEEEE   RRR      RRR
SSSSSSSSSSSS   EEEEEEEEEEEE   RRR      RRR         VVV         EEEEEEEEEEEE   RRR      RRR

==============================================================================================================

"""

line: str = "\n==============================================================================================================\n"

# Imports dependencias

from flask import Flask, request
from SmartWebSearch import SmartWebSearch, InvalidKeyError
import socket

# Setup Flask
app = Flask(__name__)
is_searching = False

# Routes
@app.route('/search', methods=['POST'])
def search():
    global is_searching

    # Check if the request is JSON
    if request.headers.get("Content-Type") != "application/json":
        return {"error": "Content-Type must be application/json"}, 400
    
    # Check if a search is already in progress
    if is_searching:
        return {"error": "Search in progress"}, 400

    # Get the request body
    body = request.json

    # Check if the request body is valid
    if not (body.get("ts_key") and body.get("ds_key") and body.get("prompt")):
        return {"error": "Missing required parameters"}, 400
    
    ts_key = body.get("ts_key")
    ds_key = body.get("ds_key")
    prompt = body.get("prompt")

    # Try to search
    try:
        sws = SmartWebSearch(ts_key, ds_key)
        is_searching = True
        summary = sws.search(prompt)
    except InvalidKeyError as e:
        return {"error": str(e)}, 401
    except Exception as e:
        return {"error": str(e)}, 500
    finally:
        is_searching = False

    is_searching = False
    return {"summary": summary}

@app.route('/deepsearch', methods=['POST'])
def deepsearch():
    global is_searching

    # Check if the request is JSON
    if request.headers.get("Content-Type") != "application/json":
        return {"error": "Content-Type must be application/json"}, 400

    # Check if a search is already in progress
    if is_searching:
        return {"error": "Search in progress"}, 400

    # Get the request body
    body = request.json
    
    # Check if the request body is valid
    if not (body.get("ts_key") and body.get("ds_key") and body.get("prompt")):
        return {"error": "Missing required parameters"}, 400
    
    ts_key = body.get("ts_key")
    ds_key = body.get("ds_key")
    prompt = body.get("prompt")

    # Try to search
    try:
        sws = SmartWebSearch(ts_key, ds_key)
        is_searching = True
        summary = sws.deepsearch(prompt)
    except InvalidKeyError as e:
        return {"error": str(e)}, 401
    except Exception as e:
        return {"error": str(e)}, 500
    finally:
        is_searching = False

    is_searching = False
    return {"summary": summary}

# Start the server
if __name__ == '__main__':
    # Print the logo
    print(logo)

    # Print the server name and version
    print("SmartWebSearch Server Version 1.0.0\n\n" + line)

    # Print the welcome message
    print("Welcome to SmartWebSearch Server!!!\n" + line)

    print(f"Server started on 'http://{socket.gethostbyname(socket.gethostname())}:5000'\n" + line)
    app.run(host='0.0.0.0', port=5000)