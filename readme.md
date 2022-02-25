# Project

## Description
Python script to run a stress test to find out how many requests the server can handle before stopping responding

## Requirements
- Python3
- Pandas
- pip glob
- pip csv
- pip psycopg2

> You can simply install pip packages if missing any with command 'pip install name_of_the_library'

## Run test
```
cd test_script
python3 script.py
```
To change the number of tests per run or number of request increases for each test, please open the script and modify the value
```
number_of_test = 15                         # Number of test per run
step = 50                                   # Number of request increase for each run. exp: 50, 100, 200..
```

## Logs
Log files are contained in the 'logs' folder. There are two types of log:
- Number of failed requests: counts the number of requests that failed to get the response from the database in each test. Naming convention %m%d%Y_%H%M%S_log.csv
- Execution time: the total time from the beginning to the end of each test. Naming convention %m%d%Y_%H%M%S_log_execution_time.csv

## Discussion
### Hardware limited
To simulate a large number of requests per second. I used the multiprocessing in Python

In the beginning, I start with 500 requests per second and the server ran just fine but the execution time to finish was more than 10 seconds. After taking a deeper look, I found out that the hardware of the server is not enough to handle that many processes running at the same time so all of the requests did not actually run in one second. The new process has to wait to be allocated in the CPU in order to run. Hence the total execution time was far more than one second.

![Alt text](images/1.png?raw=true "Title")

As you can see in the picture, the CPU was running at full capacity with 500 processes. 

![Alt text](images/2.png?raw=true "Title")

Then it stopped at 1000 requests. 

First, I thought it was the problem of too many processes that tried to read and write on the same log file but even after removing the code of writing log file, the result did not change.
Then I checked the step where the script read a random CSV file to get a random search value, and it was fine, it was not the cause of the problem. 

So far, I concluded the problem was the hardware of the server could not handle that many processes running at the same time. One of the reasons could be the Python language since it was not optimized for parallel running.
In the end, I tried with a smaller number of requests per second to get the log files, and it stopped at 550 requests.

![Alt text](images/3.png?raw=true "Title")

### Graphs
Even though the script stopped running but none of the request failed to get the response.

![Alt text](images/graph.png?raw=true "Title")

### Architecture/Software
We could create a queue system to store all the requests then distribute them to the server with a number of requests each time where it can handle. In this way, the response time of the request may increase since it has to wait in the queue for the server to process but on the other hand, the server will not stop/crash with too many requests per second.


