#!/data/data/com.termux/files/usr/bin/bash
cd ~/pond
termux-wake-lock
echo "[$(date)] Starting POND..." >> nohup.out
# kill old
pkill -f pond.py || true
sleep 1
# run forever loop so if it crashes it restarts
while true; do
  python pond.py >> nohup.out 2>&1
  echo "[$(date)] pond.py exited with $?, restarting in 5s..." >> nohup.out
  sleep 5
done
