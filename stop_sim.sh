#!/bin/bash
# Зупинка всіх компонентів симуляції
for p in "gz sim" "sim_vehicle.py" "arducopter" "mavproxy" \
         "micro_ros_agent" "micro-xrce-dds-agent" "rviz2" \
         "robot_state_publisher" "parameter_bridge"; do
    pkill -f "$p" 2>/dev/null
done
sleep 1
for p in "gz sim" "arducopter" "micro_ros_agent" "rviz2"; do
    pkill -9 -f "$p" 2>/dev/null
done
echo "Усі процеси симуляції зупинено."
