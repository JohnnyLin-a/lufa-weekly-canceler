package io.github.johnnylina.lufaweeklycanceler.CancelerAPI;

public class CancelerAPIResult {
    public String error;
    public boolean success;

    public CancelerAPIResult(String error, boolean success) {
        this.error = error;
        this.success = success;
    }
}