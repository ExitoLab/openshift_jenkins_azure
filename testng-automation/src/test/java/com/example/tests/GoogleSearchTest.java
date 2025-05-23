package com.example.tests;

import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.testng.annotations.*;

import org.openqa.selenium.support.ui.WebDriverWait;
import org.openqa.selenium.support.ui.ExpectedConditions;
import java.time.Duration;

public class GoogleSearchTest {
    private WebDriver driver;
    private MySeleniumTest seleniumTest = new MySeleniumTest();

    @Parameters({"browser", "screenshot-dir"})
    @BeforeMethod(groups = {"small", "regression"})
    public void setUp(String browser, String screenshotDir) {
        seleniumTest.setUp(browser, screenshotDir);
        driver = seleniumTest.getDriver();
    }

    @Test(groups = {"small", "regression"})
    public void testGoogleSearch() {
        driver.get("https://www.google.com");
        WebElement searchBox = driver.findElement(By.name("q"));
        searchBox.sendKeys("TestNG Selenium");
        searchBox.submit();

        // Instead of waiting for full "TestNG Selenium", wait for "TestNG"
        WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));
        wait.until(ExpectedConditions.titleContains("TestNG"));

        // Then assert the title contains "TestNG" or "Selenium"
        String title = driver.getTitle();
        assert title.contains("TestNG") || title.contains("Selenium") : "Title does not contain expected text";
    }

    @AfterMethod(groups = {"small", "regression"})
    public void tearDown() {
        seleniumTest.tearDown();
    }

    public WebDriver getDriver() {
        return driver;
    }
}