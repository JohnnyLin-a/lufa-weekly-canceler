package io.github.johnnylina.lufaweeklycanceler;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.util.Scanner;

import org.json.JSONException;
import org.json.JSONObject;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.firefox.FirefoxDriver;
import org.openqa.selenium.firefox.FirefoxOptions;

import io.github.johnnylina.lufaweeklycanceler.CancelerAPI.CancelerAPI;
import io.github.johnnylina.lufaweeklycanceler.CancelerAPI.CancelerAPIResult;
import io.github.johnnylina.lufaweeklycanceler.CancelerConfig.CancelerConfig;

public class LufaWeeklyCancelerMain {
    public static void main(String []args) throws Exception {
        // Load config
        String configJsonStr = System.getenv("LUFA_CANCELER_CONFIG");

        // Load config.json instead if ENV_VAR is null
        if (configJsonStr == null) {
            try (Scanner scanner = new Scanner(new File("config.json"))) {
                configJsonStr = "";
                while (scanner.hasNextLine()) {
                    configJsonStr += scanner.nextLine();
                }
            } catch (FileNotFoundException fnfe) {
                // Exit application because there is no config in ENV_VAR and in config.json
                System.out.println("Cannot find config.json, exiting application...");
                System.exit(1);
            }
        }

        // Parse config
        CancelerConfig config = new CancelerConfig();

        try {
            JSONObject jsonConfig = new JSONObject(configJsonStr);
            config.username = jsonConfig.getString("username");
            config.password = jsonConfig.getString("password");
            config.debug = jsonConfig.getBoolean("debug");
            config.webhook = jsonConfig.getString("webhook");
            config.mention = jsonConfig.getString("mention");
        } catch (JSONException jsone) {
            System.out.println("Cannot parse JSON properly, make sure the syntax is correct and object matches the template.");
            System.exit(1);
        }

        // Create new API
        CancelerAPI api = new CancelerAPI(config);

        // Create new WebDriver instance
        FirefoxOptions options = new FirefoxOptions();
        options.setHeadless(!config.debug);
        WebDriver wd = new FirefoxDriver();

        // Execute
        CancelerAPIResult result = api.execute(wd);
        wd.close();

        // Notify Discord server's channel via webhook POST request
        // Optional step so don't crash execution if webhook is not set
        if (config.webhook == "") {
            System.exit(0);
        }

        String discordMsg = config.mention + " Success: " + result.success + " " + result.message;

        HttpClient client = HttpClient.newHttpClient();
        HttpRequest request = HttpRequest.newBuilder()
            .uri(URI.create(config.webhook))
            .header("Content-Type", "application/json")
            .POST(HttpRequest.BodyPublishers.ofString("{\"content\":\"" + discordMsg + "\"}"))
            .build();
        try {
            client.send(request, HttpResponse.BodyHandlers.ofString());
        } catch (IOException | InterruptedException e) {
            // Failed to send http request, do nothing
            // I mean, what else is there to do? lol
        }
    }
}