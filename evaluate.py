import sqlite3
import time 
import ollama
import re

def create_connection(db_file):
    conn = sqlite3.connect(db_file)

    return conn

def evaulate_model_with_temp_and_epoch_on_dataset(dataset, model, temperature, epoch):
    '''
    THis is a sample
    '''
    conn = create_connection(f'./Results/{dataset.name}_result.db')

    create_table = """
    CREATE TABLE IF NOT EXISTS results (
        id INTEGER PRIMARY KEY,
        model TEXT NOT NULL,
        epoch INTEGER NOT NULL,
        temp REAL NOT NULL,
        leftId INTEGER NOT NULL,
        rightId INTEGER NOT NULL,
        result REAL NOT NULL,
        response BLOB NOT NULL,
        duration REAL NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """

    conn.execute(create_table)
    
    for leftId in range(len(dataset)):
        for rightId in range(leftId, len(dataset)):
            if leftId != rightId:

                start = time.time()

                (result, response) = evaluate_record(dataset=dataset, model=f'{model}_Temp_{temperature}:latest', leftId=leftId, rightId=rightId)

                end = time.time()

                insert_record = f"""
                INSERT INTO results (model, epoch, temp, leftId, rightId, result, response, duration)
                VALUES ('{model}', {epoch}, {temperature}, {leftId}, {rightId}, {result}, "{remove_special_chars(response)}", {end - start});
                """

                print(insert_record)

                conn.execute(insert_record)

                conn.commit()
    
    conn.close()

def evaluate_record(dataset, model, leftId, rightId):
    message = convert_to_message(dataset, leftId) + convert_to_message(dataset, rightId)

    response = ollama.chat(model, messages=[
        {
            'role': 'user',
            'content': message,
        },
    ])

    return (parse_response(response['message']['content']), response['message']['content'])

def convert_to_message(dataframe, id):
    cols = dataframe.columns

    record = dataframe.loc[id]

    message = ""

    for col in cols:
        message += col + ": " + str(record[col]) + "\n"

    return message

def find_last_float(s):
    matches = re.findall(r' 0\.[0-9]+', s)
    return float(matches[-1]) if matches else -1

def parse_response(response):
    return find_last_float(response)

def remove_special_chars(s):
    allowed_chars = set(".,:- ")

    s = s.replace("\n", " ")

    # Filter out special characters
    cleaned_string = "".join(c for c in s if  c.isalnum() or c in allowed_chars or c == " ")

    return cleaned_string

print(remove_special_chars("Hello\nHi 123 - 1 ][]"))