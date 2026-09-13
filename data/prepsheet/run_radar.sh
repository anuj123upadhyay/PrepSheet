#!/bin/bash
cd "$(dirname "$0")/../.."
python3 ps-shared/scripts/meeting_radar_autonomous.py >> data/prepsheet/logs/radar.log 2>&1
