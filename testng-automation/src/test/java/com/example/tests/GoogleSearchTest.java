package com.example.tests;

import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.chrome.ChromeOptions;
import org.openqa.selenium.edge.EdgeDriver;
import org.openqa.selenium.edge.EdgeOptions;
import org.testng.annotations.AfterMethod;
import org.testng.annotations.BeforeMethod;
import org.testng.annotations.Test;
import org.openqa.selenium.By;
import org.openqa.selenium.WebElement;

public class GoogleSearchTest {
    private WebDriver driver;

    @BeforeMethod(groups = {"small", "regression"})
    public void setUp() {
        String browser = System.getProperty("browser", "chrome");
        if ("edge".equalsIgnoreCase(browser)) {
            EdgeOptions options = new EdgeOptions();
            options.addArguments("--headless", "--disable-gpu");
            driver = new EdgeDriver(options);
        } else {
            ChromeOptions options = new ChromeOptions();
            options.addArguments("--headless", "--disable-gpu");
            driver = new ChromeDriver(options);
        }
        driver.manage().window().maximize();
    }

    @Test(groups = {"small", "regression"})
    public void testGoogleSearch() {
        driver.get("https://www.google.com");
        WebElement searchBox = driver.findElement(By.name("q"));
        searchBox.sendKeys("TestNG Selenium");
        searchBox.submit();
        String title = driver.getTitle();
        assert title.contains("TestNG Selenium") : "Search results page title does not contain 'TestNG Selenium'";
    }

    @AfterMethod(groups = {"small", "regression"})
    public void tearDown() {
        if (driver != null) {
            driver.quit();
        }
    }
}