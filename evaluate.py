DEFAULT_EPOCHS = 5

import sqlite3
import time 

def create_connection(db_file):
    conn = sqlite3.connect(db_file)

    return conn

def evaulate_dataset(dataset, models, prompt):
    # create db
    conn = create_connection(f'./Results/{dataset.name}_result.db')

    # create table
    create_table = """
    CREATE TABLE IF NOT EXISTS results (
        id INTEGER PRIMARY KEY,
        model TEXT NOT NULL,
        epoch INTEGER NOT NULL,
        temp REAL NOT NULL,
        leftId INTEGER NOT NULL,
        rightId INTEGER NOT NULL,
        result TEXT NOT NULL,
        duration REAL NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """

    conn.execute(create_table)

    for model in models:
        for epoch in range(1, DEFAULT_EPOCHS + 1):
            for temp in range(1, 11):
                for leftId in range(len(dataset)):
                    for rightId in range(len(dataset)):
                        if leftId != rightId:

                            start = time.time()

                            result = evaluate_record(dataset, model, temp/10, leftId, rightId)

                            end = time.time()

                            insert_record = f"""
                            INSERT INTO results (model, epoch, temp, leftId, rightId, result, duration)
                            VALUES ('{model}', {epoch}, {temp/10}, {leftId}, {rightId}, {result}, {end - start});
                            """

                            conn.execute(insert_record)

    conn.commit()
    conn.close()

def evaluate_record(dataset, model, temp, leftId, rightId):
    message = convert_to_message(dataset, leftId) + convert_to_message(dataset, rightId)

    return "0"

def convert_to_message(dataframe, id):
    cols = dataframe.columns

    record = dataframe.loc[id]

    message = ""

    for col in cols:
        message += col + ": " + str(record[col]) + "\n"

    return message