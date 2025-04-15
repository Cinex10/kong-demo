#!/bin/bash

# Setup script for api-test Kong Demo

echo "Starting Kong API Gateway demo for api-test..."
docker-compose up -d

echo "Waiting for Kong to start..."
attempt=0
max_attempts=30
until curl -s http://localhost:8001 > /dev/null; do
  attempt=$((attempt+1))
  if [ $attempt -gt $max_attempts ]; then
    echo "Kong did not start after $max_attempts attempts. Please check docker logs."
    docker-compose logs kong
    exit 1
  fi
  echo "Attempt $attempt/$max_attempts: Waiting for Kong API to be ready..." 
  sleep 5
done

echo "Kong is available. Configuring services..."

# First validate configuration
echo "Validating configuration..."
VALID_SERVICES=()


# Create amar service
if [ -z "amar" ]; then
  echo "⚠️ Warning: Skipping service with empty name"
  continue
fi

echo "Creating service: amar"
curl -s -X POST http://localhost:8001/services \
  -d name=amar \
  -d url=http://amar:8080 > /dev/null

if [ $? -eq 0 ]; then
  VALID_SERVICES+=(amar)
fi



# Create route for amar
if [ -z "amar" ]; then
  echo "⚠️ Warning: Skipping route 'amar-route-1' with empty service name"
  continue
fi

# Check if service exists
SERVICE_EXISTS=false
for svc in "${VALID_SERVICES[@]}"; do
  if [ "$svc" == "amar" ]; then
    SERVICE_EXISTS=true
    break
  fi
done

if [ "$SERVICE_EXISTS" = false ]; then
  echo "⚠️ Warning: Service 'amar' does not exist, cannot create route 'amar-route-1'"
  continue
fi

echo "Creating route: amar-route-1"
curl -s -X POST http://localhost:8001/services/amar/routes \
  -d "paths[]=/api/users" \
  -d name=amar-route-1 > /dev/null







echo "============================================================"
echo "Kong API Gateway demo for api-test is ready!"
echo "============================================================"
echo "Kong Admin API: http://localhost:8001"
echo "Kong Manager (Admin UI): http://localhost:8002"
echo "Kong Proxy: http://localhost:8000"
echo ""
echo "Available API routes:"

echo "- http://localhost:8000/api/users"

echo ""
echo "To test the configured routes, run:"
echo "./test-api.sh"