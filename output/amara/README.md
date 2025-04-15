# amara Kong API Gateway Demo

This repository contains a pre-configured Kong API Gateway setup for demonstration purposes.

## Overview

This demo includes:

- Kong API Gateway with built-in Admin UI (Kong Manager)
- PostgreSQL database for Kong
- amara, aaaa, amama mock services with realistic endpoints

## Getting Started

### Prerequisites

- Docker and Docker Compose
- curl (for testing)

### Setup Instructions

1. Start the Kong demo environment:

```bash
./setup.sh
```

2. Access the Kong Admin API at http://localhost:8001
3. Access Kong Manager UI at http://localhost:8002

## Mock API Services

Each mock API service provides the following endpoints:

- `/health` - Returns health status of the service
- `/info` - Returns information about the service
- `/echo` - Echoes back the request details (method, headers, body, etc.)
- `/items` - A CRUD REST API for demo purposes (supports GET, POST, PUT, DELETE)

## API Routes

The following API routes have been configured:


- `/api/amara` - Routes to `amara` service

- `/api/vendre` - Routes to `aaaa` service

- `/api/inventory-management` - Routes to `amama` service


## Authentication







This demo does not use authentication.

Example request:
```bash
curl -i -X GET http://localhost:8000/api/amara
```


## Plugins Enabled


- http-log


## Testing the API

Run the test script to check all configured routes:

```bash
./test-api.sh
```

## Modifying the Mock APIs

If you need to modify the mock API behavior:

1. Edit the code in `mock-apis/[service-name]/server.js`
2. Rebuild and restart the containers:
```bash
docker-compose down
docker-compose up -d
```

## Cleanup

To stop and remove all containers:

```bash
docker-compose down -v
```