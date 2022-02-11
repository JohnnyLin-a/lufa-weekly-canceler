package io.github.johnnylina.lufaweeklycanceler.CancelerAPI;

public class CancelerAPIResult {
    public String message;
    public boolean success;

    public CancelerAPIResult(String message, boolean success) {
        this.message = message;
        this.success = success;
    }
}