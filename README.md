# Projektna naloga - Analiza vremena
 
 *Avtor: Pija Vavtar*

 ## Uvod

V sledeči projektni nalogi sem predstavila analizo temperatur v treh mestih (Ljubljana, Berlin in Pariz), ki sem jih pridobila s spletne strani [OpenMeteo](https://open-meteo.com/en/docs). Zanimale so me povprečne temparature, temparature po letnih časih in ostali statistični podatki o vremenu.

## Navodila

Naložite naslednje knjižnice:
1. `pandas`,
2. `matplotlib`,
3. `seaborn`.

Odprite datoteko z razširitvijo `.ipynb` (Jupyter Notebook). Najdeto jo v isti mapi kakor README.md datoteko. Windows uporabniki lahko datoteko zaženete z ukazom 'py -m notebook' v mapi, kjer se nahaja `.ipynb` datoteka. Nato zaženite vsak korak v `.ipynb` datoteki posamezno.

## Opis datotek

* Program `analiza.py` iz zgoraj navedene spletne strani pridobi podatke, natančneje; datum, mesto, temperatura. Te podatke shrani v '.csv' datoteke.
* Program `grafi.py` zapiše funkcije za grafe in tabele.
* V datoteki `analiza.ipynb` so predstavljeni rezultati analize. 