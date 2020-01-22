### Spark Structured Streaming

- Structured Streaming is built atop the Spark SQL engine and DataFrame-based APIs
- A stream is viewed as a continually growing table, with new rows of data appended at the end. 
  - Since it's a structured table, you can issue queries against it 
- This structured model obviated the old DStreams model
- Underneath the structured streaming model, the Spark SQL core engine handles all aspects of fault-tolerance and late-data semantics
- Streaming data sources include Apache Kafka, Kinesis, and HDFS-based or cloud storage
- Structured Streaming was designed from scratch with one core philosophy -- for developers, writing stream processing pipelines should be as easy as writing batch pipelines. 


### Introduction
Data pipeline in its core concept is a chain of different sources and processors in a logical flow that takes source data in its raw form into a process form that can be consumed by the application. There are data sources everywhere: around your enterprise, connected devices, connected cars, sensors, user tracking - coming at fast pace. Companies want to get inside and see what is happening with the data that they have in their hands and they want to do it as fast as possible to understand what people are doing with e.g their applications real time. 

##### Some companies using Stuctured Streaming for the following:
- **Sensors** in vehicles, industrial equipment, and machinery send data to streaming for a performance measurement
- A website tracking **geo-location** data from customer's phones, which is gathered by streaming, so the website can make recommendation of which restaurants to visit
- Solar power company monitoring panel performance through streaming
- Online gaming company collecting streaming data about player-game interactions

>A lot of applications use continously-updated data.

The problem is that it's not possible to start writing the data to a large database or a Hadoop cluster and then applying some transformation logic at the end of the day or week to extract value. Data is generated continously from many sources simultainously and is coming in in kilobyte scale. Companies want to take the data and extract that value right away as **data value decays with time**.

#### Popular Streaming Tools:
- Storm - for high velocity data streaming
- Flink - distributed computation
- **Kinesis** - Amazon out of the box streaming tool. Minimal setup, minimal maintainance effort. Not free.
- Samza - Kafka features, callback API, streaming tool
- Kafka - Reliability with handling terabyte of data. Completely free. Developed by LinkedIn.
- **Apache Spark** - Jack of All Trades. Master of more than a few.
  - General purpose, widely used
  - Connects with a lot of the previously mentioned streaming tools
  - Fault tolterant thanks to projects like HDFS
  - Allows for tracking frequently-updated datasets
    - **Example:** Can use it to track most popular hashtags in 5 mins windows based on their counts in a Twitter stream, and by using the `StreamingContext` function.
    
    
### Five Steps to Define a Streaming Query

#### STEP 1 - DEFINE INPUT SOURCES
- As with batch queries, the first step is to define a DataFrame from a streaming source
- Here is an example of creating a DataFrame from a text data stream to be received over a socket connection.
```python
    spark = SparkSession…
           lines = ( spark
           .readStream.format("socket")
           .option("host", "localhost")
           .option("port", 9999)
           .load() )
```
Note: this does not immediately start reading the streaming data; it only sets up the configurations necessary for reading the data once the streaming query is explicitly started.


#### STEP 2 - TRANSFORM DATA

```python
   words = lines.select(split(col("value"), "\s").alias("word"))
          counts = words.groupBy("word").count()
```







