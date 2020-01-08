## Amazon Kinesis 

You can use Amazon Kinesis Data Streams to collect and process large streams of data records in real time. 
You can create data-processing applications, known as Kinesis Data Streams applications. 
A typical Kinesis Data Streams application reads data from a data stream as data records. 
These applications can use the Kinesis Client Library, and they can run on Amazon EC2 instances. 
You can send the processed records to dashboards, use them to generate alerts, dynamically change pricing and advertising strategies, or send data to a variety of other AWS services.

### What Can I Do with Kinesis Data Streams?
You can use Kinesis Data Streams for rapid and continuous data intake and aggregation. The type of data used can include IT infrastructure log data, application logs, social media, market data feeds, and web clickstream data. Because the response time for the data intake and processing is in real time, the processing is typically lightweight.

#### Typical scenarios for using Kinesis Data Streams:

**Accelerated log and data feed intake and processing**
>You can have producers push data directly into a stream. For example, push system and application logs and they are available for processing in seconds. This prevents the log data from being lost if the front end or application server fails. Kinesis Data Streams provides accelerated data feed intake because you don't batch the data on the servers before you submit it for intake.

**Real-time metrics and reporting**
>You can use data collected into Kinesis Data Streams for simple data analysis and reporting in real time. For example, your data-processing application can work on metrics and reporting for system and application logs as the data is streaming in, rather than wait to receive batches of data.

**Real-time data analytics**
>This combines the power of parallel processing with the value of real-time data. For example, process website clickstreams in real time, and then analyze site usability engagement using multiple different Kinesis Data Streams applications running in parallel.

**Complex stream processing**
>You can create Directed Acyclic Graphs (DAGs) of Kinesis Data Streams applications and data streams. This typically involves putting data from multiple Kinesis Data Streams applications into another stream for downstream processing by a different Kinesis Data Streams application.


### Benefits of Using Kinesis Data Streams
Although you can use Kinesis Data Streams to solve a variety of streaming data problems, a common use is the real-time aggregation of data followed by loading the aggregate data into a data warehouse or map-reduce cluster.

Data is put into Kinesis data streams, which ensures durability and elasticity. The delay between the time a record is put into the stream and the time it can be retrieved (put-to-get delay) is typically less than 1 second. In other words, a Kinesis Data Streams application can start consuming the data from the stream almost immediately after the data is added. The managed service aspect of Kinesis Data Streams relieves you of the operational burden of creating and running a data intake pipeline. You can create streaming map-reduce–type applications. The elasticity of Kinesis Data Streams enables you to scale the stream up or down, so that you never lose data records before they expire.

Multiple Kinesis Data Streams applications can consume data from a stream, so that multiple actions, like archiving and processing, can take place concurrently and independently. For example, two applications can read data from the same stream. The first application calculates running aggregates and updates an Amazon DynamoDB table, and the second application compresses and archives data to a data store like Amazon Simple Storage Service (Amazon S3). The DynamoDB table with running aggregates is then read by a dashboard for up-to-the-minute reports.

The Kinesis Client Library enables fault-tolerant consumption of data from streams and provides scaling support for Kinesis Data Streams applications.


### Basic Kinesis Data Stream Operations Using the AWS CLI
**Step 1: Create a Stream**
- Your first step is to create a stream and verify that it was successfully created. Use the following command to create a stream named "Foo":

`aws kinesis create-stream --stream-name Foo --shard-count 1`

- The parameter --shard-count is required, and for this part of the tutorial you are using one shard in your stream. Next, issue the following command to check on the stream's creation progress:

`aws kinesis describe-stream --stream-name Foo`

- You should get output that is similar to the following example:
```
{
    "StreamDescription": {
        "StreamStatus": "CREATING",
        "StreamName": "Foo",
        "StreamARN": "arn:aws:kinesis:us-west-2:account-id:stream/Foo",
        "Shards": []
    }
}
```

- In this example, the stream has a status CREATING, which means it is not quite ready to use. Check again in a few moments, and you should see output similar to the following example:

```
{
    "StreamDescription": {
        "StreamStatus": "ACTIVE",
        "StreamName": "Foo",
        "StreamARN": "arn:aws:kinesis:us-west-2:account-id:stream/Foo",
        "Shards": [
            {
                "ShardId": "shardId-000000000000",
                "HashKeyRange": {
                    "EndingHashKey": "170141183460469231731687303715884105727",
                    "StartingHashKey": "0"
                },
                "SequenceNumberRange": {
                    "StartingSequenceNumber": "49546986683135544286507457935754639466300920667981217794"
                }
            }
        ]
    }
}
```

There is information in this output that you don't need to be concerned about for this tutorial. The main thing for now is "StreamStatus": "ACTIVE", which tells you that the stream is ready to be used, and the information on the single shard that you requested. You can also verify the existence of your new stream by using the list-streams command, as shown here:

`aws kinesis list-streams`

- Output:

```
{
    "StreamNames": [
        "Foo"
    ]
}
```

#### Step 2: Put a Record

-  `put-record` puts a single data record containing the text "testdata" into the stream:
`aws kinesis put-record --stream-name Foo --partition-key 123 --data testdata`

- This command, if successful, will result in output similar to the following example:
```
{
    "ShardId": "shardId-000000000000",
    "SequenceNumber": "49546986683135544286507457936321625675700192471156785154"
}
```
> you just added data to a stream! Next you will see how to get data out of the stream.

