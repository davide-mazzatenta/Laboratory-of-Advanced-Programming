# ===== Build =====
FROM maven:3.9.6-eclipse-temurin-17 AS build
WORKDIR /proj

# POM
COPY pom.xml .
RUN mvn -q -DskipTests dependency:go-offline

# Sorgenti: copia i .java piatti nella cartella del package
RUN mkdir -p src/main/java/com/lexygraph/wrapper
COPY ./*.java src/main/java/com/lexygraph/wrapper/

# Compila il jar
RUN mvn -q -DskipTests package

# ===== Runtime =====
FROM eclipse-temurin:17-jre-alpine
WORKDIR /app

# 👇 aggiungi curl per l'healthcheck
RUN apk add --no-cache curl

COPY --from=build /proj/target/*.jar /app/app.jar

ENV WRAPPER_PORT=8010 \
    REQUEST_TIMEOUT_SECONDS=60 \
    RETRY_ATTEMPTS=1 \
    ALLOWED_ORIGINS=*

EXPOSE 8010

# 👇 healthcheck con curl, puntando alla tua /health
HEALTHCHECK --interval=15s --timeout=5s --retries=5 \
  CMD curl -fsS "http://localhost:${WRAPPER_PORT:-8010}/health" || exit 1

ENTRYPOINT ["java","-jar","/app/app.jar"]