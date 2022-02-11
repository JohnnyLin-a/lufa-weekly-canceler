package io.github.johnnylina.lufaweeklycanceler.CancelerAPI;

import org.openqa.selenium.WebDriver;

import io.github.johnnylina.lufaweeklycanceler.CancelerConfig.CancelerConfig;

public class CancelerAPI {
    public CancelerConfig config;

    public CancelerAPI(CancelerConfig config) {
        this.config = config;
    }

    public CancelerAPIResult execute(WebDriver wd) {
        // Do main logic here

        // Login to Lufa

        // Then cancel basket.

        return new CancelerAPIResult("Execution not yet implemented", false);
    }
}
