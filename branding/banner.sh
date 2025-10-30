#!/bin/bash

# Astrals Agency Banner
print_banner() {
    echo ""
    # Print logo from logo.txt
    local script_dir
    script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    if [ -f "$script_dir/logo.txt" ]; then
        cat "$script_dir/logo.txt"
    fi
    echo ""
    echo "    ╔══════════════════════════════════════════════════════════════╗"
    echo "    ║                    ASTRALS AGENCY                           ║"
    echo "    ║                 Social Media AI Platform                    ║"
    echo "    ╚══════════════════════════════════════════════════════════════╝"
    echo ""
}

# Compact version for smaller displays
print_compact_banner() {
    echo ""
    local script_dir
    script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    if [ -f "$script_dir/logo.txt" ]; then
        cat "$script_dir/logo.txt"
        echo ""
    fi
    echo "ASTRALS AGENCY — Social Media AI Platform"
    echo ""
}

# Minimal version for logs
print_minimal_banner() {
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                    ASTRALS AGENCY                           ║"
    echo "║                  Social Media AI Platform                   ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
}
