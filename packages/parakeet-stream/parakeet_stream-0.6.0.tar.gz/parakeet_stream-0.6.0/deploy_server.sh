#!/bin/bash
# Deploy parakeet-stream server to remote machine

set -e

# Configuration
REMOTE_HOST="maxime@192.168.2.24"
REMOTE_PATH="/home/maxime/Projects/parakeet-stream"
LOCAL_PATH="/home/maxime/Projects/parakeet-stream"

echo "🚀 Deploying parakeet-stream to $REMOTE_HOST:$REMOTE_PATH"
echo ""

# Create remote directory if it doesn't exist
echo "📁 Ensuring remote directory exists..."
ssh "$REMOTE_HOST" "mkdir -p $REMOTE_PATH"

# Sync the code (excluding .venv, __pycache__, etc.)
echo "📦 Syncing code to server..."
rsync -avz --progress \
    --exclude='.venv/' \
    --exclude='__pycache__/' \
    --exclude='*.pyc' \
    --exclude='.pytest_cache/' \
    --exclude='.git/' \
    --exclude='*.egg-info/' \
    --exclude='build/' \
    --exclude='dist/' \
    "$LOCAL_PATH/" \
    "$REMOTE_HOST:$REMOTE_PATH/"

echo ""
echo "✅ Code deployed successfully!"
echo ""
echo "📋 Next steps on the server:"
echo ""
echo "  ssh $REMOTE_HOST"
echo "  cd $REMOTE_PATH"
echo "  pip install -e '.[server]'  # or pip install -e '.[all]' for full install"
echo "  python examples/server_example.py --host 0.0.0.0 --port 8765 --device cpu"
echo ""
echo "📋 To test the client locally:"
echo ""
echo "  pip install -e '.[client]'  # or pip install -e '.[all]'"
echo "  python examples/client_microphone_example.py --server ws://192.168.2.24:8765"
echo ""
