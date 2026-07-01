#!/bin/bash

# Aether Workspace Installer
# Supported OS: macOS

set -e

VAULT_DIR="$HOME/.aether_vault"
LAUNCH_AGENT_DIR="$HOME/Library/LaunchAgents"
PLIST_FILE="$LAUNCH_AGENT_DIR/com.aether.watcher.plist"

echo "======================================================="
echo "             AETHER WORKSPACE INSTALLER                "
echo "======================================================="

# 1. OS Compatibility Check
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "Error: Aether Workspace is optimized for macOS only."
    exit 1
fi

# 2. Create vault folder structure
echo "Step 1: Creating vault directory structure..."
mkdir -p "$VAULT_DIR"
mkdir -p "$VAULT_DIR/00_Inbox"
mkdir -p "$VAULT_DIR/10_GATE_Prep/11_Syllabus_Schedules"
mkdir -p "$VAULT_DIR/10_GATE_Prep/12_Study_Materials"
mkdir -p "$VAULT_DIR/10_GATE_Prep/13_Notes_Summaries"
mkdir -p "$VAULT_DIR/10_GATE_Prep/14_Practice_Tests"
mkdir -p "$VAULT_DIR/10_GATE_Prep/15_Tools_QuizGen"
mkdir -p "$VAULT_DIR/20_College_Academics"
mkdir -p "$VAULT_DIR/30_Active_Projects"
mkdir -p "$VAULT_DIR/40_Resources_Reference"
mkdir -p "$VAULT_DIR/50_Archive/System_Dumps"
echo "Done creating folders."

# 3. Create isolated Python environment and install watchdog + pypdf
echo "Step 2: Initializing virtual environment..."
python3 -m venv "$VAULT_DIR/venv"
"$VAULT_DIR/venv/bin/pip" install --upgrade pip
"$VAULT_DIR/venv/bin/pip" install watchdog pypdf
echo "Virtual environment ready."

# 4. Copy codebase to Vault
echo "Step 3: Copying codebases into Aether vault..."
cp -R src/*.py "$VAULT_DIR/"
cp bin/desk "$VAULT_DIR/desk.sh"
chmod +x "$VAULT_DIR/desk.sh"
echo "Code files successfully deployed."

# 5. Create & Load LaunchAgent for background watcher
echo "Step 4: Registering background filing service..."
mkdir -p "$LAUNCH_AGENT_DIR"

cat <<EOF > "$PLIST_FILE"
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.aether.watcher</string>
    <key>ProgramArguments</key>
    <array>
        <string>$VAULT_DIR/venv/bin/python3</string>
        <string>$VAULT_DIR/aether_daemon.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>$VAULT_DIR/aether_daemon_stdout.log</string>
    <key>StandardErrorPath</key>
    <string>$VAULT_DIR/aether_daemon_stderr.log</string>
</dict>
</plist>
EOF

launchctl unload "$PLIST_FILE" 2>/dev/null || true
launchctl load "$PLIST_FILE"
echo "Background service launched."

# 6. Redirect screenshots to physical inbox
echo "Step 5: Redirecting default screenshot destination..."
defaults write com.apple.screencapture location "$VAULT_DIR/00_Inbox"
killall SystemUIServer || true
echo "Screenshots successfully directed to Aether Inbox."

# 7. Add command shortcut to zshrc / bash_profile
echo "Step 6: Configuring shell alias..."
ALIAS_LINE="alias desk=\"source \$HOME/.aether_vault/desk.sh\""

# Update .zshrc
if [ -f "$HOME/.zshrc" ]; then
    if ! grep -q "aether_vault/desk.sh" "$HOME/.zshrc"; then
        echo -e "\n# Aether Workspace Shortcut\n$ALIAS_LINE" >> "$HOME/.zshrc"
        echo "Configured alias in ~/.zshrc."
    fi
fi

# Update .bash_profile
if [ -f "$HOME/.bash_profile" ]; then
    if ! grep -q "aether_vault/desk.sh" "$HOME/.bash_profile"; then
        echo -e "\n# Aether Workspace Shortcut\n$ALIAS_LINE" >> "$HOME/.bash_profile"
        echo "Configured alias in ~/.bash_profile."
    fi
fi

echo "======================================================="
echo "       INSTALLATION SUCCESSFUL! AETHER READY           "
echo "======================================================="
echo "To initialize the CLI, open a new terminal window or run:"
echo "  source ~/.zshrc"
echo ""
echo "Type 'desk' to see the help menu."
EOF
