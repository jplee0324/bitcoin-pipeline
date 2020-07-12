# Cryptocurrency Trade Data Pipeline


This project focuses on collecting data regarding all buy and sell orders that are met in the Bitcoin/USDT in the cryptocurrency exchange Binance. Data is read and after going through the pipelining process, is ultimately visualized in a QuickSight dashboard at the end so that we can gain insight into how the market behaves.


**Overall General Workflow:**


Websocket Stream -> Kafka (running on EC2) -> S3 Bucket (through Vector sink) -> Amazon RDS (after processed by Lambda function)


--------


# Data Pipeline
The source of the data for the pipeline is a WebSocket connection opened up to the endpoint **wss://stream.binance.com:9443** and subscribing to a stream involving transactions being met in the Bitcoin to USDT market.


This stream reads in JSON data that describes the trade that took place:
```javascript
{
  "e": "aggTrade",  // Event type
  "E": 123456789,   // Event time
  "s": "BNBBTC",    // Symbol
  "a": 12345,       // Aggregate trade ID
  "p": "0.001",     // Price
  "q": "100",       // Quantity
  "f": 100,         // First trade ID
  "l": 105,         // Last trade ID
  "T": 123456785,   // Trade time
  "m": true,        // Is the buyer the market maker?
  "M": true         // Ignore
}
```


Due to the limitations of Amazon Web Services' "Free Tier," Kinesis streaming was not an option for this pipeline. Instead, a Kafka producer was run on an EC2 instance which logged the JSON data read in by the WebSocket stream. Due to limited memory in the EC2 instance, this Kafka topic has a retention of only 5 minutes.


The open-source tool Vector was used to act as a **sink** from the source(Kafka) to an S3 bucket. The configuration in **vector.toml** partitions the data being logged by the Kafka producer into separate files in the S3 bucket by 60 second intervals. Each file dropped into the S3 bucket contains a timestamp of the Date and Hour and Minute that the file was created. So basically, every minute, a new file is dropped into the S3 bucket with a timestamp.


When ever an object is put into the S3 bucket, a Lambda function is triggered and processes the log file from that contains all the data from the past minute. All of the transactions are aggregated into one row and inserted into a MySQL database hosted in Amazon RDS with a schema of:

| Column Name | Description |
| ----------- | ------ | 
| TIME | time showing the date, hour and minute the transactions were gathered |
| TOTAL_COUNT_BUY | total number of buy orders met |
| TOTAL_COUNT_SELL | total number of sell orders met |
| TOTAL_BTC_BUY | total sum of BTC from buy orders |
| TOTAL_BTC_SELL | total sum of BTC from sell orders | 
| TOTAL_USD_BUY| total sum in USD for buy orders |
| TOTAL_USD_SELL | total sum in USD for sell orders | 

As data points were collected over days, the data in the MySQL database was visualized on a QuickSight dashboard. This dashboard shows how different metric relating to the volume of buy and sell orders and spread between them may be able to help explain very short term fluctuations in exchange prices.

A sample of the dashboard after running the pipeline for a few days is provided below.

![dashboard](/images/CryptoPipelineDashboard.png)


