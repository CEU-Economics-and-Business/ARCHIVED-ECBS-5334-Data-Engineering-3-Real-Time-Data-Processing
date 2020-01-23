Things to be covered in this markdown but are missing:
- JSON files
- Spark Shuffle partitions , shuffle recap
- Schema recap
- Batch vs stream processing
- Sockets
- Joins
- Windowing

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
#  splitting the lines into individual words and then count them
   words = lines.select(split(col("value"), "\s").alias("word"))
          counts = words.groupBy("word").count()
```
- Note that the above DataFrame operations to transform the lines streaming DataFrame would work in the exact same way if lines were a batch DataFrame


To understand which operations are supported in Structured Streaming, you have to recognize the two broad classes of data transformations.

>**Stateless transformations:** Operations like `select`, `filter`, `map`, etc. do not require any information from previous rows to process the next row; each row can be processed by itself. The lack of previous “state” in these operation make them stateless. Stateless operations can be applied to both batch and streaming DataFrames. For instance, the flatMap operation in our code snippet is a stateless operation.

>**Stateful transformations:** In contrast, an aggregation operation like count in the above snippet requires maintaining state to combine data across multiple rows. More specifically, any DataFrame operation involving `grouping`, `joining` or `aggregations` are stateful transformations. While many of these operations are supported in Structured Streaming, a few combinations of them are not supported because it is either computationally hard, or infeasible to compute them in an incremental manner.

#### STEP 3: DEFINE OUTPUT SINK AND OUTPUT MODE
After transforming the data, we can define how to write the processed output data with DataFrame.writeStream.

```python
    writer = ( counts.writeStream
          .format("console")
          .outputMode("complete") )
```

Here we have specified “console” as the output streaming sink and “complete” as the output mode. The output mode of a streaming query specifies what part of the updated output to write out after processing new input data.

- .outputMode **("complete")** ==  All the rows of the result table/DataFrame will be outputted at the end of every trigger. This is supported by queries where the result table is likely to be much smaller than the input data and is therefore feasible to be retained in memory

- .outputMode **("append")** == This is the default mode, where only the new rows added to the result table/DataFrame (for example, the counts table) since the last trigger will be outputted to the sink.

- .outputMode **("update")** == Only the rows of result that were updated since the last trigger will be outputted at the end of every trigger

**Besides writing the output to the console, Structured Streaming natively supports streaming writes to:**
- Files
- Apache Kafka
- In addition, you can write to arbitrary locations using the `foreachBatch` and `foreach` API methods

#### STEP 4: SPECIFY PROCESSING DETAILS

Now, we have to decide how we will go about processing the data. Processing details are as follows:

Here we have specified two details using the `DataStreamWriter` that we had created with `DataFrame.writeStream`.

```python
checkpoint_dir = "..."
     writer2 = ( writer
     .trigger(Trigger.ProcessingTime("1 second"))
     .option("checkpointLocation", checkpoint_dir))
```

Now let's explain our options here when it comes to triggering details (processing of newly available streaming data):

1.) **ProcessingTime**
- `ProcessingTime` with or without a trigger interval e.g `Trigger.ProcessingTime("1 second")`
  - This is the default mode
    - By default, when no trigger is specified, a query triggers the next micro-batch as soon as the previous micro-batch has completed
    - Alternatively, you can explicitly specify the `ProcessTime` trigger with an interval, and the query will trigger micro-batches at that fixed internal

2.) **Once**
- In this mode, the streaming query will execute exactly one micro-batch - it processes all the new data available in a single batch and then stops itself. For example, it's great when you want to control cost by only executing a query once per day. 

3.) **Continuous**
- While only a small subset of DataFrame operations allow this mode to be used, it can provide much lower latency (as low as milliseconds) than the micro-batch trigger modes. 

4.) **Checkpoint location**
- This is a directory in any HDFS-compatible file system where a streaming query saves its progress information, that is, what data has been successfully processed. **Upon failure, this metadata is used to restart the failed query exactly where it left off.** Therefore, setting this option is necessary for failure recovery with exactly-once guarantees.

#### STEP 5: STARTING THE QUERY

Now, we've specified everything - we can start the query.

```python
 streaming_query = writer2.start()
 ```
 The returned instance of type `StreamingQuery` represents an active query and can be used to manage the query.

1.) `start()` is a non-blocking method, so it will return as soon as the query has been started in the background.

2.) If you want the main thread to block until the streaming query has terminated, you can use `streamingQuery.awaitTermination()`.

3.)  If the query fails in the background with an error,`awaitTermination()` will also fail with that same exception

4.) You can wait up to a time out duration using `awaitTermination(timeoutMillis)`

5.) You can explicitly stop the query with `streamingQuery.stop()`.


#### STEP 6: PUTTING IT ALL TOGETHER
Here's what we have done so far:

```python

# STEP 1
spark = SparkSession...
      lines = ( spark
      .readStream.format("socket")
      .option("host", "localhost")
       .option("port", 9999)
       .load() )
       
# STEP 2
      words = lines.select(split(col("value"), "\s").alias("word"))
      counts = words.groupBy("word").count()

# STEP 3
       checkpoint_dir = "..."
      streaming_query = ( 
      counts.writeStream
      .format("console")
      .outputMode("complete")
# STEP 4
       .trigger(processingTime = "1 second"))
       .option("checkpointLocation", checkpoint_dir)

# STEP 5
      .start() )
      streaming_query.awaitTermination()
```

- After the query has started, a background thread continuously reads new data from the streaming source, processes it, and writes it to the streaming sinks 
          


