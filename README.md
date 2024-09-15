# IT 3103 - Exercise 3

This exercise project aims to provide experience with microservice API design by implementing a simple system of intercommunicating services. The system will manage **Products**, **Customers**, and **Orders** services.

## Prerequisites

Before running the project, make sure you have the following installed:

- Docker
- Docker Compose

## Run Locally

1. **Clone the project:**
   ```
   git clone https://github.com/19104146/it3103_exercise3.git
   ```
2. **Go to the project directory:**
   ```
   cd it3103_exercise3
   ```
3. **Run the project:**
   ```
   docker-compose up -d
   ```
   > Note: The command above will expose ports corresponding to each service:
   >
   > - http://localhost:3001 - Product Service
   > - http://localhost:3002 - Customer Service
   > - http://localhost:3003 - Order Service
