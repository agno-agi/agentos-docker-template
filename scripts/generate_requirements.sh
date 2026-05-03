#!/bin/bash

############################################################################
#
#    Agno Requirements Generator
#
#    Usage:
#      ./scripts/generate_requirements.sh           # Generate
#      ./scripts/generate_requirements.sh upgrade   # Generate with upgrade
#
############################################################################

set -e

CURR_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "${CURR_DIR}")"

# Colors
ORANGE='\033[38;5;208m'
DIM='\033[2m'
BOLD='\033[1m'
NC='\033[0m'

echo ""
echo -e "    ${ORANGE}▸${NC} ${BOLD}Generating requirements.txt${NC}"
echo ""

if [[ "$1" = "upgrade" ]]; then
    echo -e "    ${DIM}Mode: upgrade${NC}"
    echo -e "    ${DIM}> uv lock --upgrade && uv export --frozen --no-hashes --no-editable${NC}"
    echo ""
    uv lock --upgrade --project ${REPO_ROOT}
else
    echo -e "    ${DIM}Mode: standard${NC}"
    echo -e "    ${DIM}> uv lock && uv export --frozen --no-hashes --no-editable${NC}"
    echo ""
    uv lock --project ${REPO_ROOT}
fi

uv export --frozen --no-hashes --no-editable --project ${REPO_ROOT} -o ${REPO_ROOT}/requirements.txt

echo ""
echo -e "    ${BOLD}Done.${NC}"
echo ""
