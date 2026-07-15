# 8. Kaj povedo simulacije

Simulacije v izvirnem članku imajo jasno dokazno vlogo: ne dokazujejo, da je MacroPCA najboljša v vseh možnih situacijah, temveč pokažejo, zakaj je potrebna metoda, ki hkrati obravnava manjkajoče vrednosti, celične osamelce in vrstične osamelce.

Primerjane metode imajo različne šibke točke:

- ICPCA zna delati z manjkajočimi vrednostmi, vendar ni robustna na osamelce,
- MROBPCA doda vrstično robustnost, vendar ostane ranljiva za razpršeno celično kontaminacijo,
- MacroPCA doda celično diagnostiko pred robustnim ocenjevanjem podprostora.

## Scenariji

Ključni simulacijski scenariji so:

- samo manjkajoče vrednosti,
- manjkajoče vrednosti in celični osamelci,
- manjkajoče vrednosti in vrstični osamelci,
- kombinacija manjkajočih vrednosti, celičnih osamelcev in vrstičnih osamelcev.

Ko so prisotne samo manjkajoče vrednosti, je ICPCA lahko konkurenčna. Ko se pojavijo osamelci, zlasti celični, se razlika spremeni. Celična kontaminacija je za metode brez celične zaščite posebej nevarna, ker lahko poškoduje veliko vrstic, ne da bi bila vsaka vrstica v celoti napačna.

## MSE kot dokazni instrument

Simulacije pogosto merijo napako rekonstrukcije oziroma ocene podprostora z MSE. To je uporabno, ker omogoča primerjavo čez različne stopnje kontaminacije. Ni pa to edina relevantna metrika. Za uporabo je pomembna tudi diagnostična uporabnost: ali metoda pove, katere celice in vrstice so problematične.

<Question
  id="macropca-method-choice"
  question="V katerem scenariju je razlika med MROBPCA in MacroPCA metodološko najpomembnejša?"
  options={["Ko ni osamelcev in ni manjkajočih vrednosti", "Ko so prisotne samo manjkajoče vrednosti MCAR", "* Ko so celični osamelci razpršeni po številnih vrsticah", "Ko je cilj samo izračun navadne kovariančne matrike"]}
  attempts={2}
>
MROBPCA je namenjena vrstično robustni PCA z manjkajočimi vrednostmi. MacroPCA je potrebna predvsem tam, kjer celični osamelci ogrozijo vrstično robustnost.
</Question>

## Kako brati rezultate

Najpomembnejši sklep ni, da mora MacroPCA vedno nadomestiti vse druge metode. Sklep je pogojen:

- če so podatki čisti, robustna kompleksnost ni nujno potrebna,
- če manjkajo samo vrednosti, je lahko iterativna PCA zadostna,
- če so osamelci vrstični, lahko pomaga ROBPCA,
- če so hkrati prisotni manjkajoče vrednosti ter celični in vrstični osamelci, je MacroPCA zasnovana prav za to kombinacijo.

To je tudi praktična lekcija za modeliranje: izbira metode mora slediti kontaminacijskemu modelu, ne navadi ali privzetemu paketu.
