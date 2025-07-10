#!/bin/bash

# run_heb.sh - Simple Docker wrapper with dynamic environment variables
# Just run: ./run_heb.sh

set -e

PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
CONFIG_FILE="$PROJECT_DIR/HEB.config"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
TESTING_SCRIPT="run_script.py"
IMAGE_NAME="heb:latest"
PYTHON_VERSION="3.12"

load_config() {
    if [ -f "$CONFIG_FILE" ]; then
        source "$CONFIG_FILE"
    else
        echo -e "${RED} HEB.config file not found. Please create a HEB.config and run again.${NC}"
        exit 1
    fi
}

# Build dynamic environment variable flags from config file
build_env_flags() {
    local env_flags=""
    local hf_token_found=false
    
    # Always add WORKDIR (not from config)
    env_flags+=" --env WORKDIR=/project"
    
    if [ -f "$CONFIG_FILE" ]; then
        # Read config file and extract all variable assignments
        while IFS= read -r line; do
            # Skip empty lines and comments
            if [[ -z "$line" ]] || [[ "$line" =~ ^[[:space:]]*# ]]; then
                continue
            fi
            
            # Extract variable name and value (handle = with optional spaces)
            if [[ "$line" =~ ^[[:space:]]*([A-Za-z_][A-Za-z0-9_]*)[[:space:]]*=[[:space:]]*(.*)$ ]]; then
                var_name="${BASH_REMATCH[1]}"
                var_value="${BASH_REMATCH[2]}"
                
                # Remove quotes if present
                var_value=$(echo "$var_value" | sed 's/^"//;s/"$//')
                
                # Check if this is HF_TOKEN
                if [[ "$var_name" == "HF_TOKEN" ]]; then
                    hf_token_found=true
                fi
                
                # Add to environment flags
                env_flags+=" --env ${var_name}=${var_value}"
            fi
        done < "$CONFIG_FILE"
    fi
    
    # If HF_TOKEN wasn't found in config, try to use the default from environment
    if [ "$hf_token_found" = false ] && [ -n "$HF_TOKEN" ]; then
        env_flags+=" --env HF_TOKEN=${HF_TOKEN}"
    fi
    
    echo "$env_flags"
}

validate_config() {
    if [ ! -d "$PROJECT_DIR" ]; then
        echo -e "${RED}Project directory does not exist: $PROJECT_DIR${NC}"
        exit 1
    fi
}

image_exists() {
    docker images -q "$IMAGE_NAME" | grep -q .
}

build_if_needed() {
    if ! image_exists; then
        echo -e "${YELLOW}Docker image not found. Building...${NC}"
        docker build -t "$IMAGE_NAME" \
            --build-arg PYTHON_VERSION="$PYTHON_VERSION" \
            "$PROJECT_DIR"
        echo -e "${GREEN}✓ Build complete${NC}"
    fi
}

run_default() {
    echo -e "${GREEN}Running: $TESTING_SCRIPT${NC}"
    echo -e "${BLUE}Project: $PROJECT_DIR${NC}"
    
    # Get dynamic environment flags
    ENV_FLAGS=$(build_env_flags)
    
    # Debug: show what environment variables will be passed
    echo -e "${BLUE}Environment variables: $(echo $ENV_FLAGS | sed 's/--env /\n  • /g' | tail -n +2)${NC}"
    
    docker run --rm \
        --mount type=bind,src="$PROJECT_DIR",dst=/project \
        $ENV_FLAGS \
        "$IMAGE_NAME" python3 "/project/$TESTING_SCRIPT"
}

# Simple usage - if no arguments, just run the default
if [ $# -eq 0 ]; then
    load_config
    validate_config
    build_if_needed
    run_default
    exit 0
fi

# Advanced usage with arguments
case "${1:-}" in
    "shell"|"sh")
        load_config
        validate_config
        build_if_needed
        echo -e "${GREEN}Starting interactive shell...${NC}"
        
        # Get dynamic environment flags
        ENV_FLAGS=$(build_env_flags)
        
        docker run -it --rm \
            --mount type=bind,src="$PROJECT_DIR",dst=/project \
            $ENV_FLAGS \
            "$IMAGE_NAME"
        ;;
    "build")
        load_config
        validate_config
        echo -e "${GREEN}Building Docker image...${NC}"
        docker build -t "$IMAGE_NAME" \
            --build-arg PYTHON_VERSION="$PYTHON_VERSION" \
            "$PROJECT_DIR"
        echo -e "${GREEN}✓ Build complete${NC}"
        ;;
    "run")
        load_config
        validate_config
        build_if_needed
        SCRIPT_TO_RUN="${2:-$TESTING_SCRIPT}"
        echo -e "${GREEN}Running: $SCRIPT_TO_RUN${NC}"
        
        # Get dynamic environment flags
        ENV_FLAGS=$(build_env_flags)
        
        docker run --rm \
            --mount type=bind,src="$PROJECT_DIR",dst=/project \
            $ENV_FLAGS \
            "$IMAGE_NAME" python3 "$SCRIPT_TO_RUN" "${@:3}"
        ;;
    "env")
        load_config
        echo -e "${GREEN}Environment variables from config:${NC}"
        ENV_FLAGS=$(build_env_flags)
        echo "$ENV_FLAGS" | sed 's/--env /\n  • /g' | tail -n +2
        ;;
    "help"|"--help"|"-h")
        echo "HumanEditBench Docker Wrapper"
        echo ""
        echo "Simple usage:"
        echo "  ./run_heb.sh              # Run default script (auto-builds if needed)"
        echo ""
        echo "Advanced usage:"
        echo "  ./run_heb.sh shell        # Interactive shell"
        echo "  ./run_heb.sh build        # Force rebuild"
        echo "  ./run_heb.sh run [script] # Run specific script"
        echo "  ./run_heb.sh env          # Show environment variables from config"
        echo ""
        echo "First time setup:"
        echo "  1. Run: ./run_heb.sh"
        echo ""
        echo "Dynamic environment variables:"
        echo "  All variables in HEB.config are automatically passed to the container!"
        ;;
    *)
        echo -e "${RED}Unknown command: $1${NC}"
        echo "Run './run_heb.sh help' for usage"
        exit 1
        ;;
esac