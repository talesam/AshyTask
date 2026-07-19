#!/usr/bin/env bash
# =============================================================================
# AshyTask - Bot Manager (start/stop/restart/status/logs)
# =============================================================================
set -euo pipefail

# Project directory (where this script lives)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"

# Configuration
BOT_SCRIPT="bot.py"
PID_FILE="${PROJECT_DIR}/ashytask.pid"
LOG_DIR="${PROJECT_DIR}/logs"
LOG_FILE="${LOG_DIR}/ashytask.log"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

print_header() {
    echo -e "${BLUE}"
    echo "  ╔══════════════════════════════════════╗"
    echo "  ║         AshyTask Bot Manager         ║"
    echo "  ╚══════════════════════════════════════╝"
    echo -e "${NC}"
}

log_info()  { echo -e "${GREEN}[INFO]${NC}  $1"; }
log_warn()  { echo -e "${YELLOW}[WARN]${NC}  $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Check if bot is running via PID file
check_running() {
    if [[ -f "$PID_FILE" ]]; then
        local pid
        pid=$(cat "$PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            return 0
        else
            rm -f "$PID_FILE"
        fi
    fi
    return 1
}

start() {
    print_header

    if check_running; then
        local pid
        pid=$(cat "$PID_FILE")
        log_warn "AshyTask already running (PID: $pid)"
        log_info "Use: $0 restart"
        exit 1
    fi

    cd "$PROJECT_DIR"

    # Activate venv if present
    if [[ -f "venv/bin/activate" ]]; then
        # shellcheck disable=SC1091
        source venv/bin/activate
        log_info "Virtual environment activated"
    fi

    # Verify .env exists
    if [[ ! -f ".env" ]]; then
        log_error ".env file not found! Copy .env.example and set your token."
        exit 1
    fi

    # Create log directory
    mkdir -p "$LOG_DIR"

    # Verify python is available
    if ! command -v python &>/dev/null; then
        log_error "Python not found!"
        exit 1
    fi

    log_info "Starting AshyTask bot..."

    # Start bot as background process, redirect output to log
    nohup python "$BOT_SCRIPT" >> "$LOG_FILE" 2>&1 &
    local pid=$!
    echo "$pid" > "$PID_FILE"

    sleep 2

    if check_running; then
        log_info "AshyTask started successfully! (PID: $pid)"
        log_info "Log file: $LOG_FILE"
    else
        log_error "Failed to start AshyTask. Check logs:"
        log_error "  tail -f $LOG_FILE"
        rm -f "$PID_FILE"
        exit 1
    fi
}

stop() {
    if ! check_running; then
        log_warn "AshyTask is not running"
        return 0
    fi

    local pid
    pid=$(cat "$PID_FILE")
    log_info "Stopping AshyTask (PID: $pid)..."

    kill -TERM "$pid"

    # Wait up to 10 seconds for graceful shutdown
    for _ in $(seq 1 10); do
        if ! kill -0 "$pid" 2>/dev/null; then
            rm -f "$PID_FILE"
            log_info "AshyTask stopped successfully"
            return 0
        fi
        sleep 1
    done

    # Force kill
    log_warn "Forcing stop..."
    kill -9 "$pid" 2>/dev/null || true
    rm -f "$PID_FILE"
    log_info "AshyTask stopped"
}

restart() {
    log_info "Restarting AshyTask..."
    stop
    sleep 1
    start
}

status() {
    if check_running; then
        local pid
        pid=$(cat "$PID_FILE")
        log_info "AshyTask is running (PID: $pid)"
        log_info "Uptime: $(ps -o etime= -p "$pid" 2>/dev/null || echo "unknown")"
        log_info "Memory: $(ps -o rss= -p "$pid" 2>/dev/null | awk '{printf "%.1f MB", $1/1024}' || echo "unknown")"
    else
        log_warn "AshyTask is not running"
    fi
}

logs() {
    if [[ -f "$LOG_FILE" ]]; then
        tail -f "$LOG_FILE"
    else
        log_warn "No log file found"
    fi
}

usage() {
    echo "Usage: $0 {start|stop|restart|status|logs}"
    echo ""
    echo "  start    Start the bot"
    echo "  stop     Stop the bot"
    echo "  restart  Restart the bot"
    echo "  status   Check bot status"
    echo "  logs     Follow logs in real time"
}

# Main
case "${1:-}" in
    start)   start   ;;
    stop)    stop    ;;
    restart) restart ;;
    status)  status  ;;
    logs)    logs    ;;
    *)       usage   ;;
esac
