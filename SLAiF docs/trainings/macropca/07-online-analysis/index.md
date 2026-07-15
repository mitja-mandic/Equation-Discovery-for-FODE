# 7. Zaporedna analiza in nadzor procesa

MacroPCA ni uporabna samo za retrospektivno analizo fiksne matrike. Ena izmed pomembnih uporab je zaporedno pregledovanje novih opazovanj. Model ocenimo na začetnem naboru podatkov, nato pa nove vrstice projiciramo v isti robustni okvir.

Tipičen potek je:

1. na zgodovinskih podatkih ocenimo robustni PCA model,
2. za novo vrstico imputiramo manjkajoče vrednosti,
3. zaznamo sumljive celice,
4. izračunamo skorje in residuale,
5. odločimo, ali je vrstica regularna, celično problematična ali vrstično osamela.

Ta logika je posebej uporabna pri nadzoru procesa. Alarm ni samo binaren. Metoda lahko pokaže tudi, katere spremenljivke so prispevale k alarmu.

## Offline model, online pregled

V produkcijskem okolju je pogosto smiselno ločiti dve časovni skali. Robustni model se posodablja občasno, na primer po validaciji novega obdobja podatkov. Nove vrstice pa se ocenjujejo sproti z že ocenjenim modelom.

To omogoči hitro diagnostiko brez ponovnega učenja celotnega modela ob vsaki novi meritvi. Hkrati pa prepreči, da bi kratkotrajna serija anomalij takoj postala del nove normalnosti.

## Tveganje zastaranja

Model se lahko zastara. Če se proces legitimno spremeni, bo MacroPCA začela označevati veliko novih vrstic kot osamele. To je lahko signal napake, lahko pa tudi signal spremembe režima. Zato online uporaba potrebuje politiko ponovne kalibracije.

<Sidenote>
Robusten online pregled ni isto kot adaptivni model. Če model nikoli ne posodobimo, bo zaznal tudi legitimne dolgoročne premike. Če ga posodabljamo prehitro, lahko normalizira anomalije.
</Sidenote>

## Kaj je dobra operativna uporaba

Dobra uporaba MacroPCA v nadzoru procesa ima tri plasti:

- statistično plast, ki izračuna skorje, residuale in oznake,
- domensko plast, ki presodi pomen označenih spremenljivk,
- operativno plast, ki določi, kdaj se model ponovno oceni.

Sama metoda ne določi stroškov lažnega alarma ali spregledane napake. To mora narediti uporabnik. MacroPCA pa da boljši diagnostični signal kot klasična PCA, ker razlikuje med manjkajočnostjo, celično anomalijo in vrstično anomalijo.
