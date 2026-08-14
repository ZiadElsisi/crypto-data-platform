import os
import duckdb
import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(BASE_DIR, "..", "..", "DuckDB")
DB_Path = os.path.join(DB_DIR,"CMC.duckdb")

os.makedirs(DB_DIR, exist_ok=True)

Table_Schemes = {
    "Real-time":{
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
        print("Data Base Already exist")
    else:
        conn = duckdb.connect(f"{DB_DIR}/CMC.duckdb")
        conn.execute(f"""CREATE TABLE CMC_Real_time ({Table_Schemes["Real-time"]['Scheme']} );
                        CREATE TABLE CMC_Historical ({Table_Schemes["Historical"]['Scheme']});
                        """)
        conn.close()


def Update_CMC_DuckDB (action="ignore"):

    if not os.path.exists(os.path.join(DB_Path)) :
        print("Data Base Doesn't Exist")
    else:
        conn = duckdb.connect(DB_Path)
        for DataCategory in ["Real-time","Historical"]:
            Processed_DIR = os.path.join(BASE_DIR,"..","..","data","processed","CMC",DataCategory)
            if not os.path.exists(Processed_DIR):
                print(f"Processed directory doesn't exist: {Processed_DIR}")
                continue
            files = os.listdir(Processed_DIR)
            for file in files:
                if file.endswith(".csv"):
                    file_name=file.replace(".csv","")
                    file_name_tstmp = datetime.datetime.strptime(file_name, "%Y-%m-%d_%H-%M-%S")
                    DataCategoryforInsert = DataCategory.replace("-","_")
                    if action == "ignore":
                        conn.execute(f"""INSERT OR IGNORE INTO CMC_{DataCategoryforInsert}  
                                        Select *,'{file_name_tstmp}' from '{Processed_DIR}/{file}' """)
                    elif action == "update":
                        conn.execute(f"""INSERT OR UPDATE INTO CMC_{DataCategoryforInsert}  
                                        Select *,'{file_name_tstmp}' from '{Processed_DIR}/{file}' """)
                    else :
                        print(f"Action Not Supported")
                else: continue

            final =conn.execute(f"""select * from CMC_{DataCategoryforInsert}""").df()
            print(final)
            print("Successfully updated")
            print("-"*220)

        conn.close()

