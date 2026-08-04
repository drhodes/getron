#!/bin/sh
set -eu

# install.sh - Bootstrap script for Getron
# Responsibility: Download/copy the getron CLI script to PATH.
# Does NOT install Tetron or configure services directly.

GITHUB_REPO="drhodes/getron"
DEFAULT_INSTALL_DIR="$HOME/.local/bin"
INSTALL_DIR="${GETRON_INSTALL_DIR:-$DEFAULT_INSTALL_DIR}"

log_info() {
    printf '%s\n' "[install.sh] $1"
}

log_error() {
    printf '%s\n' "[install.sh] ERROR: $1" >&2
}

mkdir -p "$INSTALL_DIR"

SCRIPT_SRC="$(dirname "$0")/getron"

if [ -f "$SCRIPT_SRC" ]; then
    log_info "Installing getron binary from local source to $INSTALL_DIR/getron..."
    cp "$SCRIPT_SRC" "$INSTALL_DIR/getron"
else
    log_info "Downloading getron from GitHub repository ($GITHUB_REPO)..."
    DOWNLOAD_URL="https://raw.githubusercontent.com/$GITHUB_REPO/main/getron"
    if command -v curl >/dev/null 2>&1; then
        curl -fsSL "$DOWNLOAD_URL" -o "$INSTALL_DIR/getron"
    elif command -v wget >/dev/null 2>&1; then
        wget -qO "$INSTALL_DIR/getron" "$DOWNLOAD_URL"
    else
        log_error "Neither curl nor wget is available to download getron."
        exit 1
    fi
fi

chmod +x "$INSTALL_DIR/getron"
log_info "Getron successfully installed to $INSTALL_DIR/getron"
log_info "Run 'getron install' to install Tetron."
