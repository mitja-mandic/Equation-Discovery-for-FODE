# 5. Algoritem MacroPCA

Algoritem MacroPCA lahko beremo kot zaporedje zaščitnih korakov okoli nizkorazsežnega PCA modela. Cilj ni zgolj oceniti komponente, temveč jih oceniti tako, da manjkajoče vrednosti, celični osamelci in vrstični osamelci ne povzročijo medsebojnega maskiranja.

## 1. Začetna celična diagnostika

Postopek se začne z zaznavanjem odstopajočih celic in začetno imputacijo. Ta korak je nujen, ker lahko razpršeni celični osamelci poškodujejo vsako naslednjo oceno. Če bi takoj zagnali vrstično robustno PCA, bi lahko veliko delno kontaminiranih vrstic izgledalo kot večinska struktura.

## 2. Robustno iskanje podprostora

Po začetni stabilizaciji algoritem išče nizkorazsežen podprostor, ki predstavlja večinsko strukturo. Pri tem mora biti robusten na vrstice, ki ostanejo osamele tudi po obravnavi celičnih anomalij.

Ta faza je konceptualno občutljiva: osamela vrstica ne sme biti popravljena tako, da bi postala nevidna. Če celotna vrstica prihaja iz drugega režima, je to informacija, ne samo šum.

## 3. Izbor števila komponent

Število komponent ni samo tehnični parameter. Premajhno število komponent poveča residuale in lahko ustvari lažne osamelce. Preveliko število komponent lahko v podprostor vključi kontaminacijo. MacroPCA zato izbiro dimenzije obravnava kot del robustnega postopka.

## 4. Iterativno ocenjevanje in imputacija

Ko je začetni podprostor določen, algoritem iterativno izboljšuje imputacije in oceno podprostora. Tu se srečata logika ICPCA in robustne PCA. Manjkajoče vrednosti se nadomeščajo z napovedmi iz trenutnega modela, vendar ocena modela ostaja zaščitena pred osamelci.

## 5. Robustna ocena nalaganj

Dodaten korak robustne ocene nalaganj je pomemben zaradi dobrih leverage točk. Takšne točke lahko ležijo v pravem podprostoru, vendar vplivajo na orientacijo komponent znotraj njega. Če je cilj interpretacija komponent, ne samo rekonstrukcija podprostora, so nalaganja bistvena.

<Sidenote>
Podprostor in njegove baze niso isto. Dve različni bazi lahko napenjata isti podprostor, vendar vodita do drugačnih skorjev in drugačne interpretacije komponent.
</Sidenote>

## 6. Skorji, napovedi in residuali

Končni rezultat ni samo matrika nalaganj. MacroPCA vrne skorje, napovedane vrednosti, residuale, oznake celičnih osamelcev in oznake vrstičnih osamelcev. Diagnostični del je zato enakovreden ocenjevalnemu delu.

Najpomembnejša izvedbena ideja je, da algoritem ne sme zamenjati celične imputacije za brisanje vrstične anomalije. Celične popravke uporablja zato, da stabilizira oceno večinskega podprostora; vrstične anomalije pa ostanejo predmet diagnostike.
