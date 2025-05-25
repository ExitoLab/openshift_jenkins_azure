# ====== BUILD STAGE ======
FROM maven:eclipse-temurin AS build

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget unzip curl git gnupg ca-certificates fonts-liberation \
    libnss3 libx11-xcb1 libxcomposite1 libxcursor1 libxdamage1 \
    libxrandr2 libasound2t64 libatk1.0-0 libatk-bridge2.0-0 \
    libgbm1 libgtk-3-0 libpango-1.0-0 libpangocairo-1.0-0 \
    libxss1 libxtst6 lsb-release xdg-utils xvfb \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for build and test stages
RUN groupadd -g 10000 selenium || true && \
    useradd -u 10000 -g 10000 -s /bin/bash -m selenium || true

# Copy local dependency files
COPY dependencies/google-chrome-stable_current_amd64.deb /tmp/google-chrome-stable_current_amd64.deb
COPY dependencies/chromedriver-linux64.zip /tmp/chromedriver-linux64.zip
COPY dependencies/microsoft-edge-stable_*_amd64.deb /tmp/microsoft-edge-stable_amd64.deb
COPY dependencies/edgedriver_linux64.zip /tmp/edgedriver_linux64.zip
COPY dependencies/selenium-java-4.20.0.zip /tmp/selenium.zip

# Install Google Chrome from local .deb file
RUN dpkg -i /tmp/google-chrome-stable_current_amd64.deb || apt-get update && apt-get install -y -f \
    && rm -f /tmp/google-chrome-stable_current_amd64.deb \
    && rm -rf /var/lib/apt/lists/*

# Install ChromeDriver from local zip file
RUN unzip /tmp/chromedriver-linux64.zip -d /tmp \
    && mv /tmp/chromedriver-linux64/chromedriver /usr/local/bin/ \
    && chmod +x /usr/local/bin/chromedriver \
    && chown selenium:selenium /usr/local/bin/chromedriver \
    && rm -rf /tmp/chromedriver-linux64.zip /tmp/chromedriver-linux64

# Install Microsoft Edge from local .deb file
RUN dpkg -i /tmp/microsoft-edge-stable_amd64.deb || apt-get update && apt-get install -y -f \
    && rm -f /tmp/microsoft-edge-stable_amd64.deb \
    && rm -rf /var/lib/apt/lists/*

# Install EdgeDriver from local zip file
RUN unzip /tmp/edgedriver_linux64.zip -d /tmp \
    && mv /tmp/msedgedriver /usr/local/bin/ \
    && chmod +x /usr/local/bin/msedgedriver \
    && chown selenium:selenium /usr/local/bin/msedgedriver \
    && rm -rf /tmp/edgedriver_linux64.zip

# Extract Selenium JARs
RUN unzip /tmp/selenium.zip -d /tmp/selenium \
    && mkdir -p /app/selenium \
    && cp /tmp/selenium/selenium-api-4.20.0.jar /app/selenium/ \
    && rm -rf /tmp/selenium /tmp/selenium.zip

# Build project
WORKDIR /app
COPY pom.xml .
RUN mvn dependency:go-offline -B
COPY src ./src
COPY testng.xml .
RUN mvn clean package -DskipTests -B
RUN chown -R selenium:selenium /app

# ====== TEST STAGE ======
FROM maven:eclipse-temurin

# Copy binaries and files from build stage
COPY --from=build /usr/local/bin/chromedriver /usr/local/bin/chromedriver
COPY --from=build /usr/local/bin/msedgedriver /usr/local/bin/msedgedriver
COPY --from=build /usr/bin/google-chrome /usr/bin/google-chrome
COPY --from=build /usr/bin/microsoft-edge /usr/bin/microsoft-edge
COPY --from=build /app/target /app/target
COPY --from=build /app/src /app/src
COPY --from=build /app/pom.xml /app/pom.xml
COPY --from=build /app/testng.xml /app/testng.xml
COPY --from=build /app/selenium /app/selenium

# Install minimal dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    fonts-liberation libnss3 libxss1 libatk-bridge2.0-0 libgtk-3-0 xvfb \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user before setting permissions
RUN groupadd -g 10000 selenium || true && \
    useradd -u 10000 -g 10000 -s /bin/bash -m selenium || true

# Set permissions
RUN chmod +x /usr/bin/google-chrome /usr/local/bin/chromedriver /usr/bin/microsoft-edge /usr/local/bin/msedgedriver
RUN chown selenium:selenium /usr/bin/google-chrome /usr/local/bin/chromedriver /usr/bin/microsoft-edge /usr/local/bin/msedgedriver

# Environment variables
ENV CHROME_BIN=/usr/bin/google-chrome
ENV EDGE_BIN=/usr/bin/microsoft-edge
ENV DISPLAY=:99

# Create output directory and set permissions
RUN mkdir -p /app/test-output/screenshots && \
    chown -R selenium:selenium /app

WORKDIR /app
USER selenium

COPY --chown=selenium:selenium entrypoint.sh /app/entrypoint.sh

RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]
