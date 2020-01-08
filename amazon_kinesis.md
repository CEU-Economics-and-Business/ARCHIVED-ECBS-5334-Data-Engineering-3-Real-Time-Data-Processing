## Amazon Kinesis 

You can use Amazon Kinesis Data Streams to collect and process large streams of data records in real time. 
You can create data-processing applications, known as Kinesis Data Streams applications. 
A typical Kinesis Data Streams application reads data from a data stream as data records. 
These applications can use the Kinesis Client Library, and they can run on Amazon EC2 instances. 
You can send the processed records to dashboards, use them to generate alerts, dynamically change pricing and advertising strategies, or send data to a variety of other AWS services.

#### What Can I Do with Kinesis Data Streams?
You can use Kinesis Data Streams for rapid and continuous data intake and aggregation. The type of data used can include IT infrastructure log data, application logs, social media, market data feeds, and web clickstream data. Because the response time for the data intake and processing is in real time, the processing is typically lightweight.

Typical scenarios for using Kinesis Data Streams:

**Accelerated log and data feed intake and processing**
>You can have producers push data directly into a stream. For example, push system and application logs and they are available for processing in seconds. This prevents the log data from being lost if the front end or application server fails. Kinesis Data Streams provides accelerated data feed intake because you don't batch the data on the servers before you submit it for intake.

**Real-time metrics and reporting**
>You can use data collected into Kinesis Data Streams for simple data analysis and reporting in real time. For example, your data-processing application can work on metrics and reporting for system and application logs as the data is streaming in, rather than wait to receive batches of data.

**Real-time data analytics**
>This combines the power of parallel processing with the value of real-time data. For example, process website clickstreams in real time, and then analyze site usability engagement using multiple different Kinesis Data Streams applications running in parallel.

**Complex stream processing**
>You can create Directed Acyclic Graphs (DAGs) of Kinesis Data Streams applications and data streams. This typically involves putting data from multiple Kinesis Data Streams applications into another stream for downstream processing by a different Kinesis Data Streams application.
