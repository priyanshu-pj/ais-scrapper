import configparser
import requests
import json
import os, time
from flask import Flask, Response, request, jsonify

app = Flask(__name__)

@app.route('/', methods=['GET'])
def custom_hello():
    return Response("{RES-OK: 200}")

@app.route('/scrape', methods=['GET'])
def scrape():
    try:
        start_time = time.time()

        config = configparser.ConfigParser(interpolation=None)
        config.read('config.ini')

        category = request.args['category']
        if category == "wifi":
            day = request.args['day']
        else:
            day = f'day_{request.args["day"]}'

        token = request.args['token']
        if token != "ca849a200c0f73b5cf2855f479551cab":
            return Response("Incorrect Token")
        url = config[str(category)][str(day)]

        try:
            response = requests.get(url)
            raw_json = response.json()
            indented_json = json.dumps(raw_json, indent=4)
        except requests.exceptions.RequestException as e:
            return f"Error occured while sending request, STATUS_CODE:- {response.status_code}"

        try:
            with open('output.json', 'w') as file:
                file.write(indented_json)
        except FileExistsError as e:
            os.remove('output.json')
            with open('output.json', 'w') as file:
                file.write(indented_json)

        with open('output.json', 'r') as file:
            data = json.load(file)
            data_list = data['data']['products']['items']
            result = {
                "data": [],
                "size": len(data_list),
            }
            for item in data_list:
                name = item['name']
                price = item['price_exc_vat']
                duration = item['tariff_duration']
                code = item['ussd_code']
                url = 'https://www.ais.th/en/consumers/package/' + item['url_subdirectory_1'] + '/' + item['url_subdirectory_2']
                data_item = {
                    "name": name,
                    "amount": str(price),
                    "day": str(duration),
                    "number": code,
                    "apply_url": url,
                }

                result["data"].append(data_item)
        os.remove('output.json')

        end_time = time.time()
        print("Execution time:- ", end_time - start_time)

        return result

    except Exception as e:
        error_message = str(e)
        return jsonify({'error': error_message})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3000)
