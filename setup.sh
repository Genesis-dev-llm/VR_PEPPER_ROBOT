#!/bin/bash
# ============================================================================
# Pepper VR Teleoperation - Automated Setup Script
# ============================================================================
# This script automates the installation and testing process
# Run with: bash setup.sh
# ============================================================================

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════════╗"
echo "║   Pepper VR Teleoperation - Setup Script              ║"
echo "║   Version 1.0.0 (qi framework)                         ║"
echo "╚════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# ============================================================================
# Step 1: Check Python Version
# ============================================================================
echo -e "${YELLOW}[1/7] Checking Python version...${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    echo -e "${GREEN}✓ Python 3 found: $(python3 --version)${NC}"
    
    # Check if version is compatible (3.8-3.11)
    MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
    MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)
    
    if [ "$MAJOR" -eq 3 ] && [ "$MINOR" -ge 8 ] && [ "$MINOR" -le 11 ]; then
        echo -e "${GREEN}✓ Python version is compatible (3.8-3.11)${NC}"
    else
        echo -e "${RED}⚠ Warning: Python $PYTHON_VERSION may not be fully compatible${NC}"
        echo -e "${YELLOW}  Recommended: Python 3.8-3.11${NC}"
    fi
else
    echo -e "${RED}✗ Python 3 not found! Please install Python 3.8-3.11${NC}"
    exit 1
fi

# ============================================================================
# Step 2: Create Virtual Environment
# ============================================================================
echo -e "\n${YELLOW}[2/7] Creating virtual environment...${NC}"
if [ -d "venv" ]; then
    echo -e "${YELLOW}⚠ Virtual environment already exists. Skipping.${NC}"
else
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
fi

# Activate virtual environment
source venv/bin/activate
echo -e "${GREEN}✓ Virtual environment activated${NC}"

# ============================================================================
# Step 3: Upgrade pip
# ============================================================================
echo -e "\n${YELLOW}[3/7] Upgrading pip...${NC}"
pip install --upgrade pip > /dev/null 2>&1
echo -e "${GREEN}✓ pip upgraded to $(pip --version | cut -d' ' -f2)${NC}"

# ============================================================================
# Step 4: Install Dependencies
# ============================================================================
echo -e "\n${YELLOW}[4/7] Installing Python dependencies...${NC}"
if [ -f "Python/requirements.txt" ]; then
    echo "Installing packages (this may take a minute)..."
    pip install -r Python/requirements.txt
    echo -e "${GREEN}✓ All dependencies installed${NC}"
else
    echo -e "${RED}✗ requirements.txt not found!${NC}"
    exit 1
fi

# ============================================================================
# Step 5: Verify qi Installation
# ============================================================================
echo -e "\n${YELLOW}[5/7] Verifying qi framework installation...${NC}"
python3 -c "import qi; print('qi version:', qi.__version__)" 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ qi framework installed successfully${NC}"
else
    echo -e "${RED}✗ qi framework installation failed${NC}"
    exit 1
fi

# ============================================================================
# Step 6: Get Pepper's IP Address
# ============================================================================
echo -e "\n${YELLOW}[6/7] Pepper Robot Configuration${NC}"
echo -e "${BLUE}Please provide Pepper's IP address.${NC}"
echo -e "${BLUE}(Press Pepper's chest button to hear it announce the IP)${NC}"
read -p "Enter Pepper's IP address (e.g., 192.168.1.100): " PEPPER_IP

# Validate IP format (basic check)
if [[ $PEPPER_IP =~ ^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$ ]]; then
    echo -e "${GREEN}✓ IP address format valid${NC}"
else
    echo -e "${RED}✗ Invalid IP address format${NC}"
    exit 1
fi

# ============================================================================
# Step 7: Test Connection
# ============================================================================
echo -e "\n${YELLOW}[7/7] Testing connection to Pepper...${NC}"
echo "Creating test script..."

cat > test_connection_temp.py << EOF
import qi
import sys

try:
    print("Connecting to Pepper at $PEPPER_IP:9559...")
    session = qi.Session()
    session.connect("tcp://$PEPPER_IP:9559")
    print("✓ Connected successfully!")
    
    motion = session.service("ALMotion")
    print("✓ ALMotion service accessed")
    
    tts = session.service("ALTextToSpeech")
    print("✓ ALTextToSpeech service accessed")
    
    print("\n🎉 SUCCESS! All systems ready.")
    sys.exit(0)
except Exception as e:
    print(f"✗ Connection failed: {e}")
    print("\nTroubleshooting:")
    print("1. Verify Pepper is powered on")
    print("2. Check Pepper's IP address (press chest button)")
    print("3. Ensure both devices on same network")
    print("4. Try: ping $PEPPER_IP")
    sys.exit(1)
EOF

python3 test_connection_temp.py
CONNECTION_RESULT=$?
rm test_connection_temp.py

if [ $CONNECTION_RESULT -eq 0 ]; then
    echo -e "\n${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║               SETUP COMPLETE! 🎉                       ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════════════════╝${NC}"
    
    echo -e "\n${BLUE}Next Steps:${NC}"
    echo -e "1. ${YELLOW}Test keyboard control:${NC}"
    echo -e "   python test_keyboard_control.py $PEPPER_IP"
    echo -e "\n2. ${YELLOW}Start the VR server:${NC}"
    echo -e "   python Python/main.py --ip $PEPPER_IP"
    echo -e "\n3. ${YELLOW}Configure Unity:${NC}"
    echo -e "   - Open Unity project"
    echo -e "   - Set PepperConnection.serverIp to YOUR PC's IP"
    echo -e "   - Build and deploy to Quest 2"
    
    # Save IP for future use
    echo "$PEPPER_IP" > .pepper_ip
    echo -e "\n${GREEN}✓ Pepper IP saved to .pepper_ip${NC}"
    
else
    echo -e "\n${RED}╔════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║          CONNECTION TEST FAILED                        ║${NC}"
    echo -e "${RED}╚════════════════════════════════════════════════════════╝${NC}"
    echo -e "\n${YELLOW}Please fix the connection issue and run setup again.${NC}"
    exit 1
fi

echo -e "\n${BLUE}═══════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}Setup script completed successfully!${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}\n"