from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
import mysql.connector

sc = SparkContext(appName = "btcTradesStream")
ssc = StreamingContext(sc, 60)

kvs = KafkaUtils.createStream(ssc, 'zookeeper_server:2181', 'spark-streaming', {'btcTrades':1})


