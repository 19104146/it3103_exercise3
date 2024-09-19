# IT 3103 - Exercise 3

This project provides hands-on experience with microservice API design through a system managing **Products**, **Customers**, and **Orders** services.

## Prerequisites

Ensure the following are installed:

- [Docker](https://docs.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)

## Getting Started

1. **Clone the repository:**
   ```bash
   git clone https://github.com/19104146/it3103_exercise3.git
   ```
2. **Navigate to the project directory:**
   ```bash
   cd it3103_exercise3
   ```
3. **Start the services:**
   ```bash
   docker-compose up --build -d
   ```
   > **Services are accessible at:**
   >
   > - Product Service: [http://localhost:3001](http://localhost:3001)
   > - Customer Service: [http://localhost:3002](http://localhost:3002)
   > - Order Service: [http://localhost:3003](http://localhost:3003)
4. **Stop the services:**
   ```bash
   docker-compose down
   ```
