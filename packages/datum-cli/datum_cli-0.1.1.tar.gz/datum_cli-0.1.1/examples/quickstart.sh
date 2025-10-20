#!/bin/bash

# Quick Start Script for Datum DBT Example
# This script automates the testing workflow

set -e

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}=====================================${NC}"
echo -e "${BLUE}Datum DBT - Docker Example Setup${NC}"
echo -e "${BLUE}=====================================${NC}\n"

# Step 1: Start Docker
echo -e "${YELLOW}Step 1: Starting Docker containers...${NC}"
docker-compose up -d
sleep 5

# Step 2: Wait for PostgreSQL
echo -e "${YELLOW}Step 2: Waiting for PostgreSQL to be ready...${NC}"
until docker-compose exec -T postgres pg_isready -U dbt_user > /dev/null 2>&1; do
  echo "Waiting for PostgreSQL..."
  sleep 2
done
echo -e "${GREEN}✓ PostgreSQL is ready${NC}\n"

# Step 3: Initialize Project 1
echo -e "${YELLOW}Step 3: Initializing Project 1...${NC}"
docker-compose exec -T dbt bash -c "cd /app/project-1 && datum dbt init --repo-path ." 
echo -e "${GREEN}✓ Project 1 initialized${NC}\n"

# Step 4: Validate Project 1
echo -e "${YELLOW}Step 4: Validating Project 1...${NC}"
docker-compose exec -T dbt bash -c "cd /app/project-1 && datum dbt validate"
echo -e "${GREEN}✓ Project 1 validated${NC}\n"

# Step 5: Test dry run
echo -e "${YELLOW}Step 5: Testing dry run...${NC}"
docker-compose exec -T dbt bash -c "cd /app/project-1 && datum dbt run --dry-run"
echo -e "${GREEN}✓ Dry run successful${NC}\n"

# Step 6: Run dbt
echo -e "${YELLOW}Step 6: Running dbt...${NC}"
docker-compose exec -T dbt bash -c "cd /app/project-1 && datum dbt run"
echo -e "${GREEN}✓ dbt run successful${NC}\n"

# Step 7: Add schedule
echo -e "${YELLOW}Step 7: Adding 1-minute schedule for testing...${NC}"
docker-compose exec -T dbt bash -c "cd /app/project-1 && datum dbt schedule cron --expr '* * * * *' || true"
echo -e "${GREEN}✓ Schedule added${NC}\n"

# Step 8: Show schedule
echo -e "${YELLOW}Step 8: Checking schedule status...${NC}"
docker-compose exec -T dbt bash -c "cd /app/project-1 && datum dbt schedule status"
echo -e "${GREEN}✓ Schedule status shown${NC}\n"

# Step 9: Wait for first scheduled run
echo -e "${YELLOW}Step 9: Waiting 65 seconds for first scheduled run...${NC}"
for i in {1..13}; do
  echo -n "."
  sleep 5
done
echo ""
echo -e "${GREEN}✓ Wait complete${NC}\n"

# Step 10: Show logs
echo -e "${YELLOW}Step 10: Showing run history...${NC}"
docker-compose exec -T dbt bash -c "cd /app/project-1 && datum dbt logs"
echo -e "${GREEN}✓ Logs displayed${NC}\n"

# Summary
echo -e "${BLUE}=====================================${NC}"
echo -e "${GREEN}✓ All tests completed successfully!${NC}"
echo -e "${BLUE}=====================================${NC}\n"

echo "Next steps:"
echo "1. Monitor more runs: docker-compose exec dbt bash"
echo "2. Run project-2: cd /app/project-2 && datum dbt init --repo-path ."
echo "3. View full logs: docker-compose exec dbt datum dbt logs --last 20"
echo "4. Stop: docker-compose down"
