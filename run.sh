nohup /home/ubuntu/kafka_2.12-2.5.0/bin/zookeeper-server-start.sh /home/ubuntu/kafka_
2.12-2.5.0/config/zookeeper.properties > ./logs/zookeeper-logs &
sleep 2

nohup /home/ubuntu/kafka_2.12-2.5.0/bin/kafka-server-start.sh /home/ubuntu/kafka_2.12
-2.5.0/config/server.properties > ./logs/kafka-logs &
sleep 2

vector --config /home/ubuntu/crypto-trade-pipeline/vector.toml &
sleep 2

python3 Listener.py &
