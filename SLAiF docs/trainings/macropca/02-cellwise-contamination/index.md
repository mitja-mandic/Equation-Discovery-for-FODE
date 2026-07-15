# 2. Zakaj celični osamelci zlomijo vrstično robustnost

Robustne multivariatne metode so tradicionalno osredotočene na vrstične osamelce. To je naravno: vrstica predstavlja objekt, zato je osamelec pogosto razumljen kot objekt, ki je predaleč od večine. Mnoge robustne metode zato izhajajo iz predpostavke, da je manj kot polovica vrstic kontaminiranih.

Pri celični kontaminaciji se zgodi nekaj drugega. Majhen delež napačnih celic se lahko razprši čez veliko število vrstic. Če ima matrika veliko stolpcev, zadostuje majhna verjetnost napake na celico, da ima več kot polovica vrstic vsaj eno sumljivo vrednost. Metoda, ki vidi samo vrstice, lahko zato dobi vtis, da je večina podatkov kontaminirana.

To je propagacija celičnih osamelcev v vrstično kontaminacijo. Ni nujno, da je večina objektov v celoti napačnih. Dovolj je, da ima veliko objektov po eno ali nekaj napačnih meritev.

## Zakaj univariatni pregledi niso dovolj

Naivna rešitev bi bila preveriti vsak stolpec posebej in označiti vrednosti, ki so daleč od stolpčnega centra. To odpove, kadar je anomalija multivariatna. Celica je lahko videti normalna v svojem stolpcu, vendar je nezdružljiva z drugimi celicami v isti vrstici.

Primer: pri podatkih o avtomobilih masa, moč in poraba goriva niso neodvisne. Vrednost porabe je lahko marginalno običajna, vendar nenavadna glede na kombinacijo mase in moči. Takšna celica ni nujno univariatni osamelec, je pa multivariatno sumljiva.

<Question
  id="macropca-cellwise-propagation"
  question="Zakaj lahko majhen delež celičnih osamelcev povzroči odpoved vrstično robustne PCA?"
  options={["Ker PCA ne deluje, če ima matrika več stolpcev kot vrstic", "Ker celični osamelci vedno pomenijo, da so celotni objekti iz druge populacije", "* Ker se posamezne sumljive celice lahko razpršijo čez veliko vrstic in navidezno kontaminirajo večino vrstic", "Ker robustne metode ne smejo uporabljati imputacije"]}
  attempts={2}
>
Vrstično robustna metoda običajno potrebuje dovolj veliko večino regularnih vrstic. Če je po veliko vrsticah razpršena vsaj ena sumljiva celica, metoda na ravni vrstic izgubi jasno večinsko referenco.
</Question>

## Kaj mora narediti dobra metoda

Metoda mora zaznati celične anomalije, vendar ne sme prehitro sklepati, da je celotna vrstica osamela. Hkrati pa ne sme popraviti vsake sumljive celice tako agresivno, da bi zakrila resnično vrstično anomalijo.

To je osrednja napetost MacroPCA:

- celične osamelce je treba izolirati, da ne zasukajo podprostora,
- vrstične osamelce je treba ohraniti kot diagnostično informacijo,
- manjkajoče vrednosti je treba imputirati, da je izračun sploh mogoč,
- imputacija ne sme postati mehanizem maskiranja.

Zato MacroPCA uporablja ločene predstavitve podatkov: eno za manjkajoče vrednosti in drugo za celice, ki so bile označene kot problematične. Ta ločitev prepreči, da bi algoritem zamenjal računsko stabilizacijo za statistično resnico.
