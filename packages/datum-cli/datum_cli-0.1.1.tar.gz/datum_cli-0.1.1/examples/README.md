# Datum DBT - Docker Example

This example demonstrates using Datum DBT to schedule dbt projects with Docker and PostgreSQL.

## Setup

### Prerequisites
- Docker & Docker Compose installed
- Datum DBT installed locally (for testing)

### Project Structure
```
├── docker-compose.yml      # PostgreSQL + dbt container
├── Dockerfile              # dbt + datum setup
├── profiles.yml            # dbt profiles configuration
├── project-1/              # First dbt project
│   ├── dbt_project.yml
│   ├── models/
│   └── data/
└── project-2/              # Second dbt project
    ├── dbt_project.yml
    ├── models/
    └── data/
```

## Quick Start

### 1. Start Docker Environment
```bash
docker-compose up -d

# Verify PostgreSQL is ready
docker-compose logs postgres | grep "database system is ready"
```

### 2. Enter Container
```bash
docker-compose exec dbt bash
```

### 3. Initialize Project 1
```bash
# Inside container
cd /app/project-1
datum dbt init --repo-path .

# Verify
datum dbt validate
```

### 4. Test Running dbt
```bash
# Dry run first
datum dbt run --dry-run

# Actual run
datum dbt run
```

### 5. Schedule Project 1 (1-minute interval for testing)
```bash
# Schedule for every minute
datum dbt schedule cron --expr "* * * * *"

# Check schedule
datum dbt schedule status

# View logs
datum dbt logs
```

### 6. Monitor Execution
```bash
# Watch runs execute (in a new terminal)
watch -n 5 "docker-compose exec dbt datum dbt logs"

# Or check crontab
docker-compose exec dbt crontab -l
```

### 7. After Testing, Schedule Production (every hour)
```bash
datum dbt schedule cron --expr "0 * * * *"
```

### 8. View Final Results
```bash
# List all runs
datum dbt logs --last 10

# View specific run
datum dbt logs <run-id>

# Check logs in container
ls -la ~/.datum/runs/
```

## Testing Checklist

- [ ] Docker containers start successfully
- [ ] PostgreSQL connection works
- [ ] Project 1 initializes without errors
- [ ] Validation passes all checks
- [ ] Dry run shows correct command
- [ ] Actual run executes successfully
- [ ] Schedule added to crontab
- [ ] First scheduled run executes
- [ ] Run recorded in logs
- [ ] Multiple runs tracked correctly
- [ ] Run history accessible via `datum dbt logs`
- [ ] Schedule can be removed

## Troubleshooting

### PostgreSQL Not Ready
```bash
# Wait longer
docker-compose logs postgres

# Restart
docker-compose restart postgres
```

### Connection Errors
```bash
# Verify profiles.yml is correct
cat profiles.yml

# Test connection manually
docker-compose exec dbt psql -h postgres -U dbt_user -d analytics_dev -c "SELECT 1"
```

### Cron Not Running
```bash
# Check cron service
docker-compose exec dbt service cron status

# Restart cron
docker-compose exec dbt service cron restart
```

### View All Logs
```bash
# Container logs
docker-compose logs dbt

# dbt logs in container
docker-compose exec dbt tail -f ~/.datum/runs/*/output.log
```

## Cleanup

### Stop Containers
```bash
docker-compose down

# With volume cleanup
docker-compose down -v
```

### Remove Local Config
```bash
rm -rf ~/.datum/
```

## Features Demonstrated

✅ CLI initialization with SSH keys
✅ Project validation (5 checks)
✅ dbt execution with real-time output
✅ Cron scheduling (1-minute interval)
✅ Run history and logging
✅ Configuration management
✅ Multi-project support
✅ Error handling and recovery

## Expected Output

### First Run
```
Executing: dbt run --target dev
[00:00:00] Connected to database
[00:00:05] Running 1 models...
[00:00:10] Success!
Duration: 10.2s
```

### Scheduled Runs
```
Recent Runs (last 10)

Run ID  │ Time              │ Status   │ Duration
────────┼───────────────────┼──────────┼──────────
abc123  │ 2025-10-20 10:01 │ SUCCESS  │ 10.2s
def456  │ 2025-10-20 10:00 │ SUCCESS  │ 9.8s
```

## Next Steps

1. **Test project-2** - Repeat steps 3-8 for second project
2. **Multiple projects** - Schedule both projects
3. **Different schedules** - Use different cron expressions
4. **Production setup** - Increase interval to hourly or daily
5. **Cloud integration** - Push logs to Datum cloud (future)

## Support

For issues:
1. Check logs: `docker-compose logs`
2. Verify config: `docker-compose exec dbt cat profiles.yml`
3. Test manually: `docker-compose exec dbt dbt run`
4. Review documentation: See main README

---

**Ready to schedule dbt projects with datum!** 🚀
