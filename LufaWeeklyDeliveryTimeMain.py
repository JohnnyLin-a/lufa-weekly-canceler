import os
import json
import requests
from datetime import datetime
from time import strptime
from selenium import webdriver
from selenium.webdriver import FirefoxOptions
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from flask import Flask, jsonify, request
from flask_cors import CORS


class DeliveryTimeConfig:
    def __init__(self):
        self.username = ""
        self.password = ""
        self.user_id = ""
        self.language = "en"  # default language is English

    def get_url(self, endpoint=""):
        return f"https://montreal.lufa.com/{self.language}/{endpoint}"

class DeliveryTimeAPIResult:    
    def __init__(self):
        self.message = ""
        self.success = False
        self.orderDate = None
        self.orderTotal = 0.0
        self.deliveryTime = None
        self.numberBoxNeeded = 0
        self.stopsBefore = 0
        self.deliveryToday = False
        

class DeliveryTimeAPI:
    def __init__(self, config):
        self.config = config

    def execute(self, wd):
        execution_result = DeliveryTimeAPIResult()

        # Do main logic here
        wd.get(self.config.get_url("login"))

        # Login to Lufa
        try:
            # email field
            e = wd.find_element(By.CSS_SELECTOR, "#LoginForm_user_email")
            e.send_keys(self.config.username)
        except NoSuchElementException:
            execution_result.message = "Cannot find login form: username field"
            return execution_result

        try:
            # password field
            e = wd.find_element(By.CSS_SELECTOR, "#LoginForm_password")
            e.send_keys(self.config.password)
        except NoSuchElementException:
            execution_result.message = "Cannot find login form: password field"
            return execution_result

        try:
            # login button
            e = wd.find_element(By.CSS_SELECTOR, "input[value=\"Log in\"]")
            e.click()
        except NoSuchElementException:
            execution_result.message = "Cannot find login form: login button"
            return execution_result

        try:
            WebDriverWait(wd, 20).until(
                EC.url_contains("/marketplace")
            )
        except TimeoutException:
            execution_result.message = "Did not redirect to marketplace after login"
            return execution_result
        
        lufa_state = wd.get_cookie("lufaState")
        if lufa_state is None:
            execution_result.message = "Did not login successfully, no cookie."
            return execution_result

        headers = {
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Cookie": f"{lufa_state['name']}={lufa_state['value']}"
        }
        data = {"user_id": self.config.user_id}
        
        response = requests.post(self.config.get_url("superMarket/GetUserOrderDetails"), headers=headers, data=data)

        current_order_id = ""

        try:
            json_response = response.json()
            current_order_id = json_response["orderId"]
            order_date_str = json_response["orderDate"]
            order_date = datetime.strptime(order_date_str, "%A, %B %dth, %Y")
            execution_result.orderDate = order_date.isoformat()
            execution_result.orderTotal = json_response["checkoutAmounts"]["unformatted_total"]
        except json.JSONDecodeError:
            execution_result.message = "Did not get back valid json from order data from GetUserOrderDetails"
            return execution_result

        data = {"user_id": self.config.user_id, "order_id": current_order_id}
        response = requests.post(self.config.get_url("orders/getTrackOrderData"), headers=headers, data=data)

        # Check if the request was successful
        if response.status_code != 200:
            execution_result.message = "getTrackOrderData request failed / no delivery today."
            execution_result.deliveryToday = False
            execution_result.success = True
            return execution_result

        try:
            json_response = response.json()
            eta_time_str = json_response.get("eta")
            if eta_time_str:
                # Parse the time string
                eta_time = strptime(eta_time_str, "%H:%M")

                # Get today's date
                today = datetime.today()

                # Combine today's date with the ETA time
                eta_datetime = datetime(today.year, today.month, today.day, eta_time.tm_hour, eta_time.tm_min)

                # Convert to timestamp
                execution_result.deliveryTime = eta_datetime.isoformat()
            execution_result.number_box_needed = json_response.get("number_box_needed")
            execution_result.stops_before = json_response.get("stops_before")
            execution_result.success = True
            execution_result.deliveryToday = True
        except json.JSONDecodeError:
            execution_result.message = "Did not get back valid json for eta from getTrackOrderData"
            return execution_result  

        return execution_result

app = Flask(__name__)
CORS(app)

@app.route('/execute', methods=['POST'])
def execute():
    config = DeliveryTimeConfig()

    data = request.get_json()

    config.username = data.get('username')
    config.password = data.get('password')
    config.user_id = data.get('user_id')
    config.language = data.get('language', 'en')  # default to English if not specified

    # Check if required parameters are provided
    if not config.username or not config.password or not config.user_id:
        return jsonify({
            'message': "Error in the execution of the script. Missing required parameters.",
            'success': False,
        })

    api = DeliveryTimeAPI(config)

    options = FirefoxOptions()
    options.add_argument("--headless")
    wd = webdriver.Firefox(options=options)

    try:
        result = api.execute(wd)
    except Exception as e:
        return jsonify({
            'message': "Error in the execution of the script.",
            'success': False,
        })
    finally:
        wd.close()

    return jsonify({
        'message': result.message,
        'success': result.success,
        'orderDate': result.orderDate,
        'orderTotal': result.orderTotal,
        'deliveryTime': result.deliveryTime,
        'numberBoxNeeded': result.numberBoxNeeded,
        'stopsBefore': result.stopsBefore,
        'deliveryToday': result.deliveryToday 
    })



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=38570)

