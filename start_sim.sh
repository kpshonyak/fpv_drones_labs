#!/bin/bash
# Запуск симуляції однією командою (Gazebo + SITL + DDS + міст + RViz)
# Використання:
#   ./start_sim.sh                      # світ iris_runway
#   ./start_sim.sh iris_maze            # світ iris_maze

LAUNCH_NAME="${1:-iris_runway}"
DIR="$(cd "$(dirname "$0")" && pwd)"

"$DIR/stop_sim.sh" >/dev/null 2>&1
sleep 1

# Службові файли SITL (mav.parm, eeprom.bin, mav.tlog) лишаються тут, а не в проєкті
mkdir -p "$HOME/sim_run" && cd "$HOME/sim_run" || exit 1

source "$DIR/setup.sh" || exit 1
ros2 launch ardupilot_gz_bringup "${LAUNCH_NAME}.launch.py"
