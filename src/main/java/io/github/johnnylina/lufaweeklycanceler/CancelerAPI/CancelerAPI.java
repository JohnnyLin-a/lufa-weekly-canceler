package io.github.johnnylina.lufaweeklycanceler.CancelerAPI;

import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import java.util.ArrayList;
import java.util.List;
import java.util.NoSuchElementException;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;
import org.openqa.selenium.By;
import org.openqa.selenium.Cookie;
import org.openqa.selenium.StaleElementReferenceException;
import org.openqa.selenium.TimeoutException;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;

import io.github.johnnylina.lufaweeklycanceler.CancelerConfig.CancelerConfig;

public class CancelerAPI {
    public CancelerConfig config;

    public CancelerAPI(CancelerConfig config) {
        this.config = config;
    }

    public CancelerAPIResult execute(WebDriver wd) {
        CancelerAPIResult executionResult = new CancelerAPIResult("Initialized", false);

        // Do main logic here
        wd.get("https://montreal.lufa.com/en/login");

        // Login to Lufa
        try {
            // email field
            WebElement e = wd.findElement(By.cssSelector("#LoginForm_user_email"));
            e.sendKeys(this.config.username);
        } catch (NoSuchElementException ex) {
            executionResult.message = "Cannot find login form: username field";
            return executionResult;
        }

        try {
            // password field
            WebElement e = wd.findElement(By.cssSelector("#LoginForm_password"));
            e.sendKeys(this.config.password);
        } catch (NoSuchElementException ex) {
            executionResult.message = "Cannot find login form: password field";
            return executionResult;
        }

        try {
            // login button
            WebElement e = wd.findElement(By.cssSelector("input[value=\"Log in\"]"));
            e.click();
        } catch (NoSuchElementException ex) {
            executionResult.message = "Cannot find login form: login button";
            return executionResult;
        } catch (StaleElementReferenceException ex) {
            executionResult.message = "Cannot click login button";
            return executionResult;
        }

        try {
            new WebDriverWait(wd, Duration.ofSeconds(20)).until(
                ExpectedConditions.urlContains("montreal.lufa.com/en/marketplace")
            );
        } catch (TimeoutException ex) {
            executionResult.message = "Did not redirect to marketplace after login";
            return executionResult;
        }


        // Get dates to cancel basket(s)
        Cookie lufaState = wd.manage().getCookieNamed("lufaState");
        if (lufaState == null) {
            executionResult.message = "Did not login successfully, no cookie.";
            return executionResult;
        }
        HttpClient client = HttpClient.newHttpClient();
        HttpRequest request = HttpRequest.newBuilder()
            .uri(URI.create("https://montreal.lufa.com/en/users/deliveryData"))
            .header("Content-Type", "application/x-www-form-urlencoded; charset=UTF-8")
            .header("Cookie", lufaState.getName() + "=" + lufaState.getValue())
            .POST(HttpRequest.BodyPublishers.ofString("user_id=" + this.config.user_id))
            .build();

        List<String> weeksToSkip = new ArrayList<>();

        try {
            HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());
            JSONObject jsonResponse = new JSONObject(response.body());
            JSONArray futureDeliveries = jsonResponse.getJSONObject("data").getJSONArray("future_delivery_days");
            for (int i = 0; i < futureDeliveries.length(); i++) {
                JSONObject day = futureDeliveries.getJSONObject(i);
                if (!day.getBoolean("suspended")) {
                    weeksToSkip.add(day.getString("date"));
                }
            }
        } catch (IOException | InterruptedException e) {
            executionResult.message = "Did not get delivery data successfully.";
            return executionResult;
        } catch (JSONException ex) {
            executionResult.message = "Did not get back valid json from delivery data.";
            return executionResult;
        }

        // Cancel basket(s)
        List<String> failedWeeks = new ArrayList<>();
        weeksToSkip.forEach(week -> {
            try {
                Thread.sleep(5000);
                HttpRequest req = HttpRequest.newBuilder()
                    .uri(URI.create("https://montreal.lufa.com/en/users/addVacation"))
                    .header("Content-Type", "application/x-www-form-urlencoded; charset=UTF-8")
                    .header("Cookie", lufaState.getName() + "=" + lufaState.getValue())
                    .POST(HttpRequest.BodyPublishers.ofString("user_id=" + this.config.user_id  + "&startDate=" + week + "&endDate=" + week + "&short_pause=true&vacation_id=&original_long_pause="))
                    .build();
                HttpResponse<String> response = client.send(req, HttpResponse.BodyHandlers.ofString());
                JSONObject respObj = new JSONObject(response.body());
                if (!respObj.getBoolean("success")) {
                    throw new Exception("success = false");
                }
            } catch (JSONException ex) {
                System.out.println(ex.getMessage());
                failedWeeks.add(week);
            } catch (Exception e) {
                failedWeeks.add(week);
            }
        });

        if (failedWeeks.size() != 0) {
            executionResult.message = "There are failed weeks:";
            failedWeeks.forEach(failedWeek -> {
                executionResult.message += " " + failedWeek;
            });
            return executionResult;
        }

        executionResult.message = "Done:";
        weeksToSkip.forEach(week -> {
            executionResult.message += " " + week;
        });
        executionResult.success = true;
        return executionResult;
    }
}
