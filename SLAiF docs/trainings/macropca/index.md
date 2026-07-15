---
title: "MacroPCA"
subTitle: "Robustna PCA za manjkajoče vrednosti ter celične in vrstične osamelce"
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

Ta knjiga je ekspertni učni vodnik po metodi **MacroPCA**, ki so jo predstavili Mia Hubert, Peter J. Rousseeuw in Wannes Van den Bossche v članku *MacroPCA: An All-in-One PCA Method Allowing for Missing Values as Well as Cellwise and Rowwise Outliers*.

Namen knjige ni nadomestiti članka ali reproducirati njegovega besedila. Namen je razložiti, zakaj je problem težak, kako se posamezni robustni gradniki sestavijo v enoten postopek in kako brati diagnostične rezultate. Članek ostaja primarni vir za formalne dokaze, natančne enačbe in empirične rezultate.

## Kaj obravnavamo

- zakaj klasična analiza glavnih komponent odpove pri osamelcih,
- zakaj vrstično robustna PCA ni dovolj, kadar so anomalije razpršene po celicah,
- kako manjkajoče vrednosti spremenijo nalogo ocenjevanja podprostora,
- kako MacroPCA poveže DDC, ICPCA in ROBPCA,
- kako interpretirati residualne karte in karte osamelcev,
- zakaj je metoda uporabna pri zaporednem nadzoru novih opazovanj.

## Predznanje

Knjiga predpostavlja, da bralec pozna osnovno PCA, pojem nizkorazsežnega podprostora, razliko med skorji in nalaganji ter osnovno intuicijo robustne statistike. Osnov ne ponavljamo sistematično; razlagamo jih samo tam, kjer so potrebne za razumevanje MacroPCA.

## Vir

Primarni vir je:

Hubert, M., Rousseeuw, P. J., and Van den Bossche, W. (2019). *MacroPCA: An All-in-One PCA Method Allowing for Missing Values as Well as Cellwise and Rowwise Outliers*. Technometrics. DOI: `10.1080/00401706.2018.1562989`.

Izvirni članek je licenciran z licenco, ki vključuje omejitev NoDerivatives. Zato ta knjiga uporablja lastno razlago in lastne shematske slike, izvirni članek pa obravnava kot citiran strokovni vir.
