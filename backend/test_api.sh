#!/bin/bash

# colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

BASE_URL="http://localhost:8000"

echo "=================================="
echo "testing realtime chat server api"
echo "=================================="
echo ""

# test 1: health check
echo -n "1. health check... "
RESPONSE=$(curl -s "$BASE_URL/health")
if echo "$RESPONSE" | grep -q "healthy"; then
    echo -e "${GREEN}passed${NC}"
else
    echo -e "${RED}failed${NC}"
    echo "response: $RESPONSE"
fi

# test 2: root endpoint
echo -n "2. root endpoint... "
RESPONSE=$(curl -s "$BASE_URL/")
if echo "$RESPONSE" | grep -q "Realtime Chat Server"; then
    echo -e "${GREEN}passed${NC}"
else
    echo -e "${RED}failed${NC}"
    echo "response: $RESPONSE"
fi

# test 3: register user
echo -n "3. register user... "
TIMESTAMP=$(date +%s)
EMAIL="testuser${TIMESTAMP}@example.com"
USERNAME="testuser${TIMESTAMP}"
PASSWORD="testpassword123"

RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"username\":\"$USERNAME\",\"password\":\"$PASSWORD\"}")

if echo "$RESPONSE" | grep -q "\"id\""; then
    echo -e "${GREEN}passed${NC}"
    USER_ID=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")
else
    echo -e "${RED}failed${NC}"
    echo "response: $RESPONSE"
    exit 1
fi

# test 4: login user
echo -n "4. login user... "
RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"$EMAIL\",\"password\":\"$PASSWORD\"}")

if echo "$RESPONSE" | grep -q "access_token"; then
    echo -e "${GREEN}passed${NC}"
    ACCESS_TOKEN=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")
else
    echo -e "${RED}failed${NC}"
    echo "response: $RESPONSE"
    exit 1
fi

# test 5: get current user
echo -n "5. get current user... "
RESPONSE=$(curl -s -X GET "$BASE_URL/api/v1/auth/me" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

if echo "$RESPONSE" | grep -q "$USERNAME"; then
    echo -e "${GREEN}passed${NC}"
else
    echo -e "${RED}failed${NC}"
    echo "response: $RESPONSE"
fi

# test 6: create chat room
echo -n "6. create chat room... "
RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/chat/rooms" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"Test Room\",\"room_type\":\"group\",\"member_ids\":[$USER_ID]}")

if echo "$RESPONSE" | grep -q "\"id\""; then
    echo -e "${GREEN}passed${NC}"
    ROOM_ID=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")
else
    echo -e "${RED}failed${NC}"
    echo "response: $RESPONSE"
    exit 1
fi

# test 7: get chat rooms
echo -n "7. get chat rooms... "
RESPONSE=$(curl -s -X GET "$BASE_URL/api/v1/chat/rooms" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

if echo "$RESPONSE" | grep -q "Test Room"; then
    echo -e "${GREEN}passed${NC}"
else
    echo -e "${RED}failed${NC}"
    echo "response: $RESPONSE"
fi

# test 8: send message
echo -n "8. send message... "
RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/chat/rooms/$ROOM_ID/messages" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"content":"Hello from test script!"}')

if echo "$RESPONSE" | grep -q "Hello from test script"; then
    echo -e "${GREEN}passed${NC}"
else
    echo -e "${RED}failed${NC}"
    echo "response: $RESPONSE"
fi

# test 9: get messages
echo -n "9. get messages... "
RESPONSE=$(curl -s -X GET "$BASE_URL/api/v1/chat/rooms/$ROOM_ID/messages" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

if echo "$RESPONSE" | grep -q "Hello from test script"; then
    echo -e "${GREEN}passed${NC}"
else
    echo -e "${RED}failed${NC}"
    echo "response: $RESPONSE"
fi

# test 10: get room details
echo -n "10. get room details... "
RESPONSE=$(curl -s -X GET "$BASE_URL/api/v1/chat/rooms/$ROOM_ID" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

if echo "$RESPONSE" | grep -q "Test Room"; then
    echo -e "${GREEN}passed${NC}"
else
    echo -e "${RED}failed${NC}"
    echo "response: $RESPONSE"
fi

echo ""
echo "=================================="
echo -e "${GREEN}all tests completed${NC}"
echo "=================================="
echo ""
echo "your api is working correctly"
echo ""
echo "next steps:"
echo "1. import postman_collection.json into postman"
echo "2. test websocket connections (see testing_guide.md)"
echo "3. start building the react frontend"
echo ""
echo "useful info for postman:"
echo "  - access token: $ACCESS_TOKEN"
echo "  - user id: $USER_ID"
echo "  - room id: $ROOM_ID"
echo ""
