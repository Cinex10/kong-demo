#!/bin/bash
# Test script for amara Kong API Gateway demo

# Check if jq is installed
if ! command -v jq &> /dev/null; then
    echo "jq is not installed. Trying to install it..."
    if command -v apt-get &> /dev/null; then
        sudo apt-get update && sudo apt-get install -y jq
    elif command -v yum &> /dev/null; then
        sudo yum install -y jq
    elif command -v brew &> /dev/null; then
        brew install jq
    else
        echo "Could not install jq automatically. JSON responses will not be formatted."
        JQ_MISSING=true
    fi
else
    JQ_MISSING=false
fi

# Function to format JSON if jq is available
format_json() {
    if [ "$JQ_MISSING" = true ]; then
        cat
    else
        jq 2>/dev/null || echo "Response is not in JSON format"
    fi
}

# Checking if Kong is running
if ! curl -s http://localhost:8001 > /dev/null; then
  echo "Error: Kong does not appear to be running"
  exit 1
fi

echo "Testing Kong API Gateway..."
echo "=========================="

# Check Kong configuration
echo "Checking Kong configuration..."
SERVICES=$(curl -s http://localhost:8001/services | jq -r '.data[].name' 2>/dev/null)
ROUTES=$(curl -s http://localhost:8001/routes | jq -r '.data[].name' 2>/dev/null)

# Display Kong configuration
echo "Configured services:"
echo "$SERVICES" | sed 's/^/- /'
echo 
echo "Configured routes:"
echo "$ROUTES" | sed 's/^/- /'
echo

# Check Docker service connectivity
echo "Checking Docker service connectivity..."

echo "Testing connection to amara service..."
if ! docker ps | grep -q "amara-kong-1"; then
  echo "⚠️  Warning: Kong container is not running. Make sure Kong is up before testing connectivity."
  echo
else
  DOCKER_TEST=$(docker exec amara-kong-1 curl -s --connect-timeout 5 http://amara:8080/health 2>&1)
  if [[ "$DOCKER_TEST" == *"connection refused"* ]] || [[ "$DOCKER_TEST" == *"Name or service not known"* ]] || [[ "$DOCKER_TEST" == *"Failed to connect"* ]]; then
    echo "⚠️  Warning: Could not connect to amara service from Kong container"
    echo "   Error: $DOCKER_TEST" 
    echo "   This might cause API requests to fail."
    echo
  else
    echo "✅ Connection to amara service successful!"
    echo "$DOCKER_TEST" | format_json
    echo
  fi
fi

echo "Testing connection to aaaa service..."
if ! docker ps | grep -q "amara-kong-1"; then
  echo "⚠️  Warning: Kong container is not running. Make sure Kong is up before testing connectivity."
  echo
else
  DOCKER_TEST=$(docker exec amara-kong-1 curl -s --connect-timeout 5 http://aaaa:8080/health 2>&1)
  if [[ "$DOCKER_TEST" == *"connection refused"* ]] || [[ "$DOCKER_TEST" == *"Name or service not known"* ]] || [[ "$DOCKER_TEST" == *"Failed to connect"* ]]; then
    echo "⚠️  Warning: Could not connect to aaaa service from Kong container"
    echo "   Error: $DOCKER_TEST" 
    echo "   This might cause API requests to fail."
    echo
  else
    echo "✅ Connection to aaaa service successful!"
    echo "$DOCKER_TEST" | format_json
    echo
  fi
fi

echo "Testing connection to amama service..."
if ! docker ps | grep -q "amara-kong-1"; then
  echo "⚠️  Warning: Kong container is not running. Make sure Kong is up before testing connectivity."
  echo
else
  DOCKER_TEST=$(docker exec amara-kong-1 curl -s --connect-timeout 5 http://amama:8080/health 2>&1)
  if [[ "$DOCKER_TEST" == *"connection refused"* ]] || [[ "$DOCKER_TEST" == *"Name or service not known"* ]] || [[ "$DOCKER_TEST" == *"Failed to connect"* ]]; then
    echo "⚠️  Warning: Could not connect to amama service from Kong container"
    echo "   Error: $DOCKER_TEST" 
    echo "   This might cause API requests to fail."
    echo
  else
    echo "✅ Connection to amama service successful!"
    echo "$DOCKER_TEST" | format_json
    echo
  fi
fi


echo "Testing API routes..."
echo "===================="







echo
echo "Testing route: /api/amara (amara)"
echo "-------------------------------------------------------"


# No authentication
echo "Get all items:"
RESPONSE=$(curl -s -X GET http://localhost:8000/api/amara/items)
echo "$RESPONSE" | format_json

echo -e "\nGet specific item (ID: 1):"
RESPONSE=$(curl -s -X GET http://localhost:8000/api/amara/items/1)
echo "$RESPONSE" | format_json

echo -e "\nService info:"
RESPONSE=$(curl -s -X GET http://localhost:8000/api/amara/info)
echo "$RESPONSE" | format_json

echo -e "\nEcho request:"
RESPONSE=$(curl -s -X POST http://localhost:8000/api/amara/echo \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}')
echo "$RESPONSE" | format_json



echo
echo "Testing route: /api/vendre (aaaa)"
echo "-------------------------------------------------------"


# No authentication
echo "Get all items:"
RESPONSE=$(curl -s -X GET http://localhost:8000/api/vendre/items)
echo "$RESPONSE" | format_json

echo -e "\nGet specific item (ID: 1):"
RESPONSE=$(curl -s -X GET http://localhost:8000/api/vendre/items/1)
echo "$RESPONSE" | format_json

echo -e "\nService info:"
RESPONSE=$(curl -s -X GET http://localhost:8000/api/vendre/info)
echo "$RESPONSE" | format_json

echo -e "\nEcho request:"
RESPONSE=$(curl -s -X POST http://localhost:8000/api/vendre/echo \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}')
echo "$RESPONSE" | format_json



echo
echo "Testing route: /api/inventory-management (amama)"
echo "-------------------------------------------------------"


# No authentication
echo "Get all items:"
RESPONSE=$(curl -s -X GET http://localhost:8000/api/inventory-management/items)
echo "$RESPONSE" | format_json

echo -e "\nGet specific item (ID: 1):"
RESPONSE=$(curl -s -X GET http://localhost:8000/api/inventory-management/items/1)
echo "$RESPONSE" | format_json

echo -e "\nService info:"
RESPONSE=$(curl -s -X GET http://localhost:8000/api/inventory-management/info)
echo "$RESPONSE" | format_json

echo -e "\nEcho request:"
RESPONSE=$(curl -s -X POST http://localhost:8000/api/inventory-management/echo \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}')
echo "$RESPONSE" | format_json




echo
echo "Testing Kong Admin API"
echo "======================"
echo "API Information:"
curl -s http://localhost:8001 | jq '.plugins.available_on_server' 2>/dev/null || echo "Response is not JSON format"

echo -e "\nStatus Information:"
curl -s http://localhost:8001/status | jq 2>/dev/null || echo "Response is not JSON format"

echo
echo "Tests completed."
echo "You can access Kong Admin API at: http://localhost:8001"
echo "You can access Kong Manager UI at: http://localhost:8002"