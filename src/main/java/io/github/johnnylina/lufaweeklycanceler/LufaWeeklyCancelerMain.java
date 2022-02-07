package io.github.johnnylina.lufaweeklycanceler;

import java.io.File;
import java.io.FileNotFoundException;
import java.util.Scanner;

import org.json.JSONException;
import org.json.JSONObject;

import io.github.johnnylina.lufaweeklycanceler.CancelerConfig.CancelerConfig;

public class LufaWeeklyCancelerMain {
    public static void main(String []args) {
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
        } catch (JSONException jsone) {
            System.out.println("Cannot parse JSON properly, make sure the syntax is correct and object matches the template.");
            System.exit(1);
        }

        System.out.println(config.username + " " + config.password);
    }
}