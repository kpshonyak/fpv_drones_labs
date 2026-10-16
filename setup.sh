# Usage: source ~/fpv_labs/setup.sh

if [ -n "$ZSH_VERSION" ]; then
   SHELL_EXT=zsh
else
   SHELL_EXT=bash
fi

WORKSPACE_FOLDER=${WORKSPACE_FOLDER:-$HOME}
ARDU_WS=$HOME/ardu_ws

export GZ_VERSION=harmonic
export PATH=/usr/lib/ccache:$PATH
export PATH=$PATH:$HOME/Micro-XRCE-DDS-Gen/scripts

source /opt/ros/humble/setup.$SHELL_EXT
source $ARDU_WS/install/setup.$SHELL_EXT
source $WORKSPACE_FOLDER/fpv_labs/install/setup.$SHELL_EXT

# Щоб Gazebo знаходив моделі за URI package://ardupilot_gazebo/
export SDF_PATH=$ARDU_WS/install/ardupilot_gazebo/share:$SDF_PATH
export GZ_SIM_RESOURCE_PATH=$ARDU_WS/install/ardupilot_gazebo/share:$GZ_SIM_RESOURCE_PATH
