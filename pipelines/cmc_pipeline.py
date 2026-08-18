from src.ingestion import api_ingest
from src.transformation import api_transform
from src.storage import DuckDB
from src.DataQuality import Validation
import os
import logging

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(BASE_DIR,'..', "logs")
os.makedirs(LOG_DIR, exist_ok=True)
logging.basicConfig(level=logging.INFO ,format='%(asctime)s - %(levelname)s - %(message)s',
                    filemode='a',filename=f'{os.path.join(LOG_DIR, "CMC_pipeline.log")}')

def run_pipeline(date_string=None):
    logging.info("=" * 60)
    logging.info("Pipeline run started")
    logging.info("=" * 60)

    if date_string == None:
        d_type = "Real_time"
    else:
        d_type = "Historical"
    try:
        raw_file = api_ingest.cmc_api_ingest(date_string=date_string)
    except ValueError as e:
        logging.exception(f"invalid input {e}")
        return
    except Exception as e:
        logging.exception(f"error happened {e}")
        return

    logging.info(f"raw data ingested at {raw_file}")

    try:
        processed_file = api_transform.cmc_api_transform(raw_file, d_type=d_type)
    except ValueError as e:
        logging.exception(f"invalid input {e}")
        return
    except FileNotFoundError as e:
        logging.exception(f"file {e} not found")
        return
    except Exception as e:
        logging.exception(f"error happened {e}")
        return
    logging.info(f"processed data transformed at {processed_file}")

    try:
        is_valid = Validation.validate_file(processed_file, d_type=d_type)
    except FileNotFoundError as e:
        logging.exception(f"file {e} not found")
        return
    except ValueError as e:
        logging.exception(f"invalid input {e}")
        return
    except Exception as e:
        logging.exception(f"error happened {e}")
        return


    if is_valid:
        logging.info("Data is valid")
        try:
            DuckDB.Update_CMC_DuckDB()
        except ValueError as e:
            logging.exception(f"invalid input {e}")
            return
        except Exception as e:
            logging.exception(f"error happened {e}")
            return

        try:
            DuckDB.verify_load(path=processed_file, d_type=d_type)
        except ValueError as e:
            logging.exception(f"invalid input {e}")
            return
        except FileNotFoundError as e:
            logging.exception(f"file {e} not found")
            return
        except Exception as e:
            logging.exception(f"error happened {e}")
            return

        logging.info("Data is verified")

    else:
        logging.info("Data is invalid")
    logging.info("Pipeline run finished")
if __name__ == "__main__":
        run_pipeline()