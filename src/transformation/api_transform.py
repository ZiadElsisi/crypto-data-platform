import os
import pandas as pd
import json

def CMC_API_Transform(Path):
    # Check if path exists
    if not os.path.exists(path=Path):
        print("Path does not exist")
        raise FileNotFoundError

    #Chech Real-time Or historical
    if "Real-time"  in Path:
        Raw_Data_Type = "Real-time"
    elif "Historical" in Path:
        Raw_Data_Type = "Historical"
    else:
        raise ValueError("Unknown CMC data type")


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
            if Raw_Data_Type == "Real-time":
                 dic["price" ]= data["quote"][0]["price"]
                 dic["market_cap" ]= data["quote"][0]["market_cap"]
                 dic["volume_24h" ]= data["quote"][0]["volume_24h"]
                 dic["volume_change_24h" ]= data["quote"][0]["volume_change_24h"]
                 dic["percent_change_1h" ]= data["quote"][0]["percent_change_1h"]
                 dic["percent_change_24h" ]= data["quote"][0]["percent_change_24h"]
                 dic["percent_change_7d" ]= data["quote"][0]["percent_change_7d"]
                 dic["market_cap_dominance"] = data["quote"][0]["market_cap_dominance"]
                 dic["percent_change_90d"] = data["quote"][0]["percent_change_90d"]

            elif Raw_Data_Type == "Historical":
                dic["price"] = data["quote"]["USD"]["price"]
                dic["market_cap"] = data["quote"]["USD"]["market_cap"]
                dic["volume_24h"] = data["quote"]["USD"]["volume_24h"]
                dic["percent_change_1h"] = data["quote"]["USD"]["percent_change_1h"]
                dic["percent_change_24h"] = data["quote"]["USD"]["percent_change_24h"]
                dic["percent_change_7d"] = data["quote"]["USD"]["percent_change_7d"]


            Filtered_Data.append(dic)

    df = pd.DataFrame(Filtered_Data)
    print(df.info())
    File_date= Path[-24:-5]
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    Processed_DIR = os.path.join(BASE_DIR, "..", "..", "data", "processed","CMC",Raw_Data_Type)
    df.to_csv(os.path.join(Processed_DIR,f"{File_date}.csv"), index=False)





