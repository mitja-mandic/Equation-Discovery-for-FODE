# 3. Manjkajoče vrednosti in PCA

Manjkajoče vrednosti niso isto kot osamelci. Pri osamelcu je vrednost opazovana, vendar sumljiva. Pri manjkajoči vrednosti podatka ni. Ta razlika je pomembna, ker PCA potrebuje popolno matriko ali postopek, ki zna delati z nepopolnimi vrsticami.

Klasičen pristop je iterativna PCA z imputacijo. Najprej manjkajoče vrednosti nadomestimo z začetnimi ocenami, na primer s stolpčnimi povprečji. Nato izračunamo PCA, rekonstruiramo podatke iz izbranega podprostora, posodobimo manjkajoče vrednosti in ponavljamo do konvergence. Ta logika je sorodna EM pristopu: neznane vrednosti nadomeščamo s trenutnimi modelnimi napovedmi.

Težava je, da navadna iterativna PCA ni robustna. Če so poleg manjkajočih vrednosti prisotni osamelci, modelne napovedi že od začetka temeljijo na poškodovanem podprostoru.

## MCAR, MAR in meja modela

MacroPCA predpostavlja manjkajoče vrednosti tipa MAR: verjetnost, da celica manjka, ni odvisna od njene neopažene vrednosti, lahko pa je povezana z drugimi opazovanimi vrednostmi v isti vrstici. To je standardna predpostavka za veliko EM-podobnih postopkov.

MCAR je strožji poseben primer, kjer manjkajočnost ni povezana niti z manjkajočo vrednostjo niti z drugimi vrednostmi. MNAR je drugačen in težji primer: manjkanje je povezano prav z neopaženo vrednostjo. MacroPCA ni zasnovana kot splošna rešitev za MNAR.

<Sidenote>
Če je meritev manjkajoča prav zato, ker je ekstremna, je to lahko MNAR mehanizem. Takrat sama imputacija iz PCA podprostora ne reši identifikacijskega problema; potrebujemo domensko razlago manjkajočnosti.
</Sidenote>

## Imputacija kot računsko sredstvo

V tej knjigi je ključno razlikovati med tremi stvarmi:

- opazovano vrednostjo,
- imputirano vrednostjo za manjkajočo celico,
- modelno nadomestitvijo za sumljivo celico.

Imputirana vrednost ni dokaz, da je bila resnična vrednost takšna. Je vrednost, ki omogoči stabilno ocenjevanje podprostora in primerljivo diagnostiko. Pri MacroPCA ima ta razlika še večjo težo, ker metoda hkrati nadomešča manjkajoče vrednosti in obravnava sumljive celice.

<Question
  id="macropca-imputation-role"
  question="Katera interpretacija imputacije v MacroPCA je najprimernejša?"
  options={["Imputirana vrednost je končna rekonstruirana resnica o manjkajoči meritvi", "* Imputirana vrednost je računska in diagnostična ocena, ki stabilizira ocenjevanje podprostora", "Imputacija je potrebna samo za lepši prikaz grafov", "Imputacija pomeni, da osamelcev ni več treba označevati"]}
  attempts={2}
>
MacroPCA uporablja imputacijo za ocenjevanje in diagnostiko. Imputirane vrednosti je treba ločiti od opazovanih meritev in od domenske resnice.
</Question>
