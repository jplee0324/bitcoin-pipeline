nohup vector --config /home/ubuntu/crypto-trade-pipeline/vector.toml &
sleep 2

nohup python3 Listener.py &
