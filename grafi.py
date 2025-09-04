import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import linregress

sns.set(style="whitegrid")

def temperaturni_graf(df: pd.DataFrame, izbrana_mesta=None):
    df = df.copy()
    df["datum"] = pd.to_datetime(df["datum"])
    
    if izbrana_mesta:
        df = df[df["mesto"].isin(izbrana_mesta)]
    
    plt.figure(figsize=(14, 6))
    sns.lineplot(data=df, x="datum", y="Povprečna temperatura (v °C)", hue="mesto")
    plt.title("Povprečne dnevne temperature skozi čas")
    plt.xlabel("Datum")
    plt.ylabel("Temperatura (°C)")
    plt.tight_layout()
    plt.show()


def sezonska_analiza(df: pd.DataFrame):
    df = df.copy()
    df["datum"] = pd.to_datetime(df["datum"])
    df["mesec"] = df["datum"].dt.month
    df["Letni čas"] = df["mesec"].map({
        12: "Zima", 1: "Zima", 2: "Zima",
        3: "Pomlad", 4: "Pomlad", 5: "Pomlad",
        6: "Poletje", 7: "Poletje", 8: "Poletje",
        9: "Jesen", 10: "Jesen", 11: "Jesen"
    })
    return df.groupby(["mesto", "Letni čas"])["Povprečna temperatura (v °C)"].mean().unstack().round(2)


def statistika_mest(df: pd.DataFrame):
    return df.groupby("mesto")["Povprečna temperatura (v °C)"].agg(["min", "max", "mean", "std"]).round(2)


def prikazi_stolpicni_diagram_letni_casi(sezonski_povprecji, mesta):
    podatki = sezonski_povprecji.loc[mesta]

    letni_casi = ['Jesen', 'Poletje', 'Pomlad', 'Zima']

    ax = podatki[letni_casi].plot(kind='bar')
    ax.set_title('Povprečne temperature po letnih časih')
    ax.set_ylabel('Temperatura (°C)')
    ax.set_xlabel('Mesto')
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.show()

