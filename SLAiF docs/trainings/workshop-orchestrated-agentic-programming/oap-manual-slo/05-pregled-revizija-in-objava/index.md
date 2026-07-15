# Del V: Pregled, revizija in objava

## V.1 Pregled in revizija

Pregled je točka, kjer OAP bodisi postane inženirstvo bodisi se sesuje v gledališče avtomatizacije. Izhod agenta je treba pregledati, vendar pregled ne pomeni, da mora človek po privzeti poti ročno prebrati vsako generirano vrstico. Zrel OAP najprej pregleduje prek zgoščenih dokazov, šele nato s ciljno usmerjeno inspekcijo.

### Strateški povzetek za pregled

Vsak PR bi moral za človeka ustvariti kratek strateški povzetek pregleda:

```markdown
## Povzetek odločitve
Priporočilo: merge / popravi / zavrni / odloži

Ujemanje s ciljem:
- ...

Dokazi:
- Testni ukaz in rezultat:
- Rezultat CI:
- Ključne spremenjene datoteke:
- Spremenjena dokumentacija:

Tveganja:
- ...

Potrebna človeška odločitev:
- ...
```

Povzetek mora biti dovolj kratek, da ga je mogoče hitro prebrati. Ne sme skrivati dokazov. Nanje mora kazati. Človek lahko nato zahteva razširitev:

- pokaži točen test;
- pokaži spremenjeni invariant;
- pojasni varnostno implikacijo;
- primerjaj PR z izvirnim ciljem;
- povej, kaj ni bilo testirano;
- povej, zaradi česa bi ti ta PR zavrnil.

### Človeški pregled kot managerska disciplina

Človeški pregled bi moral ocenjevati:

- obseg diffa;
- vedenje;
- teste;
- varnost;
- dokumentacijo;
- varnost migracij;
- trditve o izdaji;
- vpliv na operaterje.

Pregledovalec naj ne sprašuje samo: "ali se to prevede?" Spraševati bi moral: "ali to ohranja pomen sistema?" Človek lahko to presodi na podlagi povzetka odločitve, strateškega zasliševanja, ciljnega pregleda datotek in zunanje revizije, kadar to zahteva tveganje. Ni nujno, da vrstični pregled postane rutinsko ozko grlo.

### Pregled s pomočjo UI

UI lahko pomaga pri pregledu, v OAP pa je strateška UI privzeti prvi pregledovalec. Ne bi pa smela biti končni odgovorni pregledovalec. Uporabni prompti za UI-pregled vključujejo:

```text
Preglej ta diff glede:
- varnostnih regresij;
- manjkajočih testov;
- odmika dokumentacije;
- kršitev `AGENTS.md`.

Daj prednost konkretnim ugotovitvam pred pohvalami.
```

UI-pregled je še posebej uporaben za:

- pregledovanje nedoslednosti;
- primerjanje dokumentacije z vedenjem;
- iskanje manjkajočih negativnih testov;
- primerjavo trditev v PR-ju z diffom;
- pripravo vprašanj za človeški pregled;
- stiskanje velikih diffov v kratke povzetke odločitve.

