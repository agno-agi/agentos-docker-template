#!/bin/bash

############################################################################
#
#    Agno Container Entrypoint
#
############################################################################

# Colors
ORANGE='\033[38;5;208m'
DIM='\033[2m'
BOLD='\033[1m'
NC='\033[0m'

echo ""
echo -e "${ORANGE}"
cat << 'BANNER'
     █████╗  ██████╗ ███╗   ██╗ ██████╗
    ██╔══██╗██╔════╝ ████╗  ██║██╔═══██╗
    ███████║██║  ███╗██╔██╗ ██║██║   ██║
    ██╔══██║██║   ██║██║╚██╗██║██║   ██║
    ██║  ██║╚██████╔╝██║ ╚████║╚██████╔╝
    ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝ ╚═════╝
BANNER
echo -e "${NC}"

if [[ "$PRINT_ENV_ON_LOAD" = true || "$PRINT_ENV_ON_LOAD" = True ]]; then
    echo -e "    ${DIM}Environment:${NC}"
    printenv | sed 's/^/    /'
    echo ""
fi

if [[ "$WAIT_FOR_DB" = true || "$WAIT_FOR_DB" = True ]]; then
    echo -e "    ${DIM}Waiting for database at ${DB_HOST}:${DB_PORT}...${NC}"
    TIMEOUT="${WAIT_FOR_DB_TIMEOUT:-60}"
    if command -v dockerize >/dev/null 2>&1; then
        dockerize -wait tcp://$DB_HOST:$DB_PORT -timeout "${TIMEOUT}s"
    else
        # Fallback: simple port wait (no dockerize in image)
        ELAPSED=0
        until python3 -c "import socket; socket.create_connection(('$DB_HOST', $DB_PORT), timeout=2)" 2>/dev/null; do
            sleep 2
            ELAPSED=$((ELAPSED + 2))
            if [[ $ELAPSED -ge $TIMEOUT ]]; then
                echo -e "    ${BOLD}Timeout waiting for DB after ${TIMEOUT}s.${NC}" >&2
                exit 1
            fi
        done
    fi
    echo -e "    ${BOLD}Database ready.${NC}"
    echo ""
fi

case "$1" in
    chill)
        echo -e "    ${DIM}Mode: chill${NC}"
        echo -e "    ${BOLD}Container running.${NC}"
        echo ""
        while true; do sleep 18000; done
        ;;
    *)
        echo -e "    ${DIM}> $@${NC}"
        echo ""
        exec "$@"
        ;;
esac