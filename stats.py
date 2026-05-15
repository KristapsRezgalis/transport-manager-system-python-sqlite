import matplotlib.pyplot as plt
import pandas as pd


def generate_diagram(df, stat_type, period):

    # Copy dataframe
    df = df.copy()

    # Convert loading column to datetime
    df["loading"] = pd.to_datetime(df["loading"])

    # -------------------------
    # GROUPING
    # -------------------------

    if period == "Per day":
        df["period"] = df["loading"].dt.date

    elif period == "Per month":
        df["period"] = df["loading"].dt.to_period("M").astype(str)

    elif period == "Per year":
        df["period"] = df["loading"].dt.year

    # -------------------------
    # CALCULATIONS
    # -------------------------
    # 'Cost per pallet', 'Cost per cargo', 'Total cost', 'Total cargos', 'Total pallets', 'Total weight', 'Pallets per cargo', 'Weight per pallet', 'Weight per cargo', 'Cargos per country', 'Cargos per forwarder', 'Cost per forwarder'
    if stat_type == "Total cost":
        result = df.groupby("period")["cost"].sum()

    elif stat_type == "Total cargos":
        result = df.groupby("period").size()

    elif stat_type == "Cost per cargo":
        result = df.groupby("period")["cost"].mean()

    elif stat_type == "Cost per pallet":
        grouped = df.groupby("period")
        result = grouped["cost"].sum() / grouped["pallets"].sum()
        
    elif stat_type == "Total pallets":
        result = df.groupby("period")["pallets"].sum()
        
    elif stat_type == "Total weight":
        result = df.groupby("period")["weight"].sum()
        
    elif stat_type == "Weight per pallet":
        grouped = df.groupby("period")
        result = grouped["weight"].sum() / grouped["pallets"].sum()
        
    elif stat_type == "Weight per cargo":
        grouped = df.groupby("period")
        result = grouped["weight"].sum() / grouped["pallets"].size()
        
    else:
        print("Unknown stat type")
        return

    # -------------------------
    # CREATE CHART
    # -------------------------

    plt.figure(figsize=(10, 5))

    plt.plot(result.index, result.values)
    # Add labels
    for x, y in zip(result.index, result.values):
        plt.text(x, y, f"{y:.0f}")

    plt.title(f"{stat_type} ({period})")

    plt.xlabel(period)

    plt.ylabel(stat_type)

    plt.grid(True)

    plt.xticks(rotation=45)

    plt.tight_layout()

    plt.show()