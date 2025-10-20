#!/bin/bash
# Skill Jangler MCP Server - Quick Setup Script
# This script automates the MCP server setup for Claude Code

set -e # Exit on error

echo "=================================================="
echo "Skill Jangler MCP Server - Quick Setup"
echo "=================================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Step 1: Check Python version
echo "Step 1: Checking Python version..."
if ! command -v python3 &>/dev/null; then
	echo -e "${RED}❌ Error: python3 not found${NC}"
	echo "Please install Python 3.7 or higher"
	exit 1
fi
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo -e "${GREEN}✓${NC} Python $PYTHON_VERSION found"
echo ""

# Step 2: Get repository path
REPO_PATH=$(pwd)
echo "Step 2: Repository location"
echo "Path: $REPO_PATH"
echo ""

# Step 3: Install dependencies
echo "Step 3: Installing Python dependencies..."
echo "This will install: mcp, requests, beautifulsoup4"
read -p "Continue? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
	echo "Installing MCP server dependencies..."
	uv pip install -r mcp/requirements.txt || {
		echo -e "${RED}❌ Failed to install MCP dependencies${NC}"
		exit 1
	}

	echo "Installing CLI tool dependencies..."
	uv pip install requests beautifulsoup4 || {
		echo -e "${RED}❌ Failed to install CLI dependencies${NC}"
		exit 1
	}

	echo -e "${GREEN}✓${NC} Dependencies installed successfully"
else
	echo "Skipping dependency installation"
fi
echo ""

# Step 4: Test MCP server
echo "Step 4: Testing MCP server..."
timeout 3 python3 mcp/server.py 2>/dev/null || {
	if [ $? -eq 124 ]; then
		echo -e "${GREEN}✓${NC} MCP server starts correctly (timeout expected)"
	else
		echo -e "${YELLOW}⚠${NC} MCP server test inconclusive, but may still work"
	fi
}
echo ""

# Step 5: Optional - Run tests
echo "Step 5: Run test suite? (optional)"
read -p "Run MCP tests to verify everything works? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
	# Check if pytest is installed
	if ! command -v pytest &>/dev/null; then
		echo "Installing pytest..."
		pip3 install pytest || {
			echo -e "${YELLOW}⚠${NC} Could not install pytest, skipping tests"
		}
	fi

	if command -v pytest &>/dev/null; then
		echo "Running MCP server tests..."
		python3 -m pytest tests/test_mcp_server.py -v --tb=short || {
			echo -e "${RED}❌ Some tests failed${NC}"
			echo "The server may still work, but please check the errors above"
		}
	fi
else
	echo "Skipping tests"
fi
echo ""

# Step 6: Configure Claude Code
echo "Step 6: Configure Claude Code"
echo "=================================================="
echo ""
echo "You need to add this configuration to Claude Code:"
echo ""
echo -e "${YELLOW}Configuration file:${NC} ~/.config/claude-code/mcp.json"
echo ""
echo "Add this JSON configuration:"
echo ""
echo -e "${GREEN}{"
echo "  \"mcpServers\": {"
echo "    \"skill-jangler\": {"
echo "      \"command\": \"python3\","
echo "      \"args\": ["
echo "        \"$REPO_PATH/mcp/server.py\""
echo "      ],"
echo "      \"cwd\": \"$REPO_PATH\""
echo "    }"
echo "  }"
echo -e "}${NC}"
echo ""
echo "To configure automatically, run:"
echo ""
echo -e "${YELLOW}  mkdir -p ~/.config/claude-code${NC}"
echo ""
echo "Then edit ~/.config/claude-code/mcp.json and add the configuration above"
echo ""
echo "Or use this one-liner (BE CAREFUL - this may overwrite existing config):"
echo ""
echo -e "${RED}cat > ~/.config/claude-code/mcp.json << 'EOF'
{
  \"mcpServers\": {
    \"skill-jangler\": {
      \"command\": \"python3\",
      \"args\": [
        \"$REPO_PATH/mcp/server.py\"
      ],
      \"cwd\": \"$REPO_PATH\"
    }
  }
}
EOF${NC}"
echo ""

# Ask if user wants auto-configure
echo ""
read -p "Auto-configure Claude Code now? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
	# Check if config already exists
	if [ -f ~/.config/claude-code/mcp.json ]; then
		echo -e "${YELLOW}⚠ Warning: ~/.config/claude-code/mcp.json already exists${NC}"
		echo "Current contents:"
		cat ~/.config/claude-code/mcp.json
		echo ""
		read -p "Overwrite? (y/n) " -n 1 -r
		echo ""
		if [[ ! $REPLY =~ ^[Yy]$ ]]; then
			echo "Skipping auto-configuration"
			echo "Please manually add the skill-jangler server to your config"
			exit 0
		fi
	fi

	# Create config directory
	mkdir -p ~/.config/claude-code

	# Write configuration
	cat >~/.config/claude-code/mcp.json <<EOF
{
  "mcpServers": {
    "skill-jangler": {
      "command": "python3",
      "args": [
        "$REPO_PATH/mcp/server.py"
      ],
      "cwd": "$REPO_PATH"
    }
  }
}
EOF

	echo -e "${GREEN}✓${NC} Configuration written to ~/.config/claude-code/mcp.json"
else
	echo "Skipping auto-configuration"
	echo "Please manually configure Claude Code using the JSON above"
fi
echo ""

# Step 7: Final instructions
echo "=================================================="
echo "Setup Complete!"
echo "=================================================="
echo ""
echo "Next steps:"
echo ""
echo "  1. ${YELLOW}Restart Claude Code${NC} (quit and reopen, don't just close window)"
echo "  2. In Claude Code, test with: ${GREEN}\"List all available configs\"${NC}"
echo "  3. You should see 9 Skill Jangler tools available"
echo ""
echo "Available MCP Tools:"
echo "  • generate_config   - Create new config files"
echo "  • estimate_pages    - Estimate scraping time"
echo "  • scrape_docs       - Scrape documentation"
echo "  • package_skill     - Create .zip files"
echo "  • upload_skill      - Upload skills to Claude"
echo "  • list_configs      - Show available configs"
echo "  • validate_config   - Validate config files"
echo "  • split_config      - Split large documentation"
echo "  • generate_router   - Create router/hub skills"
echo ""
echo "Example commands to try in Claude Code:"
echo "  • ${GREEN}List all available configs${NC}"
echo "  • ${GREEN}Validate configs/react.json${NC}"
echo "  • ${GREEN}Generate config for Tailwind at https://tailwindcss.com/docs${NC}"
echo ""
echo "Documentation:"
echo "  • MCP Setup Guide: ${YELLOW}docs/MCP_SETUP.md${NC}"
echo "  • Full docs: ${YELLOW}README.md${NC}"
echo ""
echo "Troubleshooting:"
echo "  • Check logs: ~/Library/Logs/Claude Code/ (macOS)"
echo "  • Test server: python3 mcp/server.py"
echo "  • Run tests: python3 -m pytest tests/test_mcp_server.py -v"
echo ""
echo "Happy skill creating! 🚀"