#### Step 3: Get the Record
Before you can get data from the stream you need to obtain the shard iterator for the shard you are interested in. A shard iterator represents the position of the stream and shard from which the consumer (`get-record` command in this case) will read. You'll use the `get-shard-iterator` command, as follows:

`aws kinesis get-shard-iterator --shard-id shardId-000000000000 --shard-iterator-type TRIM_HORIZON --stream-name Foo`

- Recall that the `aws kinesis` commands have a Kinesis Data Streams API behind them, so if you are curious about any of the parameters shown, you can read about them in the GetShardIterator API reference topic. Successful execution will result in output similar to the following example (scroll horizontally to see the entire output):

```
{
    "ShardIterator": "AAAAAAAAAAHSywljv0zEgPX4NyKdZ5wryMzP9yALs8NeKbUjp1IxtZs1Sp+KEd9I6AJ9ZG4lNR1EMi+9Md/nHvtLyxpfhEzYvkTZ4D9DQVz/mBYWRO6OTZRKnW9gd+efGN2aHFdkH1rJl4BL9Wyrk+ghYG22D2T1Da2EyNSH1+LAbK33gQweTJADBdyMwlo5r6PqcP2dzhg="
}
```

- The long string of seemingly random characters is the shard iterator (yours will be different). You will need to copy/paste the shard iterator into the get command, shown next. Shard iterators have a valid lifetime of 300 seconds, which should be enough time for you to copy/paste the shard iterator into the next command. Notice you will need to remove any newlines from your shard iterator before pasting to the next command. If you get an error message that the shard iterator is no longer valid, simply execute the get-shard-iterator command again.

- The `get-records` command gets data from the stream, and it resolves to a call to GetRecords in the Kinesis Data Streams API. The shard iterator specifies the position in the shard from which you want to start reading data records sequentially. If there are no records available in the portion of the shard that the iterator points to, GetRecords returns an empty list. Note that it might take multiple calls to get to a portion of the shard that contains records.

- In the following example of the get-records command (scroll horizontally to see the entire command):
``` aws kinesis get-records --shard-iterator AAAAAAAAAAHSywljv0zEgPX4NyKdZ5wryMzP9yALs8NeKbUjp1IxtZs1Sp+KEd9I6AJ9ZG4lNR1EMi+9Md/nHvtLyxpfhEzYvkTZ4D9DQVz/mBYWRO6OTZRKnW9gd+efGN2aHFdkH1rJl4BL9Wyrk+ghYG22D2T1Da2EyNSH1+LAbK33gQweTJADBdyMwlo5r6PqcP2dzhg=
```
- If you are running this tutorial from a Unix-type command processor such as bash, you can automate the acquisition of the shard iterator using a nested command, like this (scroll horizontally to see the entire command):
```
SHARD_ITERATOR=$(aws kinesis get-shard-iterator --shard-id shardId-000000000000 --shard-iterator-type TRIM_HORIZON --stream-name Foo --query 'ShardIterator')

aws kinesis get-records --shard-iterator $SHARD_ITERATOR
```
- If you are running this tutorial from a system that supports PowerShell, you can automate acquisition of the shard iterator using a command such as this (scroll horizontally to see the entire command):

```
aws kinesis get-records --shard-iterator ((aws kinesis get-shard-iterator --shard-id shardId-000000000000 --shard-iterator-type TRIM_HORIZON --stream-name Foo).split('"')[4])
```

- The successful result of the get-records command will request records from your stream for the shard that you specified when you obtained the shard iterator, as in the following example (scroll horizontally to see the entire output):

```
{
  "Records":[ {
    "Data":"dGVzdGRhdGE=",
    "PartitionKey":"123”,
    "ApproximateArrivalTimestamp": 1.441215410867E9,
    "SequenceNumber":"49544985256907370027570885864065577703022652638596431874"
  } ],
  "MillisBehindLatest":24000,
  "NextShardIterator":"AAAAAAAAAAEDOW3ugseWPE4503kqN1yN1UaodY8unE0sYslMUmC6lX9hlig5+t4RtZM0/tALfiI4QGjunVgJvQsjxjh2aLyxaAaPr+LaoENQ7eVs4EdYXgKyThTZGPcca2fVXYJWL3yafv9dsDwsYVedI66dbMZFC8rPMWc797zxQkv4pSKvPOZvrUIudb8UkH3VMzx58Is="
}
```

#### Step 4: Clean Up
- Finally, you'll want to delete your stream to free up resources and avoid unintended charges to your account, as previously noted. Do this in practice any time you have created a stream and will not be using it because charges accrue per stream whether you are putting and getting data with it or not. The clean-up command is simple:

`aws kinesis delete-stream --stream-name Foo`

- Success results in no output, so you might want to use describe-stream to check on deletion progress:

`aws kinesis describe-stream --stream-name Foo`

- If you execute this command immediately after the delete command, you will likely see output similar to the following example:
```
{
    "StreamDescription": {
        "StreamStatus": "DELETING",
        "StreamName": "Foo",
        "StreamARN": "arn:aws:kinesis:us-west-2:account-id:stream/Foo",
        "Shards": []
    }
}
```
- After the stream is fully deleted, describe-stream will result in a "not found" error:
```
A client error (ResourceNotFoundException) occurred when calling the DescribeStream operation: 
Stream Foo under account 112233445566 not found.
```

