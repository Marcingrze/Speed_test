# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Simple Python script for testing internet connection speed using the speedtest-cli library.

## Environment Setup

The project uses a Python virtual environment named `ebv/`:

```bash
# Activate the virtual environment
source ebv/bin/activate

# Install dependencies (if needed)
pip install -r requirements.txt
```

## Running the Application

```bash
# Activate virtual environment first
source ebv/bin/activate

# Run the speed test
python sp.py
```

The script will:
1. Connect to speedtest servers
2. Find the best server
3. Measure download and upload speeds
4. Display results in Mbps

## Architecture

- **sp.py**: Single-file script that uses the `speedtest` library to:
  - Initialize a Speedtest object
  - Automatically select the best server
  - Perform download and upload speed tests
  - Format and display results (converts from bits/s to Mbps)

## Dependencies

- `speedtest-cli==2.1.3`: Library for testing internet bandwidth using speedtest.net
