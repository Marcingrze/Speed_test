# Speed Test Tool - Makefile
# Automatyzuje podstawowe operacje instalacji, testowania i utrzymania

.PHONY: help install uninstall test clean setup dev-setup run-cli run-gui run-scheduler

# Default target
help:
	@echo "Speed Test Tool - Available commands:"
	@echo ""
	@echo "Installation:"
	@echo "  make setup          - Complete setup (venv + dependencies)"
	@echo "  make install        - Install executable scripts"
	@echo "  make install-user   - Install for current user only"
	@echo "  make uninstall      - Remove installed scripts"
	@echo ""
	@echo "Development:"
	@echo "  make dev-setup      - Setup development environment"
	@echo "  make test          - Run basic functionality tests"
	@echo "  make test-full     - Run complete installation test"
	@echo "  make test-offline  - Run tests without network"
	@echo "  make clean         - Clean temporary files"
	@echo ""
	@echo "Running Applications:"
	@echo "  make run-cli       - Run CLI interface"
	@echo "  make run-gui       - Run GUI interface"
	@echo "  make run-scheduler - Run scheduler"
	@echo "  make config        - Create sample configuration"
	@echo ""
	@echo "Maintenance:"
	@echo "  make update        - Update dependencies"
	@echo "  make backup        - Backup configuration and data"
	@echo "  make restore       - Restore from backup"

# Setup virtual environment and install dependencies
setup:
	@echo "Setting up Speed Test Tool..."
	python3 -m venv speedtest_env
	./speedtest_env/bin/pip install --upgrade pip
	./speedtest_env/bin/pip install -r requirements.txt
	@echo "Applying Python 3.13 compatibility patch..."
	./speedtest_env/bin/python3 fix_speedtest_py313.py || echo "Warning: Patch failed, GUI may not work on Python 3.13"
	@echo "✓ Setup completed"
	@echo "Run 'make install' to install executable scripts"

# Development setup with additional tools
dev-setup: setup
	@echo "Installing development dependencies..."
	./speedtest_env/bin/pip install pytest black flake8 mypy
	@echo "✓ Development setup completed"

# Install executable scripts (requires sudo for system-wide)
install: setup
	@echo "Installing Speed Test Tool..."
	python3 install.py

# Install for current user only
install-user: setup
	@echo "Installing Speed Test Tool (user mode)..."
	python3 install.py --user

# Uninstall
uninstall:
	@echo "Uninstalling Speed Test Tool..."
	python3 uninstall.py

# Uninstall everything including config and data
uninstall-all:
	@echo "Uninstalling Speed Test Tool (including config and data)..."
	python3 uninstall.py --remove-all

# Run applications directly (development mode)
run-cli:
	@echo "Running CLI Speed Test..."
	./speedtest_env/bin/python3 sp.py

run-gui:
	@echo "Running GUI Speed Test..."
	./speedtest_env/bin/python3 speedtest_gui.py

run-scheduler:
	@echo "Running Speed Test Scheduler..."
	./speedtest_env/bin/python3 scheduled_testing.py

# Create sample configuration
config:
	@echo "Creating sample configuration..."
	./speedtest_env/bin/python3 sp.py --create-config
	@echo "✓ Configuration created: speedtest_config.json"

# Basic functionality tests
test: setup
	@echo "Running basic functionality tests..."
	python3 test_installation.py --quick

# Full installation test
test-full: setup
	@echo "Running full installation test suite..."
	python3 test_installation.py

# Test without network
test-offline: setup
	@echo "Running offline installation tests..."
	python3 test_installation.py --no-network

# Update dependencies
update:
	@echo "Updating dependencies..."
	./speedtest_env/bin/pip install --upgrade pip
	./speedtest_env/bin/pip install --upgrade -r requirements.txt
	@echo "Applying Python 3.13 compatibility patch..."
	./speedtest_env/bin/python3 fix_speedtest_py313.py || echo "Warning: Patch failed, GUI may not work on Python 3.13"
	@echo "✓ Dependencies updated"

# Clean temporary files
clean:
	@echo "Cleaning temporary files..."
	find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	find . -name "*.pyo" -delete 2>/dev/null || true
	find . -name ".pytest_cache" -type d -exec rm -rf {} + 2>/dev/null || true
	@echo "✓ Cleaned temporary files"

