import pandas as pd  
import sqlite3

csv_path = "data/monthly_data.csv"

df = pd.read_csv(csv_path)
# print(df.head())


df["Date"] = pd.to_datetime(df["Date"], dayfirst=True)

# print(df.head())

clean = df[(df["Category"] == "Electricity generation") & (df["Variable"] == "Clean") & (df["Unit"] == "%")]
# print(clean.head())
clean = clean[["Area", "ISO 3 code", "Date", "Value"]]
clean = clean.rename(columns={"Area" : "country", "ISO 3 code" : "iso3", "Date" : "date", "Value" : "clean_share",})
clean = clean.sort_values(["country", "date"]).reset_index(drop=True)
# print(clean.head())

clean_twh = df[(df["Category"] == "Electricity generation") & (df["Variable"] == "Clean") & (df["Unit"] == "TWh")]
# print(clean_twh.head())
clean_twh = clean_twh[["Area", "ISO 3 code", "Date", "Value"]]
clean_twh = clean_twh.rename(columns={"Area": "country", "ISO 3 code": "iso3", "Date": "date", "Value": "clean_twh",})
clean_twh = clean_twh.sort_values(["country", "date"]).reset_index(drop=True)
# print(clean_twh.head())


connection = sqlite3.connect("electricity.db")
clean.to_sql("clean_share", connection, if_exists="replace", index=False)
clean_twh.to_sql("clean_generation", connection, if_exists="replace", index=False)
connection.close()