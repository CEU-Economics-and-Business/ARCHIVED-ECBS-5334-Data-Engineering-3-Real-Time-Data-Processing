## Logs in Distributed Systems

>This notebook serves as an introduction to how logs work in distributed systems. We then will provide practical applications of these concepts to a variety of common uses: data integration, enterprise architecture, real-time data processing, and data system design.

* * *

### Overview

#### Log

<img src="https://learning.oreilly.com/library/view/i-heart-logs/9781491909379/assets/ihtl_0101.png" width="400" height="200">
                                                                                                         
                                                                                                           
- Log is a series of loosely structured requests, errors, or other messages in a sequence of rotating text files
- Humans do not read logs, it's not manageable when services and servers are involved
  - The purpose of logs is an input to queries and graphs to understand behavior across many machines
- The log we are discussing - also known as - `commit log` or `journal` is an **append-only** sequence of records ordered by time

<img src="https://learning.oreilly.com/library/view/i-heart-logs/9781491909379/assets/ihtl_0102.png" width="400" height="200">

- Each rectangle represents a record that was appended to the log
- Records are stored in the order they were appended
- Reads proceed from left to right
- Each entry appended to the log is assigned a unique, sequential log entry number that acts as its unique key
- The ordering of records defines a notion of “time” 
  - Entries to the left are defined to be older then entries to the right
  - The log entry number can be thought of as the “timestamp” of the entry

>A file is an array of bytes, a table is an array of records, and a log is really just a kind of table or file where the records are sorted by time

- Logs look like a file or a table. (array of bytes, array of records). However, it is important that we think about the log as an abstract data structure, not a text file

<center>The question is - Why study logs?</center>
<p style="text-align: center;">They record what happened and when</p>








