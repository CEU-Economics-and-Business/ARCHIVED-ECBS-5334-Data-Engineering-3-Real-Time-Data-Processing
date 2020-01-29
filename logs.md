## Logs in Distributed Systems

>This notebook serves as an introduction to how logs work in distributed systems. We then will provide practical applications of these concepts to a variety of common uses: data integration, enterprise architecture, real-time data processing, and data system design.

* * *

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

A file is an array of bytes, a table is an array of records, and a log is really just a kind of table or file where the records are sorted by time

- Logs look like a file or a table. (array of bytes, array of records). However, it is important that we think about the log as an abstract data structure, not a text file

**Key takeaway: Logs record what happened and when!**

* * *

#### Logs in Databases

- Logs usage in databases: keeping in sync a variety of data structures and indexes in the presence of crashes
  - Logs write out information about the database records it will be modifying before applying the changes to all the various data structures that it maintains
  - The log is the record of what happened, and each table or index is a pro‐ jection of this history into some useful data structure or index
  - It is used as the authoritative source in restoring all other persistent structures in the event of a crash
  - Log is a method for replicating data between databases - (the sequence of changes that hap‐ pened on the database is exactly what is needed to keep a remote replica database in sync)
    - Oracle, MySQL, PostgreSQL, and MongoDB include log shipping protocols (replica databases that act as slaves)
    - The slaves can then apply the changes recorded in the log to their own local data structures to stay in sync with the master

**Other use-cases of log:**

1.) Publish/subscribe mechanism to transmit data to other replicas

2.) Consistency mechanism to order the updates that are applied to multiple replicas

* * * 

#### Logs in Distributed Systems 

- The log-centric approach to distributed systems arises from a simple observation

>If two identical, **deterministic** processes begin in the same **state** and get the same inputs in the same order, they will produce the same output and end in the same state.

- **Deterministic:** means that the processing isn’t timing dependent and doesn’t let any other out-of-band input influence its results
- **State:** of the process is whatever data remains on the machine, either in memory or on disk, after our processing

Two deterministic pieces of code => the same input log => the same output => in the same order

**Application in distributed systems:**
- Squeeze all the nondeterminism out of the input stream to ensure that each replica that is processing this input stays in sync

- You can describe the state of each replica by a single number: the `timestamp` for the maximum log entry that it has processed
  - Two replicas at the same time will be in the same state
    - This timestamp combined with the log uniquely capture the entire state of the replica
    - This gives a discrete, event-driven notion of time that, unlike the machine’s local clocks, is easily compara‐ ble between different machines

* * *

#### Log-Centric Designs

- **Physical** (or row-based logging) means logging the contents of each row that is changed
- **Logical** (or statement logging) means not logging the changed rows, but instead logging the SQL commands that lead to the row changes (the insert, update, and delete statements)
- (1) **State Machine Model** is an active-active model, where we keep a log of the incoming requests and each replica processes each request in log order
  - (2) Slightly modified **Primary-Backup Model** elects one replica as the leader. This leader processes requests in the order they arrive and logs the changes to its state that occur as a result of processing the requests. Other replicas apply the state changes that the leader makes so that they will be in sync and ready to take over as leader, should the leader fail.
  
Figure explanation:
  **Primary Backup Model**: The `Master` node handles all reads and writes. Each write is posted to The Log. `Slaves` are subscribed to this log and they apply the changes that the master executed. So if the `Master` fails - a new Master is elected from the `Slaves`

**State Machine Replication Model:** All nodes are peers. Writes first go to The Log and all nodes apply the write in the order determined by The Log.
  
  <img src="https://learning.oreilly.com/library/view/i-heart-logs/9781491909379/assets/ihtl_0103.png" width="400" height="200">