# Backup configuration and data
backup:
	@echo "Creating backup..."
	mkdir -p backups
	@BACKUP_NAME="speedtest-backup-$$(date +%Y%m%d-%H%M%S)"; \
	mkdir -p "backups/$$BACKUP_NAME"; \
	if [ -f speedtest_config.json ]; then cp speedtest_config.json "backups/$$BACKUP_NAME/"; fi; \
	if [ -f speedtest_history.db ]; then cp speedtest_history.db "backups/$$BACKUP_NAME/"; fi; \
	echo "✓ Backup created: backups/$$BACKUP_NAME"

# Restore from latest backup
restore:
	@if [ ! -d backups ]; then echo "No backups found"; exit 1; fi
	@LATEST_BACKUP=$$(ls -1t backups/ | head -n1); \
	if [ -z "$$LATEST_BACKUP" ]; then echo "No backup files found"; exit 1; fi; \
	echo "Restoring from: $$LATEST_BACKUP"; \
	if [ -f "backups/$$LATEST_BACKUP/speedtest_config.json" ]; then \
		cp "backups/$$LATEST_BACKUP/speedtest_config.json" .; \
		echo "✓ Configuration restored"; \
	fi; \
	if [ -f "backups/$$LATEST_BACKUP/speedtest_history.db" ]; then \
		cp "backups/$$LATEST_BACKUP/speedtest_history.db" .; \
		echo "✓ Database restored"; \
	fi

# Show system information
info:
	@echo "Speed Test Tool - System Information"
	@echo "===================================="
	@echo "Python version: $$(python3 --version)"
	@echo "App directory: $$(pwd)"
	@echo "Virtual env: $$(if [ -d speedtest_env ]; then echo 'Present'; else echo 'Not found'; fi)"
	@echo "Configuration: $$(if [ -f speedtest_config.json ]; then echo 'Present'; else echo 'Not found'; fi)"
	@echo "Database: $$(if [ -f speedtest_history.db ]; then echo 'Present'; else echo 'Not found'; fi)"
	@echo "Installed scripts:"
	@for script in speedtest-cli speedtest-gui speedtest-scheduler; do \
		if command -v $$script >/dev/null 2>&1; then \
			echo "  ✓ $$script: $$(command -v $$script)"; \
		else \
			echo "  ✗ $$script: Not found"; \
		fi; \
	done

# Development shortcuts
lint:
	@echo "Running linters..."
	./speedtest_env/bin/flake8 --max-line-length=100 --ignore=E501 *.py || true
	@echo "✓ Linting completed"

format:
	@echo "Formatting code..."
	./speedtest_env/bin/black --line-length=100 *.py || true
	@echo "✓ Code formatted"

# Service management (requires systemd)
service-install:
	@echo "Installing systemd service..."
	@if [ "$(shell id -u)" -ne 0 ]; then echo "Error: Run as root for system service"; exit 1; fi
	@APP_DIR=$$(pwd); \
	cat > /etc/systemd/system/speedtest.service << EOF; \
[Unit]; \
Description=Speed Test Scheduler; \
After=network.target; \
; \
[Service]; \
Type=simple; \
User=speedtest; \
Group=speedtest; \
WorkingDirectory=$$APP_DIR; \
ExecStart=$$APP_DIR/speedtest_env/bin/python3 $$APP_DIR/scheduled_testing.py --interval 60; \
Restart=on-failure; \
RestartSec=30; \
; \
[Install]; \
WantedBy=multi-user.target; \
EOF
	systemctl daemon-reload
	@echo "✓ Service installed. Enable with: systemctl enable speedtest.service"

service-start:
	@echo "Starting speedtest service..."
	systemctl start speedtest.service
	systemctl status speedtest.service

service-stop:
	@echo "Stopping speedtest service..."
	systemctl stop speedtest.service

service-status:
	systemctl status speedtest.service

# Quick deployment to remote server
deploy:
	@echo "This would deploy to a remote server"
	@echo "Configure your deployment settings first"

# Show recent logs
logs:
	@echo "Recent speed test logs:"
	@if [ -f speedtest.log ]; then tail -20 speedtest.log; else echo "No log file found"; fi