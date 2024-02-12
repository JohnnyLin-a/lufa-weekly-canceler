import os
import json
import requests
from urllib.parse import urlencode
from selenium import webdriver
from selenium.webdriver import FirefoxOptions
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from flask import Flask, jsonify
from flask_cors import CORS


class DeliveryTimeConfig:
    def __init__(self):
        self.username = ""
        self.password = ""
        self.user_id = ""

class DeliveryTimeAPIResult:
    def __init__(self, message, success):
        self.message = message
        self.success = success

class DeliveryTimeAPI:
    def __init__(self, config):
        self.config = config

    def execute(self, wd):
        execution_result = DeliveryTimeAPIResult("Initialized", False)


        # Define the payload
        payload = {
            "LoginForm[user_email]": self.config.username,
            "LoginForm[password]": self.config.password,
            "yt0": "Log in"
        }

        # URL encode the payload
        payload_encoded = urlencode(payload)

        # Send the POST request
        response = requests.post("https://montreal.lufa.com/en/login", data=payload_encoded)

        # Check if login was successful
        if response.status_code != 200:
            execution_result.message = "Login failed"
            return execution_result

        # Save the cookies
        cookies = response.cookies

        # Check if the cookie was set
        if 'lufaState' not in cookies:
            execution_result.message = "Did not login successfully, no cookie."
            return execution_result


        headers = {
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Cookie": f"lufaState={cookies['lufaState']}"
        }
        data = {"user_id": self.config.user_id}
        
        #Get order details for orderID
        response = requests.post("https://montreal.lufa.com/en/superMarket/GetUserOrderDetails", headers=headers, data=data)

        current_order_id = ""

        try:
            json_response = response.json()
            current_order_id = json_response["orderId"]
        except json.JSONDecodeError:
            execution_result.message = "Did not get back valid json from order data."
            return execution_result

         #Get ETA for orderID
        data = {"user_id": self.config.user_id, "order_id": current_order_id}
        response = requests.post("https://montreal.lufa.com/fr/orders/getTrackOrderData", headers=headers, data=data)

        current_eta = ""

        try:
            json_response = response.json()
            current_eta = json_response["eta"]
            execution_result.message = current_eta
            execution_result.success = True
        except json.JSONDecodeError:
            execution_result.message = "Did not get back valid json for eta."
            return execution_result     


        return execution_result

app = Flask(__name__)
CORS(app)

@app.route('/execute', methods=['GET'])

def execute():

    config_json_str = os.getenv("LUFA_DELIVERY_CONFIG")

    if config_json_str is None:
        try:
            with open("config.json") as f:
                config_json_str = f.read()
        except FileNotFoundError:
            print("Cannot find config.json, exiting application...")
            exit(1)    

    config = DeliveryTimeConfig()

    try:
        json_config = json.loads(config_json_str)
        config.username = json_config["username"]
        config.password = json_config["password"]
        config.user_id = json_config["user_id"]

    except json.JSONDecodeError:
        print("Cannot parse JSON properly, make sure the syntax is correct and object matches the template.")
        exit(1)


    api = DeliveryTimeAPI(config)

    options = FirefoxOptions()
    options.add_argument("--headless")
    wd = webdriver.Firefox(options=options)

    result = api.execute(wd)
    wd.close()
    print(f"Result: {result.success} Message: {result.message}")
    return jsonify({'success': result.success, 'message': result.message})



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=38570)


