#!/bin/bash

# Script to run different Docker Compose configurations
# Usage: ./run-stack.sh [full|no-chunker|no-extraction|minimal] [up|down|build|logs]

CONFIGURATION=${1:-full}
COMMAND=${2:-up}

case $CONFIGURATION in
  "full")
    echo "🚀 Running full stack (all services)..."
    COMPOSE_FILES="-f docker-compose.yml -f docker-compose.full.yml"
    ;;
  "no-chunker")
    echo "🚀 Running stack without chunker service..."
    COMPOSE_FILES="-f docker-compose.yml -f docker-compose.no-chunker.yml"
    ;;
  "no-extraction")
    echo "🚀 Running stack without extraction agent..."
    COMPOSE_FILES="-f docker-compose.yml -f docker-compose.no-extraction.yml"
    ;;
  "minimal")
    echo "🚀 Running minimal stack (no chunker, no extraction agent)..."
    COMPOSE_FILES="-f docker-compose.yml"
    ;;
  *)
    echo "❌ Invalid configuration. Use: full, no-chunker, no-extraction, or minimal"
    echo "Usage: $0 [full|no-chunker|no-extraction|minimal] [up|down|build|logs]"
    exit 1
    ;;
esac

case $COMMAND in
  "up")
    echo "📦 Starting services..."
    docker-compose $COMPOSE_FILES up -d
    ;;
  "down")
    echo "🛑 Stopping services..."
    docker-compose $COMPOSE_FILES down
    ;;
  "build")
    echo "🔨 Building services..."
    docker-compose $COMPOSE_FILES build
    ;;
  "logs")
    echo "📋 Showing logs..."
    docker-compose $COMPOSE_FILES logs -f
    ;;
  "restart")
    echo "🔄 Restarting services..."
    docker-compose $COMPOSE_FILES down
    docker-compose $COMPOSE_FILES up -d
    ;;
  *)
    echo "❌ Invalid command. Use: up, down, build, logs, or restart"
    echo "Usage: $0 [full|no-chunker|no-extraction|minimal] [up|down|build|logs|restart]"
    exit 1
    ;;
esac

echo "✅ Command completed!"