---
planFor: macropca
sourceCorpus: ../.ingest/google-drive-1VsNW703KlumEhnJRgIjiPTVvePjVnNSy
targetLanguage: sl
targetLevel: expert
status: planned
---

# Nacrt knjige: MacroPCA

## Predlagani naslov

**MacroPCA: robustna analiza glavnih komponent z manjkajocimi vrednostmi ter celicnimi in vrsticnimi osamelci**

## Predlagani podnaslov

**Ekspertni vodic po metodi Hubert, Rousseeuw in Van den Bossche (2019)**

## Cilj in obseg

Knjiga naj bo vodeno strokovno branje in metodoloska razlaga clanka o MacroPCA. Namen ni prepis ali predelava clanka, temvec avtorska ucna razlaga:

- zakaj klasicna PCA odpove pri realnih tabelarnih podatkih,
- zakaj vrsticno robustne metode niso dovolj, ce so prisotni celicni osamelci,
- kako MacroPCA sestavi DDC, ICPCA in ROBPCA v enoten postopek,
- kako interpretirati residual maps in outlier maps,
- kako uporabiti metodo kot diagnostični mehanizem pri zaporednem nadzoru podatkov.

Ciljna publika je ekspertna: bralec naj pozna osnovno PCA, linearno algebro, robustno statistiko vsaj na konceptualni ravni in probleme manjkajocih vrednosti. Knjiga zato ne sme porabiti veliko prostora za osnovno razlago PCA, mora pa biti natancna pri razlikovanju kontaminacijskih modelov in vlog posameznih robustnih komponent.

## Publikacijski model

- Predlagani imenik knjige: `macropca`
- Uporabnikov ciljni naziv: `MacroPCA`
- Razlog za imenik `macropca`: stabilen, nizko-crkovni URL in skladnost z obstojecimi imeniki v repozitoriju.
- Knjiga naj ima `index.md` in numericno urejene poglavne imenike.
- Priporocena uporaba eksplicitnega seznama `chapters` v `index.md`, ker bo zaporedje pedagosko, ne nujno odvisno samo od imenikov.
- Ko bo knjiga pripravljena za objavo, jo je treba dodati v `books` seznam v korenskem `collection.md`.

Predvideni URL po objavi v tem repozitoriju:

```text
/trainings/macropca
```

## Predlagana struktura

```text
macropca/
  index.md
  book-plan.md
  assets/
    contamination-matrix.svg
    macropca-flow.svg
    residual-map-guide.svg
    outlier-map-guide.svg
  01-problem-setting/
    index.md
  02-cellwise-contamination/
    index.md
  03-missing-values-and-pca/
    index.md
  04-building-blocks/
    index.md
  05-macropca-algorithm/
    index.md
  06-diagnostics/
    index.md
  07-online-analysis/
    index.md
  08-evidence-from-simulations/
    index.md
  09-real-data-examples/
    index.md
  10-reading-notes/
    index.md
```

## Predlagani `index.md`

Front matter:

```yaml
---
title: "MacroPCA"
subTitle: "Robustna PCA za manjkajoce vrednosti ter celicne in vrsticne osamelce"
language: "sl"
tocInHeader: true
chapters:
  - ./01-problem-setting
  - ./02-cellwise-contamination
  - ./03-missing-values-and-pca
  - ./04-building-blocks
  - ./05-macropca-algorithm
  - ./06-diagnostics
  - ./07-online-analysis
  - ./08-evidence-from-simulations
  - ./09-real-data-examples
  - ./10-reading-notes
---
```

Uvod naj jasno pove, da je knjiga spremljevalno ucno gradivo k clanku Hubert, Rousseeuw in Van den Bossche (2019), ne nadomestilo clanka.

## Poglavja

### 1. Problem: PCA na neurejenih realnih matrikah

Namen: postaviti okvir. Pojasniti, da podatkovna matrika ni samo numericni objekt, ampak nosi tri vrste nepopolnosti: manjkajoce vrednosti, osamele celice in osamele vrstice.

Vsebina:

- klasicna PCA kot nizkorazsezni model,
- zakaj navadna PCA ni robustna,
- razlikovanje med vrsticno in celicno kontaminacijo,
- zakaj je problem visokorazsezen.

