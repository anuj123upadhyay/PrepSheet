#!/bin/bash
cd "$(dirname "$0")/../.."
python3 ps-shared/scripts/dawn_autonomous.py >> data/prepsheet/logs/dawn.log 2>&1
