import os
import json
import requests
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
        self.debug = False

class DeliveryTimeAPIResult:
    def __init__(self, message, success):
        self.message = message
        self.success = success

class DeliveryTimeAPI:
    def __init__(self, config):
        self.config = config

    def execute(self, wd):
        execution_result = DeliveryTimeAPIResult("Initialized", False)

        # Do main logic here
        wd.get("https://montreal.lufa.com/en/login")

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
                EC.url_contains("montreal.lufa.com/en/marketplace")
            )
        except TimeoutException:
            execution_result.message = "Did not redirect to marketplace after login"
            return execution_result
        
        lufa_state = wd.get_cookie('lufaState')
        if lufa_state is None:
            execution_result.message = "Did not login successfully, no cookie."
            return execution_result

        # Get notebox-countdown text
        try:
            WebDriverWait(wd, 30).until(
                EC.presence_of_element_located((By.CLASS_NAME, "notebox-eta"))
            )
            notebox_eta = wd.find_element(By.CLASS_NAME, "notebox-eta")
            notebox_eta_text = notebox_eta.text
            execution_result.message = notebox_eta_text
            execution_result.success = True
        except NoSuchElementException:
            execution_result.message = "Cannot find ETA"
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
        config.debug = json_config["debug"]

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


