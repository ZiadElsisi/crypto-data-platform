import os
import pandas as pd
import json

def cmc_api_transform(Path,d_type):
    # Check if path exists
    if not os.path.exists(path=Path):
        raise FileNotFoundError("Path does not exist")

    #Chech Real_time Or historical

    if not (d_type == "Historical" or d_type == "Real_time"):
        raise ValueError("Restricted CMC Type ")


    with open(Path) as json_file:
        json_data = json.load(json_file)

        # Lets Extract Fieleds
        Filtered_Data = []
        for data in json_data["data"]:
            dic = {
                "id": data["id"],
                "name": data["name"],
                "symbol": data["symbol"],
                "cmc_rank" : data["cmc_rank"],
                "last_updated" : data["last_updated"],
                "circulating_supply" : data["circulating_supply"],
                "max_supply" : data.get("max_supply"),
            }
            if d_type == "Real_time":
                 dic["price" ]= data["quote"][0]["price"]
                 dic["market_cap" ]= data["quote"][0]["market_cap"]
                 dic["volume_24h" ]= data["quote"][0]["volume_24h"]
                 dic["volume_change_24h" ]= data["quote"][0]["volume_change_24h"]
                 dic["percent_change_1h" ]= data["quote"][0]["percent_change_1h"]
                 dic["percent_change_24h" ]= data["quote"][0]["percent_change_24h"]
                 dic["percent_change_7d" ]= data["quote"][0]["percent_change_7d"]
                 dic["market_cap_dominance"] = data["quote"][0]["market_cap_dominance"]
                 dic["percent_change_90d"] = data["quote"][0]["percent_change_90d"]

            elif d_type == "Historical":
                dic["price"] = data["quote"]["USD"]["price"]
                dic["market_cap"] = data["quote"]["USD"]["market_cap"]
                dic["volume_24h"] = data["quote"]["USD"]["volume_24h"]
                dic["percent_change_1h"] = data["quote"]["USD"]["percent_change_1h"]
                dic["percent_change_24h"] = data["quote"]["USD"]["percent_change_24h"]
                dic["percent_change_7d"] = data["quote"]["USD"]["percent_change_7d"]


            Filtered_Data.append(dic)

    df = pd.DataFrame(Filtered_Data)

    File_date= Path.split("/")[-1].replace(".json", "")
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    Processed_DIR = os.path.join(BASE_DIR, "..", "..", "data", "processed","CMC",d_type)
    os.makedirs(os.path.join(Processed_DIR), exist_ok=True)
    FullPath = os.path.join(Processed_DIR, f"{File_date}.csv")
    df.to_csv(f"{FullPath}", index=False )


    return FullPath


