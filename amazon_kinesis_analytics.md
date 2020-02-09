[Home](./README.md) | 
[Logs](./logs.md) | 
[Amazon Kinsesis](./amazon_kinesis.md) | 
[Kinsesis Analytics](./amazon_kinesis_analytics.md) | 
[Help/Resources](./resources.md).


For a Detailed Description of Kinesis Analytics, please check out the page on the <a href="https://aws.amazon.com/kinesis/data-analytics/">AWS website.</a>

Here is the code we are using in the class:

```

-- ** Continuous Filter ** 
-- Performs a continuous filter based on a WHERE condition.
--          .----------.   .----------.   .----------.              
--          |  SOURCE  |   |  INSERT  |   |  DESTIN. |              
-- Source-->|  STREAM  |-->| & SELECT |-->|  STREAM  |-->Destination
--          |          |   |  (PUMP)  |   |          |              
--          '----------'   '----------'   '----------'               
-- STREAM (in-application): a continuously updated entity that you can SELECT from and INSERT into like a TABLE
-- PUMP: an entity used to continuously 'SELECT ... FROM' a source STREAM, and INSERT SQL results into an output STREAM
-- Create output stream, which can be used to send to a destination
CREATE OR REPLACE STREAM "myanalyticsstream" (
    event_time VARCHAR(32),
    country   VARCHAR(32),
    country_alpha VARCHAR(4),
    amount_eur INTEGER);
-- Create pump to insert into output 
CREATE OR REPLACE PUMP "STREAM_PUMP" AS INSERT INTO "myanalyticsstream"
-- Select all columns from source stream
SELECT STREAM "event_time", "country", "country_alpha", "amount_eur"
FROM "SOURCE_SQL_STREAM_001"
-- LIKE compares a string to a string pattern (_ matches all char, % matches substring)
-- SIMILAR TO compares string to a regex, may use ESCAPE
WHERE "country" NOT IN ('HU', 'RO');
```
