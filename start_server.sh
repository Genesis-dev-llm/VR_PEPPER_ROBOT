#!/bin/bash
# ============================================================================
# Quick Start Script - Launch Pepper VR Server
# ============================================================================
# Usage: 
#   ./start_server.sh                    (uses saved IP)
#   ./start_server.sh 192.168.1.100      (use specific IP)
# ============================================================================

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════════╗"
echo "║      Pepper VR Teleoperation Server Launcher          ║"
echo "╚════════════════════════════════════════════════════════╝"
echo -e "${NC}\n"

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
    echo -e "${GREEN}✓ Virtual environment activated${NC}"
else
    echo -e "${YELLOW}⚠ Virtual environment not found. Run setup.sh first.${NC}"
    exit 1
fi

# Determine Pepper IP
if [ -n "$1" ]; then
    PEPPER_IP="$1"
    echo -e "${BLUE}Using provided IP: $PEPPER_IP${NC}"
elif [ -f ".pepper_ip" ]; then
    PEPPER_IP=$(cat .pepper_ip)
    echo -e "${BLUE}Using saved IP: $PEPPER_IP${NC}"
else
    echo -e "${YELLOW}No IP provided and no saved IP found.${NC}"
    read -p "Enter Pepper's IP address: " PEPPER_IP
fi

# Display startup info
echo -e "\n${YELLOW}Starting Pepper VR Teleoperation Server...${NC}"
echo -e "${BLUE}───────────────────────────────────────────────────────${NC}"
echo -e "Pepper IP:      $PEPPER_IP"
echo -e "WebSocket Port: 5000"
echo -e "Video Port:     8080"
echo -e "${BLUE}───────────────────────────────────────────────────────${NC}\n"

# Get PC's IP for Unity configuration
PC_IP=$(hostname -I | awk '{print $1}')
if [ -n "$PC_IP" ]; then
    echo -e "${GREEN}Your PC's IP: $PC_IP${NC}"
    echo -e "${YELLOW}Configure Unity PepperConnection.serverIp = \"$PC_IP\"${NC}\n"
fi

echo -e "${YELLOW}Press Ctrl+C to stop the server${NC}\n"
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}\n"

# Start the server
python Python/main.py --ip $PEPPER_IP

# Cleanup on exit
echo -e "\n${YELLOW}Server stopped.${NC}"