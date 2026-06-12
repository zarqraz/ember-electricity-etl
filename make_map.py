import pandas as pd 
import sqlite3      
import os              
import urllib.request  
import geopandas as gpd  
import matplotlib.pyplot as plt

connection = sqlite3.connect("electricity.db")
share = pd.read_sql_query("SELECT * FROM clean_share", connection)
generation = pd.read_sql_query("SELECT * FROM clean_generation", connection)
connection.close()

share["year"] = pd.to_datetime(share["date"]).dt.year
generation["year"] = pd.to_datetime(generation["date"]).dt.year

avg_2015 = share[share["year"] == 2015].groupby(["country", "iso3"])["clean_share"].mean()
avg_2025 = share[share["year"] == 2025].groupby(["country", "iso3"])["clean_share"].mean()
growth = (avg_2025 - avg_2015).reset_index(name="growth")

in_window = generation[(generation["year"] >= 2015) & (generation["year"] <= 2025)]
totals = in_window.groupby(["country", "iso3"])["clean_twh"].sum().reset_index(name="total_twh")

GEO_URL = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_admin_0_countries.geojson"
GEO_PATH = "ne_110m_admin_0_countries.geojson"

if not os.path.exists(GEO_PATH):
    print("\nDownloading country shapes (one-time)...")
    urllib.request.urlretrieve(GEO_URL, GEO_PATH)

world = gpd.read_file(GEO_PATH)
europe = world[world["CONTINENT"] == "Europe"]


europe_growth = europe.merge(growth, left_on="ISO_A3_EH", right_on="iso3", how="left")
europe_totals = europe.merge(totals, left_on="ISO_A3_EH", right_on="iso3", how="left")

def plot_map(geo_data, value_column, title, legend_label, output_path):
    """Draw a Europe choropleth coloured by `value_column` and save it as a PNG."""
    fig, ax = plt.subplots(figsize=(10, 10))

    geo_data.plot(
        ax=ax,
        column=value_column,        
        cmap="YlGn",                 
        edgecolor="white",      
        linewidth=0.4,
        legend=True,            
        legend_kwds={"label": legend_label, "shrink": 0.5},
        missing_kwds={"color": "lightgrey"}, 
    )

    ax.set_xlim(-25, 45)
    ax.set_ylim(33, 72)
    ax.set_title(title, fontsize=15)
    ax.axis("off")                   

    fig.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print("Saved map:", output_path)


plot_map(
    europe_growth,
    value_column="growth",
    title="Growth in clean electricity share, 2015-2025",
    legend_label="Change in clean share (pp)",
    output_path="map_clean_share_growth.png",
)


plot_map(
    europe_totals,
    value_column="total_twh",
    title="Total clean electricity generation, 2015-2025",
    legend_label="Total clean generation (TWh)",
    output_path="map_clean_generation_twh.png",
)