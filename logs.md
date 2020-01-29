### Logs in Distributed Systems

>This notebook serves as an introduction to how logs work in distributed systems. We then will provide practical applications of these concepts to a variety of common uses: data integration, enterprise architecture, real-time data processing, and data system design.

#### Overview

#### Log

<a href="https://learning.oreilly.com/library/view/i-heart-logs/9781491909379/assets/ihtl_0101.png" width="400" height="400></a>
                                                                                                           
- Log is a series of loosely structured requests, errors, or other messages in a sequence of rotating text files
- Humans do not read logs, it's not manageable when services and servers are involved
  - The purpose of logs quickly is an input to queries and graphs to understand behavior across many machines
