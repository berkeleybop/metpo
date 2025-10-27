#!/bin/bash
# Monitor memory usage of the migration process

LOG_FILE="memory_usage.log"
INTERVAL=60  # Check every 60 seconds

echo "Starting memory monitor - logging to $LOG_FILE"
echo "Timestamp,Total_RAM_GB,Used_RAM_GB,Free_RAM_GB,Python_RSS_MB,Python_VSZ_MB,Python_CPU%" > "$LOG_FILE"

while true; do
    # Get system memory in GB
    mem_info=$(free -g | awk 'NR==2 {print $2","$3","$4}')

    # Find the Python migration process and get its memory usage
    # RSS = Resident Set Size (actual physical memory)
    # VSZ = Virtual Memory Size
    # Get the actual .venv/bin/python3 process (not the uv wrapper)
    python_mem=$(ps aux | grep "\.venv/bin/python3 migrate_to_chromadb_resilient.py" | grep -v grep | awk '{print $6/1024","$5/1024","$3}' | head -1)

    if [ -z "$python_mem" ]; then
        # Process not running
        echo "$(date '+%Y-%m-%d %H:%M:%S'),$mem_info,0,0,0" >> "$LOG_FILE"
    else
        echo "$(date '+%Y-%m-%d %H:%M:%S'),$mem_info,$python_mem" >> "$LOG_FILE"
    fi

    sleep $INTERVAL
done
