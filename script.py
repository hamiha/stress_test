import psycopg2
import random
import pandas as pd
from multiprocessing import Process, Value
from datetime import datetime
import glob
import asyncio
import os
import csv

folder_path = '/home'                       # Folder contains the csv files
log_file_path = '/home/test_script/logs'    # Folder contains the log files
number_of_test = 15                         # Number of test per run
step = 50                                   # Number of request increase for each run. exp: 50, 100, 200...


def get_connection_db():
    # Connect to db
    cur = None
    try:
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            database="postgres",
            user="postgres",
            password="test123")
        cur = conn.cursor()

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    if cur is None:
        print('Could not connect to database')
    return cur


def generate_random_value(file_path, number_of_request):
    random_request_list = []
    # Get list of csv files
    list_file = [file for file in glob.glob('{}/*.csv'.format(file_path))]
    # Read random csv file from the list
    df = pd.read_csv(list_file[random.randint(0, len(list_file) - 1)], header=None)
    total_record = len(df.index)

    # Generate random index and get value from csv file
    for i in range(0, number_of_request):
        # Get random row in the chosen csv file
        random_row = random.randint(0, total_record - 1)
        param = df[0][random_row]
        random_request_list.append(param)

    return random_request_list


def call_request(search_param, count):
    # Create and execute query
    query = """select * from sharding where url_hash = '\\x{}'::bytea""".format(search_param)
    db_cursor = get_connection_db()
    try:
        db_cursor.execute(query, (search_param,))
        # Fetch to check if query execute successfully
        data = db_cursor.fetchone()[0]
    except Exception as e:
        # Increase if query failed to execute
        count.value += 1
    # print('Query executed successful')
    db_cursor.close()


async def run_simulate(random_value, request_fn, log_file):
    # Share variables between processes to count the number of fail requests
    count = Value('i', 0)
    proc = []

    # Create Processes to execute query concurrently
    for value in random_value:
        p = Process(target=request_fn, args=(value, count))
        if p is not None:
            proc.append(p)
    for process in proc:
        process.start()
    for p in proc:
        p.join()

    # Create log file of request status
    with open(log_file, 'a') as log:
        writer = csv.writer(log)
        writer.writerow([len(random_value), count.value])


async def run_stress_test(log_file):
    # Generate list number of requests per test
    list_number_of_requests = [i * step for i in range(1, number_of_test + 1)]

    # Run each test with number of request from list
    for number_of_request in list_number_of_requests:
        random_search_value_list = generate_random_value(folder_path, number_of_request)
        # print('>> Done generating random value')
        start_time = datetime.now()
        # print('Start with {} requests at {}'.format(number_of_request, start_time))
        await run_simulate(random_search_value_list, call_request, log_file)
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        # print('Executed took {}'.format(execution_time))

        # Create log file for execution time
        log_execution_name = '{}_execution_time.csv'.format(log_file.split('/')[-1].split('.')[0])
        with open(os.path.join(log_file_path, log_execution_name), 'a') as le:
            writer = csv.writer(le)
            writer.writerow([len(random_search_value_list), execution_time])


async def run_single_test(log_file):
    random_search_value_list = generate_random_value(folder_path, 1)
    start_time = datetime.now()
    print('Start with 1 requests at {}'.format(start_time))
    await run_simulate(random_search_value_list, call_request, log_file)
    end_time = datetime.now()
    print('Executed took {}'.format((end_time - start_time).total_seconds()))


def main():
    # Create log file
    log_file_name = '{}_log.csv'.format(datetime.now().strftime("%m%d%Y_%H%M%S"))

    # Make folder contains log files if not exist
    if not os.path.exists(log_file_path):
        os.makedirs(log_file_path)
    log_file = os.path.join(log_file_path, log_file_name)

    # Run test
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_stress_test(log_file))
    loop.close()


if __name__ == '__main__':
    main()
