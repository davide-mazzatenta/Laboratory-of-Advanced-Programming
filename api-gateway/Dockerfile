# Stage 1: Build with Maven and Java 17
FROM maven:3.9.6-eclipse-temurin-17 AS build

WORKDIR /app

# Copy all project files (pom.xml + src) together
COPY . .

# Build the project, skipping tests
RUN mvn clean package -DskipTests

# Stage 2: Run the application with a slim JDK
FROM eclipse-temurin:17-jdk-alpine

WORKDIR /app

# Copy the built JAR from the build stage
COPY --from=build /app/target/*.jar app.jar

# Set environment variables
ENV SPRING_PROFILES_ACTIVE=dev

# Expose the port configured in application.yml
EXPOSE 8080

# Healthcheck aligned with application port
HEALTHCHECK --interval=30s --timeout=3s --start-period=30s --retries=3 \
  CMD wget --spider -q http://localhost:8080/api/health || exit 1

# Run the app
ENTRYPOINT ["java", "-jar", "app.jar"]