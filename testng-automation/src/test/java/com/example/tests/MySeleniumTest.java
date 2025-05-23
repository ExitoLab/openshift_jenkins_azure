package com.example.tests;

import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.chrome.ChromeOptions;
import org.openqa.selenium.edge.EdgeDriver;
import org.openqa.selenium.edge.EdgeOptions;
import org.testng.annotations.*;

public class MySeleniumTest {
    private WebDriver driver;

    private ChromeOptions getCommonChromeOptions() {
        ChromeOptions options = new ChromeOptions();
        options.addArguments("--headless");
        options.addArguments("--disable-gpu");
        options.addArguments("--no-sandbox");
        options.addArguments("--disable-dev-shm-usage");
        // options.addArguments("--remote-debugging-port=9222"); // REMOVE this line
        options.addArguments("--window-size=1920,1080");
        options.addArguments("--disable-extensions");
        options.addArguments("--disable-background-networking");
        options.addArguments("--disable-background-timer-throttling");
        options.addArguments("--disable-client-side-phishing-detection");
        options.addArguments("--disable-default-apps");
        options.addArguments("--disable-hang-monitor");
        options.addArguments("--disable-popup-blocking");
        options.addArguments("--disable-prompt-on-repost");
        options.addArguments("--disable-sync");
        options.addArguments("--metrics-recording-only");
        options.addArguments("--no-first-run");
        options.addArguments("--safebrowsing-disable-auto-update");
        options.addArguments("--enable-automation");
        options.addArguments("--password-store=basic");
        options.addArguments("--use-mock-keychain");
        options.addArguments("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36");
        options.addArguments("--lang=en-US");
        return options;
    }

    private EdgeOptions getCommonEdgeOptions() {
        EdgeOptions options = new EdgeOptions();
        options.addArguments("--headless");
        options.addArguments("--disable-gpu");
        options.addArguments("--no-sandbox");
        options.addArguments("--disable-dev-shm-usage");
        options.addArguments("--remote-debugging-port=9222");
        options.addArguments("--window-size=1920,1080");
        return options;
    }

    @Parameters({"browser", "screenshot-dir"})
    @BeforeMethod
    public void setUp(String browser, String screenshotDir) {
        if (browser == null) {
            throw new IllegalArgumentException("Browser parameter is required");
        }
        System.setProperty("webdriver.chrome.driver", "/usr/local/bin/chromedriver");
        System.setProperty("webdriver.edge.driver", "/usr/local/bin/msedgedriver");

        if (browser.equalsIgnoreCase("chrome")) {
            driver = new ChromeDriver(getCommonChromeOptions());
        } else if (browser.equalsIgnoreCase("edge")) {
            driver = new EdgeDriver(getCommonEdgeOptions());
        } else {
            throw new IllegalArgumentException("Unsupported browser: " + browser);
        }
        System.out.println("Screenshot directory: " + screenshotDir);
    }

    @Test
    public void testExample() {
        driver.get("https://example.com");
        // Add your test logic here
    }

    @AfterMethod
    public void tearDown() {
        if (driver != null) {
            driver.quit();
        }
    }

    // Getter for WebDriver
    public WebDriver getDriver() {
        return driver;
    }
}