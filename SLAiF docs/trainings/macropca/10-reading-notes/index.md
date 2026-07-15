# 10. Bralne opombe, omejitve in nadaljevanje

MacroPCA je specializirana metoda za realističen, vendar še vedno modeliran problem. Njena uporabnost izhaja iz natančne predpostavke: podatki imajo večinsko nizkorazsežno strukturo, vendar so poškodovani z manjkajočimi vrednostmi, celičnimi osamelci in vrstičnimi osamelci.

## Omejitve

Prva omejitev je predpostavka o manjkajočnosti. MAR je uporabna in standardna predpostavka, ni pa univerzalna. Če manjkanje neposredno nosi informacijo o neopaženi vrednosti, potrebujemo dodatno modeliranje.

Druga omejitev je interpretacija osamelcev. Statistični osamelec ni nujno napaka. Lahko je nov režim, redka legitimna populacija ali signal, da je model preozek. Robustna metoda zmanjša vpliv takih točk na oceno večinske strukture, ne razreši pa njihove domenske narave.

Tretja omejitev je izbira števila komponent. Robustnost ne odstrani potrebe po presoji dimenzije. Premajhen podprostor lahko proizvaja umetne residuale, prevelik pa lahko absorbira kontaminacijo.

## Terminološki povzetek

V tej knjigi uporabljamo naslednje prevode:

- `principal component analysis`: analiza glavnih komponent,
- `score`: skor,
- `loading`: nalaganje,
- `cellwise outlier`: celični osamelec,
- `rowwise outlier`: vrstični osamelec,
- `residual map`: residualna karta,
- `outlier map`: karta osamelcev.

Angleški izrazi ostajajo pomembni, ker so vezani na literaturo in programsko opremo. Slovenski izrazi pa pomagajo ohraniti jasno razlikovanje med ravnmi kontaminacije.

## Nadaljnje branje

Za formalne podrobnosti je treba brati izvirni članek:

Hubert, M., Rousseeuw, P. J., and Van den Bossche, W. (2019). *MacroPCA: An All-in-One PCA Method Allowing for Missing Values as Well as Cellwise and Rowwise Outliers*. Technometrics. DOI: `10.1080/00401706.2018.1562989`.

Za širši kontekst so pomembne teme:

- robustna lokacija in kovarianca,
- ROBPCA,
- DetectDeviatingCells,
- manjkajoči podatki in EM-podobni postopki,
- robustna diagnostika v visoki dimenziji.

## Praktičen zaključek

MacroPCA je smiselna izbira, ko podatki niso samo nepopolni ali samo kontaminirani, ampak oboje hkrati. Njena glavna prednost ni samo robustnejši podprostor. Glavna prednost je, da ohrani diagnostično ločljivost med celičnimi težavami, vrstičnimi težavami in manjkajočnostjo.
