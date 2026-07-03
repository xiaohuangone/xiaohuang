FROM openjdk:17-jdk-slim

WORKDIR /app

COPY back/pom.xml .
COPY back/src ./src

RUN apt-get update && apt-get install -y maven && rm -rf /var/lib/apt/lists/*

RUN mvn clean package -DskipTests

EXPOSE 8080

CMD ["java", "-jar", "target/web-1.0.0-SNAPSHOT.jar"]
