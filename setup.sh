#!/bin/bash
# ============================================================
# setup.sh — New project initialization (conda-first)
# Run once after cloning the template
# ============================================================

set -e

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; NC='\033[0m'

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}  Project Template Setup (conda-first)         ${NC}"
echo -e "${BLUE}================================================${NC}"

# --- Check conda is available ---
if ! command -v conda &> /dev/null; then
  echo -e "${RED}Error: conda not found.${NC}"
  echo "Install Miniconda: https://docs.conda.io/en/latest/miniconda.html"
  exit 1
fi

# --- Project name ---
echo ""
read -p "Project name (snake_case): " PROJECT_NAME
if [ -z "$PROJECT_NAME" ]; then echo -e "${RED}Error: name required${NC}"; exit 1; fi

# --- Domain ---
echo ""
echo "Select domain:"
echo "  1) Quantum  2) Cybersecurity  3) AI/ML  4) Data Science  5) Hybrid"
read -p "Choice [1-5]: " DOMAIN_CHOICE
case $DOMAIN_CHOICE in
  1) DOMAIN="quantum" ;; 2) DOMAIN="cyber" ;; 3) DOMAIN="ai" ;;
  4) DOMAIN="data" ;; 5) DOMAIN="hybrid" ;; *) echo -e "${RED}Invalid${NC}"; exit 1 ;;
esac

# --- Update environment.yml with project name ---
if [[ "$OSTYPE" == "darwin"* ]]; then
  sed -i '' "s/name: \[project-name\]/name: ${PROJECT_NAME}/" environment.yml
  sed -i '' "s/project_name/${PROJECT_NAME}/g" configs/config.yaml
  sed -i '' "s/domain: \"\"/domain: \"${DOMAIN}\"/" configs/config.yaml
else
  sed -i "s/name: \[project-name\]/name: ${PROJECT_NAME}/" environment.yml
  sed -i "s/project_name/${PROJECT_NAME}/g" configs/config.yaml
  sed -i "s/domain: \"\"/domain: \"${DOMAIN}\"/" configs/config.yaml
fi
echo -e "${GREEN}✓ Config files updated${NC}"

# --- Create .env ---
cp .env.example .env
if [[ "$OSTYPE" == "darwin"* ]]; then
  sed -i '' "s/your_project_name/${PROJECT_NAME}/" .env
else
  sed -i "s/your_project_name/${PROJECT_NAME}/" .env
fi
echo -e "${GREEN}✓ .env created${NC}"

# --- Create conda environment ---
echo ""
echo -e "${BLUE}Creating conda environment: ${PROJECT_NAME}${NC}"
echo -e "${YELLOW}(This may take 2–5 minutes — conda resolves hardware-aware binaries)${NC}"
conda env create -f environment.yml
echo -e "${GREEN}✓ Conda environment created${NC}"

# --- Activate and install pip-only packages ---
echo ""
echo -e "${BLUE}Installing pip packages inside conda env...${NC}"
conda run -n "$PROJECT_NAME" pip install -r requirements.txt --quiet
echo -e "${GREEN}✓ Pip packages installed${NC}"

# --- Copy ECC rules/skills ---
ECC_PATH="$HOME/everything-claude-code"
if [ -d "$ECC_PATH" ]; then
  echo ""
  echo -e "${BLUE}Copying ECC rules and skills...${NC}"
  cp -r "$ECC_PATH/rules/common" .claude/rules/ 2>/dev/null && echo -e "${GREEN}  ✓ rules/common${NC}"
  cp -r "$ECC_PATH/rules/python" .claude/rules/ 2>/dev/null && echo -e "${GREEN}  ✓ rules/python${NC}"
  cp -r "$ECC_PATH/skills/research-first" .claude/skills/ 2>/dev/null && echo -e "${GREEN}  ✓ skills/research-first${NC}"
  cp -r "$ECC_PATH/skills/tdd-guide" .claude/skills/ 2>/dev/null && echo -e "${GREEN}  ✓ skills/tdd-guide${NC}"
  cp -r "$ECC_PATH/skills/architecture-decision-records" .claude/skills/ 2>/dev/null && echo -e "${GREEN}  ✓ skills/architecture-decision-records${NC}"
else
  echo -e "${YELLOW}! ECC not found — see .claude/rules/README.md to install manually${NC}"
fi

# --- Directory placeholders ---
touch data/raw/.gitkeep data/processed/.gitkeep notebooks/.gitkeep
mkdir -p logs checkpoints
echo -e "${GREEN}✓ Directory structure ready${NC}"

# --- Git init ---
if [ ! -d .git ]; then
  git init
  git add .
  git commit -m "chore: initial scaffold — ${PROJECT_NAME} (${DOMAIN})"
  echo -e "${GREEN}✓ Git initialized${NC}"
fi

echo ""
echo -e "${GREEN}================================================${NC}"
echo -e "${GREEN}  Setup complete!                              ${NC}"
echo -e "${GREEN}================================================${NC}"
echo ""
echo "Activate your environment:"
echo "  conda activate ${PROJECT_NAME}"
echo ""
echo "Next: open Gemini with gemini_setup.md and start Phase 1"
