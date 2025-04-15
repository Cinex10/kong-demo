#!/bin/bash

# Setup script for amara Kong Demo

echo "Starting Kong API Gateway demo for amara..."
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


# Create amara service
if [ -z "amara" ]; then
  echo "⚠️ Warning: Skipping service with empty name"
  continue
fi

echo "Creating service: amara"
curl -s -X POST http://localhost:8001/services \
  -d name=amara \
  -d url=http://amara:8080 > /dev/null

if [ $? -eq 0 ]; then
  VALID_SERVICES+=(amara)
fi

# Create aaaa service
if [ -z "aaaa" ]; then
  echo "⚠️ Warning: Skipping service with empty name"
  continue
fi

echo "Creating service: aaaa"
curl -s -X POST http://localhost:8001/services \
  -d name=aaaa \
  -d url=http://aaaa:8080 > /dev/null

if [ $? -eq 0 ]; then
  VALID_SERVICES+=(aaaa)
fi

# Create amama service
if [ -z "amama" ]; then
  echo "⚠️ Warning: Skipping service with empty name"
  continue
fi

echo "Creating service: amama"
curl -s -X POST http://localhost:8001/services \
  -d name=amama \
  -d url=http://amama:8080 > /dev/null

if [ $? -eq 0 ]; then
  VALID_SERVICES+=(amama)
fi



# Create route for amara
if [ -z "amara" ]; then
  echo "⚠️ Warning: Skipping route 'amara-route-1' with empty service name"
  continue
fi

# Check if service exists
SERVICE_EXISTS=false
for svc in "${VALID_SERVICES[@]}"; do
  if [ "$svc" == "amara" ]; then
    SERVICE_EXISTS=true
    break
  fi
done

if [ "$SERVICE_EXISTS" = false ]; then
  echo "⚠️ Warning: Service 'amara' does not exist, cannot create route 'amara-route-1'"
  continue
fi

echo "Creating route: amara-route-1"
curl -s -X POST http://localhost:8001/services/amara/routes \
  -d "paths[]=/api/amara" \
  -d name=amara-route-1 > /dev/null


# Create route for aaaa
if [ -z "aaaa" ]; then
  echo "⚠️ Warning: Skipping route 'aaaa-route-1' with empty service name"
  continue
fi

# Check if service exists
SERVICE_EXISTS=false
for svc in "${VALID_SERVICES[@]}"; do
  if [ "$svc" == "aaaa" ]; then
    SERVICE_EXISTS=true
    break
  fi
done

if [ "$SERVICE_EXISTS" = false ]; then
  echo "⚠️ Warning: Service 'aaaa' does not exist, cannot create route 'aaaa-route-1'"
  continue
fi

echo "Creating route: aaaa-route-1"
curl -s -X POST http://localhost:8001/services/aaaa/routes \
  -d "paths[]=/api/vendre" \
  -d name=aaaa-route-1 > /dev/null


# Create route for amama
if [ -z "amama" ]; then
  echo "⚠️ Warning: Skipping route 'amama-route-1' with empty service name"
  continue
fi

# Check if service exists
SERVICE_EXISTS=false
for svc in "${VALID_SERVICES[@]}"; do
  if [ "$svc" == "amama" ]; then
    SERVICE_EXISTS=true
    break
  fi
done

if [ "$SERVICE_EXISTS" = false ]; then
  echo "⚠️ Warning: Service 'amama' does not exist, cannot create route 'amama-route-1'"
  continue
fi

echo "Creating route: amama-route-1"
curl -s -X POST http://localhost:8001/services/amama/routes \
  -d "paths[]=/api/inventory-management" \
  -d name=amama-route-1 > /dev/null




# Add http-log plugin
echo "Adding plugin: http-log"
curl -s -X POST http://localhost:8001/plugins \
  -d name=http-log \


  -d "config.http_endpoint=http://logger:3000/log" \

  -d "config.method=POST" \

  -d "config.timeout=10000" \

  -d "config.keepalive=60000" 


 > /dev/null





echo "============================================================"
echo "Kong API Gateway demo for amara is ready!"
echo "============================================================"
echo "Kong Admin API: http://localhost:8001"
echo "Kong Manager (Admin UI): http://localhost:8002"
echo "Kong Proxy: http://localhost:8000"
echo ""
echo "Available API routes:"

echo "- http://localhost:8000/api/amara"

echo "- http://localhost:8000/api/vendre"

echo "- http://localhost:8000/api/inventory-management"

echo ""
echo "To test the configured routes, run:"
echo "./test-api.sh"