Vizual: lasten diagram podatkovne matrike z oznacenimi regularnimi celicami, manjkajocimi celicami, celicnimi osamelci in vrsticnimi osamelci.

### 2. Zakaj celicni osamelci zlomijo vrsticno robustnost

Namen: razloziti glavni metodoloski razlog za MacroPCA.

Vsebina:

- propagacija celicnih osamelcev v kontaminirane vrstice,
- omejitev metod, ki zahtevajo manj kot polovico osamelih vrstic,
- zakaj univariatno zaznavanje po stolpcih ni dovolj,
- vloga korelacijske strukture pri zaznavi celicnih anomalij.

Vizual: shema, kjer majhen delez problematicnih celic kontaminira vec kot polovico vrstic.

### 3. Manjkajoce vrednosti in PCA

Namen: lociti problem manjkajocih vrednosti od problema osamelcev.

Vsebina:

- MCAR, MAR in prakticni pomen predpostavke MAR,
- ICPCA kot EM-podoben pristop,
- zakaj imputacija v tem kontekstu ni koncna resnica,
- razlika med matriko z imputiranimi manjkajocimi vrednostmi in matriko z imputiranimi celicnimi osamelci.

Sidenote kandidat: kratka opomba o tem, zakaj MNAR ni obravnavan v izvirnem algoritmu.

### 4. Gradniki: DDC, ICPCA in ROBPCA

Namen: predstaviti sestavne dele pred celotnim algoritmom.

Vsebina:

- DDC kot celicna diagnostika in zacetna imputacija,
- ICPCA kot iterativni mehanizem za manjkajoce vrednosti,
- ROBPCA kot vrsticno robustna ocena podprostora,
- kaj vsak gradnik resi in cesa sam ne resi.

Vizual: primerjalna tabela gradnikov in tipov motenj.

### 5. Algoritem MacroPCA

Namen: sestaviti celoten postopek v pedagosko berljiv algoritemski tok.

Vsebina:

- zacetna DDC faza,
- projekcijsko iskanje robustnega podprostora,
- izbor dimenzije podprostora,
- iterativno ocenjevanje,
- robustna ocena nalaganj,
- skorji, napovedi in residuali,
- zakaj algoritem ne imputira celicnih osamelcev znotraj osamelih vrstic na nacin, ki bi jih prikril.

Vizual: diagram toka algoritma.

### 6. Diagnostika: residual map in outlier map

Namen: narediti metodo uporabno za interpretacijo.

Vsebina:

- residual map kot lokalizacija problematicnih spremenljivk,
- outlier map kot locitev tipov vrstic,
- razlika med ortogonalno razdaljo in score distance,
- dobre leverage tocke, ortogonalni osamelci in slabe leverage tocke,
- kako brati graficne prikaze brez pretirane interpretacije.

Vizual: lastna poenostavljena residual map in outlier map.

Vprašanja: smiselno dodati 2-3 neocenjena interpretacijska vprašanja na koncu poglavja.

### 7. Zaporedna analiza in nadzor procesa

Namen: pokazati uporabnost metode pri novih podatkih.

Vsebina:

- ucenje modela na zacetnem naboru,
- uporaba modela na novi vrstici,
- imputacija, celicna diagnostika in vrsticna oznaka za novo opazovanje,
- zakaj je to relevantno za procesni nadzor,
- tveganje zastaranja modela in potreba po periodični ponovni oceni.

Vizual: shema "fit offline, screen online".

### 8. Kaj povedo simulacije

Namen: povzeti dokazno strukturo, ne reproducirati vseh grafov.

Vsebina:

- scenariji: manjkajoce vrednosti, celicni osamelci, vrsticni osamelci, kombinacije,
- metrika MSE kot primerjalni kriterij,
- zakaj ICPCA odpove pri osamelcih,
- zakaj MROBPCA odpove pri celicni kontaminaciji,
- kdaj MacroPCA ohrani nizko napako.

Vizual: lastna konceptualna tabela rezultatov namesto predelave izvirnih simulacijskih figur.

### 9. Realna primera: steklo in DPOSS

Namen: povezati metodo z realnimi domenami.

Vsebina:

