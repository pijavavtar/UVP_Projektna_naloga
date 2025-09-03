import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import linregress

# Nastavi stil grafov
sns.set(style="whitegrid")

def narisi_temperaturni_graf(df: pd.DataFrame, izbrana_mesta=None):
    df = df.copy()
    df["datum"] = pd.to_datetime(df["datum"])
    
    if izbrana_mesta:
        # Filtriraj po seznamu mest
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
    # Povprečja temperature po mestu in letnem času
    return df.groupby(["mesto", "Letni čas"])["Povprečna temperatura (v °C)"].mean().unstack().round(2)


def statistika_mest(df: pd.DataFrame):
    return df.groupby("mesto")["Povprečna temperatura (v °C)"].agg(["min", "max", "mean", "std"]).round(2)


def izracunaj_trend(df: pd.DataFrame, mesto: str):
    poddf = df[df["mesto"] == mesto].copy()
    if poddf.empty:
        print(f"Mesto {mesto} ni bilo najdeno v podatkih.")
        return None

    poddf["datum"] = pd.to_datetime(poddf["datum"])
    poddf["datum_stevilka"] = poddf["datum"].map(pd.Timestamp.toordinal)

    slope, intercept, r_value, p_value, std_err = linregress(
        poddf["datum_stevilka"], poddf["Povprečna temperatura (v °C)"]
    )

    return {
        "mesto": mesto,
        "naklon_C_na_dan": slope,
        "naklon_C_na_leto": slope * 365,
        "R2": r_value ** 2,
        "p-vrednost": p_value
    }


def narisi_trend(df: pd.DataFrame, mesto: str):
    poddf = df[df["mesto"] == mesto].copy()
    if poddf.empty:
        print(f"Mesto {mesto} ni bilo najdeno v podatkih.")
        return

    poddf["datum"] = pd.to_datetime(poddf["datum"])
    poddf["datum_stevilka"] = poddf["datum"].map(pd.Timestamp.toordinal)

    slope, intercept, *_ = linregress(
        poddf["datum_stevilka"], poddf["Povprečna temperatura (v °C)"]
    )

    poddf["trend"] = intercept + slope * poddf["datum_stevilka"]

    plt.figure(figsize=(10, 5))
    plt.plot(poddf["datum"], poddf["Povprečna temperatura (v °C)"], label="Temperatura", alpha=0.6)
    plt.plot(poddf["datum"], poddf["trend"], label="Trend (regresija)", color="red", linewidth=2)
    plt.title(f"Temperaturni trend za mesto {mesto}")
    plt.xlabel("Datum")
    plt.ylabel("Temperatura (°C)")
    plt.legend()
    plt.tight_layout()
    plt.show()

def prikazi_stolpicni_diagram_letni_casi(sezonski_povprecji, mesta):
    podatki = sezonski_povprecji.loc[mesta]

    # Stolpci letnih časov
    letni_casi = ['Jesen', 'Poletje', 'Pomlad', 'Zima']

    # Stolpični diagram
    ax = podatki[letni_casi].plot(kind='bar')
    ax.set_title('Povprečne temperature po letnih časih')
    ax.set_ylabel('Temperatura (°C)')
    ax.set_xlabel('Mesto')
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.show()


def ustvari_pivot_tabelo(ime_datoteke):
    df = pd.read_csv(ime_datoteke)

    pivot_df = df.pivot(index='datum', columns='mesto', values='Povprečna temperatura (v °C)')

    pivot_df.reset_index(inplace=True)
    pivot_df.rename(columns={'datum': 'Datum/mesto'}, inplace=True)

    return pivot_df
