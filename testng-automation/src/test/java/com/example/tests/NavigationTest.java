package com.example.tests;

import org.openqa.selenium.By; // Added
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.chrome.ChromeOptions;
import org.openqa.selenium.edge.EdgeDriver;
import org.openqa.selenium.edge.EdgeOptions;
import org.testng.annotations.AfterMethod;
import org.testng.annotations.BeforeMethod;
import org.testng.annotations.Test;

public class NavigationTest {
    private WebDriver driver;

    @BeforeMethod(groups = {"regression"})
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

    @Test(groups = {"regression"})
    public void testGoogleHomePageTitle() {
        driver.get("https://www.google.com");
        String title = driver.getTitle();
        assert title.equals("Google") : "Home page title is not 'Google'";
    }

    @Test(groups = {"regression"})
    public void testGoogleImagesNavigation() {
        driver.get("https://www.google.com");
        driver.findElement(By.linkText("Images")).click();
        String title = driver.getTitle();
        assert title.contains("Images") : "Images page title does not contain 'Images'";
    }

    @AfterMethod(groups = {"regression"})
    public void tearDown() {
        if (driver != null) {
            driver.quit();
        }
    }
}