- glass data kot kemometrijski primer,
- DPOSS kot primer z velikim delezem manjkajocih vrednosti,
- kaj residual maps dodajo k navadni PCA interpretaciji,
- zakaj so spremenljivke, ne samo opazovanja, del diagnoze.

Pravno opozorilo: ce se uporabijo izvirne figure, morajo ostati nespremenjene in atribuirane. Boljsa izbira so lastni didakticni diagrami in opis rezultatov.

### 10. Bralne opombe, omejitve in nadaljevanje

Namen: zakljuciti kot ekspertno gradivo.

Vsebina:

- predpostavke in omejitve,
- MAR ni MNAR,
- robustnost ni samodejna garancija pravilne domenske interpretacije,
- racunska zahtevnost v primerjavi s klasicno PCA,
- povezave na originalni clanek, DDC, ROBPCA in robustno statistiko,
- mozna nadaljevanja: PCA regresija, PLS, robustne metode za produkcijske tokove.

## Strategija slik

Ne uporabljati izvirnih figur kot osnovo za predelane slike, ker vir navaja licenco CC BY-NC-ND. Prednostna strategija:

- izdelati lastne shematske SVG diagrame,
- izvirne figure obravnavati kot referencni dokaz in jih citirati,
- ce se izvirna figura uporabi, jo uporabiti nespremenjeno, z atribucijo in jasnim virom,
- v knjigi lociti "konceptualni diagram" od "rezultatov iz clanka".

Prioritetne lastne slike:

- `assets/contamination-matrix.svg`
- `assets/macropca-flow.svg`
- `assets/residual-map-guide.svg`
- `assets/outlier-map-guide.svg`

## Strategija vprašanj

Gostota: nizka do srednja.

Vprašanja naj bodo v poglavjih, ne v uvodu knjige. Najprimernejsa mesta:

- poglavje 2: prepoznavanje posledic celicne kontaminacije,
- poglavje 3: MCAR/MAR in pomen imputacije,
- poglavje 6: interpretacija residual map in outlier map,
- poglavje 8: izbira metode glede na tip motnje.

Vprašanja naj bodo vecinoma `ungraded`, ker gre za ekspertno spremljevalno gradivo, kjer je cilj preverjanje razumevanja, ne formalno ocenjevanje.

## Kandidati za stranske opombe

- Razlika med "cellwise" in "casewise/rowwise" terminologijo.
- Zakaj robustna metoda z visoko breakdown point se vedno ni nujno odporna na celicno kontaminacijo.
- Zakaj imputiranih vrednosti ne smemo nekriticno interpretirati kot opazovanih podatkov.
- Kaj pomeni "good leverage point" v PCA diagnostiki.
- Zakaj online screening ne pomeni, da se model nikoli ne posodobi.

## Terminoloske odlocitve

Predlagana slovenska terminologija:

- principal component analysis: analiza glavnih komponent oziroma PCA,
- score: skor,
- loading: nalaganje,
- residual: residual,
- rowwise outlier: vrsticni osamelec,
- cellwise outlier: celicni osamelec,
- missing value: manjkajoca vrednost,
- imputation: imputacija,
- outlier map: karta osamelcev,
- residual map: residualna karta.

Opomba: v strokovni statistični rabi je "osamelec" sprejemljivejsi od "izstopajoca vrednost", kadar govorimo o celih vrsticah oziroma objektih. Za celice je "celicni osamelec" jasen in neposreden prevod.

## Odprte odlocitve pred pisanjem

- Ali naj knjiga vsebuje R-kodno poglavje z uporabo paketa `cellWise`, ali naj ostane metodolosko bralno gradivo?
- Ali naj se vključi lastni simulacijski primer, da se lahko ustvarijo avtorski grafi brez licencnih tveganj?
- Ali naj bo knjiga popolnoma slovenska, ali naj ohrani angleške izraze v oklepajih pri prvi pojavitvi?
- Ali naj se poglavje 9 omeji na interpretacijo primerov iz clanka ali naj doda nov prakticen primer iz lokalno dostopnih podatkov?

## Naslednji korak

Pred `draft-book macropca` je treba sprejeti vsaj ti dve odlocitvi:

- uporabiti samo metodolosko razlago ali dodati R izvedbeni primer,
- ustvariti lastne diagrame ali uporabiti izvirne figure nespremenjene z atribucijo.
