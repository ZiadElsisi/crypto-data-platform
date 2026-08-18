import os
import duckdb
import datetime
import pandas as pd

import logging

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DB_DIR = os.path.join(BASE_DIR, "..", "..", "DuckDB")
DB_Path = os.path.join(DB_DIR,"CMC.duckdb")

os.makedirs(DB_DIR, exist_ok=True)

Table_Schemes = {
    "Real_time":{
        "Table":"CMC_Real_time",
        "Scheme" : '''
                        id                   INTEGER  ,
                        name                 VARCHAR NOT NULL,
                        symbol               VARCHAR NOT NULL,
                        cmc_rank             INTEGER,
                        last_updated         TIMESTAMPTZ,
                        circulating_supply   DOUBLE,
                        max_supply           DOUBLE,
                        price                DOUBLE,
                        market_cap           DOUBLE,
                        volume_24h           DOUBLE,
                        volume_change_24h    DOUBLE,
                        percent_change_1h    DOUBLE,
                        percent_change_24h   DOUBLE,
                        percent_change_7d    DOUBLE,
                        market_cap_dominance DOUBLE,
                        percent_change_90d   DOUBLE,
                        Date_of_file         TIMESTAMPTZ  ,
                        PRIMARY KEY (id,Date_of_file)
        
        '''
    },
    "Historical":{
        "Table":"CMC_Historical",
        "Scheme" : '''
                        id                  INT            ,
                        name                VARCHAR(100)    NOT NULL,
                        symbol              VARCHAR(20)     NOT NULL,
                        cmc_rank            INTEGER,
                        last_updated        TIMESTAMPTZ,
                        circulating_supply  DOUBLE,
                        max_supply          DOUBLE,
                        price               DOUBLE,
                        market_cap          DOUBLE,
                        volume_24h          DOUBLE,
                        percent_change_1h   DOUBLE,
                        percent_change_24h  DOUBLE,
                        percent_change_7d   DOUBLE,
                        Date_of_file         TIMESTAMPTZ  ,
                        PRIMARY KEY (id,Date_of_file)
        '''
    }

}
def Create_CMC_DuckDB ():


    if os.path.exists(f"{DB_DIR}/CMC.duckdb"):
        logging.info(f"CMC.duckdb already exists")
    else:
        conn = duckdb.connect(f"{DB_DIR}/CMC.duckdb")
        conn.execute(f"""CREATE TABLE CMC_Real_time ({Table_Schemes["Real_time"]['Scheme']} );
                        CREATE TABLE CMC_Historical ({Table_Schemes["Historical"]['Scheme']});
                        """)
        conn.close()
    return


def Update_CMC_DuckDB (action="ignore"):

    if not os.path.exists(os.path.join(DB_Path)) :
        raise FileNotFoundError(f"Database  does not exist")


    conn = duckdb.connect(DB_Path)
    for DataCategory in ["Real_time","Historical"]:
        Processed_DIR = os.path.join(BASE_DIR,"..","..","data","processed","CMC",DataCategory)
        if not os.path.exists(Processed_DIR):
            logging.warning(f"Processed Directory for {DataCategory} does not exist")
            continue


        files = os.listdir(Processed_DIR)
        for file in files:
            if file.endswith(".csv"):
                file_name=file.replace(".csv","")
                file_name_tstmp = datetime.datetime.strptime(file_name, "%Y-%m-%d_%H-%M-%S")
                if action == "ignore":
                    conn.execute(f"""INSERT OR IGNORE INTO CMC_{DataCategory}  
                                    Select *,'{file_name_tstmp}' from '{Processed_DIR}/{file}' """)
                elif action == "update":
                    conn.execute(f"""INSERT OR UPDATE INTO CMC_{DataCategory}  
                                    Select *,'{file_name_tstmp}' from '{Processed_DIR}/{file}' """)
                else :
                    raise ValueError(f"Invalid action {action}")
            else: continue

        final =conn.execute(f"""select * from CMC_{DataCategory}""").df()
        print(final)
        print("Successfully updated")
        print("-"*220)

    conn.close()


def verify_load(path,d_type):
    if not os.path.isfile(path): ## Checks if there is a file there
        raise FileNotFoundError(f"File {path} does not exist")

    conn = duckdb.connect(DB_Path)
    df_rows_count = pd.read_csv(path).shape[0]
    date_of_file = path.split("/")[-1].replace(".csv","")
    parsed_date_of_file = datetime.datetime.strptime(date_of_file, "%Y-%m-%d_%H-%M-%S")

    if d_type == "Historical" :
        DB_rows = conn.execute(f"""select count(*) from CMC_Historical
                                    WHERE Date_of_file = '{parsed_date_of_file}'""").fetchone()[0]
    elif d_type == "Real_time" :
        DB_rows = conn.execute(f"""select count(*) from CMC_Real_time
                                    WHERE Date_of_file = '{parsed_date_of_file}' """).fetchone()[0]
    else :
        logging.exception(f"Invalid data type {d_type}")
        conn.close()
        return False

    if DB_rows != df_rows_count:

        logging.warning(f"File Rows : {df_rows_count} !=  DB Rows : {DB_rows}")
        conn.close()
        return False


    conn.close()
    return True