GitHub integracija Codexa je javni primer takšne smeri: vedenje pregleda je mogoče prilagoditi z navodili repozitorija, prompti za pregled pa lahko usmerijo agenta na skrbi, kot so varnostne regresije [[42]](#ref-codex-github).

### Križna revizija med modeli

Uporaben vzorec OAP je, da se gradi z eno družino modelov, revidira pa z drugo. To revizije ne naredi objektivne, zmanjša pa eno vrsto krožnosti. Model, ki ni sodeloval pri implementaciji, lahko opazi drugačne težave, zlasti pri pretiravanju s trditvami, manjkajočih testih, varnostnih mejah, računovodskih invariantih in odmiku dokumentacije.

Križna revizija ne bi smela biti obravnavana kot dekorativni končni pregled. V zrelem projektu OAP je to kadenca: zgradi, revidiraj, odpravi, preveri in ponovno revidiraj, ko se profil tveganja spremeni. Javni arhiv SLAIF API Gatewaya ta vzorec jasno pokaže. Pregledi so bili ohranjeni kot projektni artefakti, ugotovitve so bile sledene v matriki sanacije, kasnejše delo pa je povezalo ugotovitve s PR-ji in dokaznim gradivom preverjanja [[43]](#ref-slaif-reviews-archive); [[44]](#ref-slaif-remediation-matrix).

Križna revizija najbolje deluje, kadar revizor vidi:

- URL ali posnetek repozitorija;
- cilje projekta;
- znane omejitve;
- rezultate testov;
- konkretna vprašanja;
- odsotnost pritiska k pohvalam.

Človek lahko križno revizijo uporabi kot managerski vzvod: ne zato, da bi več bral, ampak da bi zastavil boljša vprašanja in se odločil, kaj pregledati.

<Sidenote>
Namen revizijske kadence ni ceremonija. Namen je v tem, da periodično izzove arhitekturo, trditve in dokaze, še preden se navidezna dokončanost strdi v preveliko samozavest pred izdajo.
</Sidenote>

### Kadenca revizij

Križno revizijo bi bilo praviloma treba sprožiti v teh točkah:

- **Arhitekturna revizija.** Ko obstajajo konstitucija, začetni skelet in prvi izvršljiv ogrodni sistem, vendar preden se nabere veliko funkcionalnosti.
- **Revizija mej.** Ko so uvedeni avtentikacija, skrivnosti, obračunavanje, kvote, streaming, namestitev ali druge visoko tvegane meje.
- **Revizija zrelosti.** Preden se jezik projekta spremeni iz prototipa v beta, release candidate ali production-ready.
- **Nadaljnja revizija.** Ko pristanejo PR-ji sanacije, zlasti kadar je prvotna ugotovitev zadevala varnost, obračunavanje ali trditve o izdaji.

Dodatni krogi revizije so upravičeni, kadar:

- širok refaktor spremeni arhitekturo ali transakcijske meje;
- funkcionalnost uvede nove meje zaupanja ali tok poverilnic;
- testi uspejo, strateški model pa dokaza ne zna jasno razložiti;
- dokumentacija začne trditi več, kot implementacija v resnici podpira;
- se napake CI ponavljajo v vzorcu, ki kaže na krhko zasnovo;
- je odločitev o izdaji odvisna od predpostavke, ki še ni bila izzvana;
- človeka mika sprejeti rezultat predvsem zato, ker agent zveni samozavestno.

Revizija SLAIF API Gateway Review 6.0 / RC1 je dober primer, zakaj je to pomembno. Pregled je projekt za implementirani obseg klasificiral kot verodostojen RC-beta, hkrati pa je ugotovil konkreten preostali rizik trde kvote: predrezervacija vhodnih tokenov in stroškov bi lahko podcenjevala polja Chat Completions, ki niso del message vsebine, kot sta `tools` in sheme `response_format` [[45]](#ref-slaif-review6). Ta ugotovitev je postala omejena sanacija, ne pa nejasna skrb. Matriko sanacije so nato napolnili popravek ocenjevanja ne-sporočilnih vhodov, nadaljnji testi invariant in produkcijski runbooki kot ločene delovne enote z dokaznim gradivom preverjanja [[44]](#ref-slaif-remediation-matrix).

### Mehanika revizijske zanke

Revizijski krog bi moral ustvariti artefakte, ki jih projekt lahko uporabi:

1. Zamrzni trenutni obseg: vejo, commit, release candidate ali URL repozitorija.
2. Opiši implementirani obseg in znane izključitve.
3. Prosi revizorja za ugotovitve, ne za vzpodbudo.
4. Loči napake trenutnega obsega od prihodnjih predlogov funkcionalnosti.
5. Sprejete ugotovitve dodaj v matriko sanacije.
6. Vsako ugotovitev trenutnega obsega pretvori v enega ali več delovnih nalogov velikosti PR-ja.
7. Ugotovitve zapri šele s testi, dokumentacijo, povezavami na kodo ali spremembami release notesa.
8. Ohrani pošten jezik: revizija ni certifikacija, razen če to dejansko je.

Pomembna managerska poteza je korak 4. Zunanji modeli se pogosto pritožujejo nad funkcionalnostmi, ki nikoli niso bile namenjene trenutni izdaji. OAP ne implementira slepo vsakega komentarja revizije. Človek s pomočjo strateške UI ugotovitve razvrsti: dejanska napaka, manjkajoč test, odmik dokumentacije, prihodnje delo ali zavrnjeno priporočilo. Izvajalni agent nato prejme samo omejene delovne naloge.

### Zunanja revizija

Pri resnih sistemih je treba zunanjo revizijo obravnavati kot projektni artefakt. Ugotovitve je treba arhivirati, jih povezati s sanacijskimi nalogami in jih zapreti z dokaznim gradivom. Namen ni zbiranje laskavih ocen. Namen je ustvarjanje revizijske sledi.

### Komentarji pregleda kot delovni nalogi

Komentar pregleda lahko postane naslednja izvajalna naloga. Strateška plast naj ga pretvori v natančen popravljalni prompt:

```text
Obravnavaj samo nerešen komentar pregleda o manjkajočih preverjanjih lastništva.
Ne refaktoriraj nepovezane kode.
Dodaj regresijski test, ki dokazuje, da neposedovani ID-ji ne dosežejo adapterja ponudnika.
Pushaj v obstoječo vejo PR-ja.
Poročaj o spremenjenih datotekah in testih.
```

## V.2 Pripravljenost na izdajo

Dokončanost funkcionalnosti ni isto kot pripravljenost na izdajo. Funkcionalnost lahko obstaja, pa je še vedno ni varno izdati. V OAP je pripravljenost na izdajo managerska odločitev, podprta s tehničnimi dokazi. Človek je lastnik kriterijev izdaje in od strateške UI zahteva, da dokaze zgosti v obliko, pripravljeno za odločitev.

<ExpandingSideImg
  src="../assets/fig-07-release-readiness.svg"
  alt="Pripravljenost na izdajo zahteva več kot zgolj implementirano kodo."
  caption="Pripravljenost na izdajo zahteva več kot zgolj implementirano kodo."
/>

### Ravni dokončanosti

OAP bi moral razlikovati med:

- prototipno dokončano;
- implementirano za ozek scenarij;
- testirano za pričakovani scenarij;
- testirano za negativne scenarije;
- dokumentirano;
- operativno obnovljivo;
- pregledano;
- kandidat za izdajo;
- pripravljeno za produkcijo.

To so različne trditve. Priročnik, README ali release note jih ne bi smeli zabrisati.

### Ocenjevanje pripravljenosti

Ocenjevanje pripravljenosti lahko pomaga, če je pošteno. Primer:

| Dimenzija | Vprašanje |
| --- | --- |
| Funkcionalna dokončanost | Ali je predvideno vedenje implementirano? |
| Kakovost arhitekture | Ali ustreza zasnovi sistema? |
| Varnostna drža | Ali so znana tveganja pod nadzorom? |
| Pokritost s testi | Ali testi dokazujejo osrednje in negativne scenarije? |
| Dokumentacija | Ali lahko uporabniki in operaterji razumejo obseg? |
| Operativna pripravljenost | Ali je mogoče sistem namestiti, opazovati in obnoviti? |
| Poštenost izdaje | Ali so omejitve jasno navedene? |

Ocene ne bi smele nadomestiti dokazov. Dokaze samo povzemajo.

### Povzetek odločitve o izdaji

Pred odločitvijo o izdaji bi morala strateška UI pripraviti kratek povzetek:

```markdown
## Povzetek odločitve o izdaji
Priporočilo: izdaj / ne izdaj / izdaj z omejitvami

Cilj:
- ...

Kriteriji izdaje:
- ...

Dokazi:
- CI:
- Testi:
- Varnost:
- Dokumentacija:
- Povrnitev:

Znane omejitve:
- ...

Potrebna odločitev:
- ...
```

Ta povzetek človeku omogoča, da deluje kot discipliniran vodja: najprej kratek tekst, nato neposredna vprašanja in šele nato ciljni pregled. Človeku ni treba rekonstruirati pripravljenosti na izdajo iz surovih PR-jev, dnevnikov in razpršenih zgodovin klepeta.

<Sidenote>
V OAP je jezik izdaje del tehnične pravilnosti. Sistem je lahko implementiran in še vedno napačno predstavljen, če dokumentacija ali trditve o izdaji prehitevajo dokaze.
</Sidenote>

### Vratca izdaje

Pred izdajo zahtevaj:

- ekspliciten cilj izdaje;
- eksplicitne kriterije izdaje;
- čisto delovno drevo;
- zeleno stanje vsega CI, relevantnega za izdajo;
- noben zahtevan test ne sme biti preskočen brez eksplicitne klasifikacije blokade;
- dokumentacija mora biti usklajena z implementiranim obsegom;
- znane omejitve morajo biti dokumentirane;
- varnostni pregledi morajo biti zaključeni;
- opombe o migraciji in rollbacku morajo biti pripravljene;
- končno človeško odločitev o izdaji.

### Nevarnost navidezne dokončanosti

Agentsko kodiranje lahko naredi projekt videti dokončan hitreje, kot postane koherenten. Hitro lahko doda datoteke, teste, dokumente in elemente uporabniškega vmesnika. Človeški vodja izdaje mora vprašati, ali ti deli sploh tvorijo sistem.

Pripravljenost na izdajo je disciplina, da se reče "še ne", kadar diff izgleda impresivno, dokazi pa so šibki.

<Question
  id="oap-release-readiness"
  question="Kaj priročnik obravnava kot ključno razliko med dokončanostjo funkcionalnosti in pripravljenostjo na izdajo?"
  options={["Dokončanost funkcionalnosti že sama po sebi pomeni pripravljenost za produkcijo", "Pripravljenost na izdajo je odvisna samo od tega, ali je CI enkrat uspel", "* Pripravljenost na izdajo je managerska presoja, podprta z dokazi, dokumentacijo, testi in operativnimi kriteriji", "Pripravljenost na izdajo v celoti določa poročilo izvajalnega agenta"]}
  attempts={2}
>
Priročnik dosledno ločuje med implementiranim vedenjem ter trditvami o izdaji, ki so podprte, testirane, dokumentirane in operativno poštene.
</Question>
