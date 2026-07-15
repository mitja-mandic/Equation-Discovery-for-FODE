# Del VII: Razprava in doktrina

## VII.1 Načini odpovedi

OAP je zasnovan okoli načinov odpovedi, ki se v programski opremi, podprti z UI, pojavljajo znova in znova.

### Halucinirani API-ji in odvisnosti

Modeli si lahko izmislijo metode knjižnic, konfiguracijske zastavice, pakete ali oblike endpointov. Halucinacije paketov so bile raziskovane kot tveganje v dobavni verigi, ker lahko neobstoječi paketi postanejo tarče napada, če jih napadalci pozneje objavijo [[48]](#ref-package-hallucination).

Ublažitev:

- preverjaj uradno dokumentacijo za nestabilne API-je;
- poženi kodo;
- pripni odvisnosti na točne različice;
- ne dodajaj odvisnosti mimogrede;
- testiraj dejanske uvozne poti.

### Plitvi testi

Agenti lahko generirajo teste, ki potrjujejo kodo, ki so jo pravkar napisali, namesto vedenja, ki je dejansko pomembno.

Ublažitev:

- zahtevaj negativne teste;
- kadar je praktično, zahtevaj teste, ki odpovedo pred popravkom;
- pregleduj mocke;
- vprašaj, ali test res ščiti pred tveganjem.

### Drsenje konteksta

Dolge seje drsijo. Model si zapomni stare stanja PR-jev, zastarelo arhitekturo ali pretečene odločitve. OAP to tveganje razcepi: strateški model bi moral ohranjati dolg kontekst, izvajalni agent pa ne bi smel nositi predpostavk čez več kot eno nalogo.

Ublažitev:

- preverjaj trenutno stanje repozitorija;
- piši handoffe;
- ohranjaj konstitucijo aktualno;
- daj prednost živemu viru pred spominom iz klepeta;
- med nalogami velikosti enega PR-ja izvajalnega agenta kompaktiraj ali ponastavi.

### Šibek strateški model

OAP odpove, če je strateška plast za svojo vlogo prešibka. Poceni ali kratkokontekstni model lahko samozavestno povzema, medtem ko spregleda arhitekturni odmik, varnostne implikacije ali nerešene človeške cilje.

Ublažitev:

- za strategijo uporabljaj najmočnejši praktični model;
- strateški kontekst ohranjaj čist in dolgoživ;
- zahtevaj eksplicitno mapiranje dokazov;
- za visoko tvegane odločitve uporabljaj križno revizijo med modeli;
- handoffe piši, preden kontekst postane krhek.

### Inverzija nadzora

Do inverzije nadzora pride, ko izvajalni agent začne voditi človeka. Simptomi vključujejo ponavljajoče zahteve, da človek namešča pakete, poganja ukaze, lepi dnevnike, popravlja okolja ali odloča o nizkoravenskih implementacijskih podrobnostih, ki bi morale soditi v izvajalno virtualko.

Ublažitev:

- agentu daj dovolj pravic znotraj utrjene virtualke;
- produkcijske skrivnosti in nenadomestljivo stanje drži zunaj te virtualke;
- zahtevaj, da agent dokumentira lokalno pripravo;
- zavržljiva okolja ponovno zgradi namesto ročnega pestovanja;
- človeške odločitve vodi prek strateškega modela.

### Prekomerno breme človeškega branja

OAP odpove, če mora človek za vsako majhno odločitev brati velike diffe, dolge dnevnike in razvlečena poročila. To ponovno ustvari delovno ozko grlo, samo na drugi ravni.

Ublažitev:

- zahtevaj kratke povzetke odločitve;
- od strateške UI zahtevaj zaključek, dokaz, tveganje in odločitev;
- poglobi se samo, kadar to zahtevata tveganje ali negotovost;
- PR-je ohranjaj dovolj majhne za strateški pregled;
- prepovej meglena poročila, ki zahtevajo rekonstrukcijo.

### Širjenje obsega

Agenti lahko implementirajo sosednje funkcionalnosti, ker so videti povezane.

Ublažitev:

- eksplicitni necilji;
- naloge velikosti PR-ja;
- zavračanje preširokih diffov;
- popravljanje obsega pred mergeanjem.

### Pretiravanje v trditvah

Agenti in ljudje lahko precenijo pripravljenost. "Implementirano" postane "podprto". "Usmerjeni testi so uspešni" postane "v celoti testirano". "RC" postane "pripravljeno za produkcijo."

Ublažitev:

- standardno besedišče poročil;
- kontrolni seznam pripravljenosti na izdajo;
- pregled dokumentacije;
- zunanja revizija.

### Uhajanje poverilnic

Agenti lahko razkrijejo skrivnosti prek promptov, dnevnikov, commitov, posnetkov zaslona ali telemetrije.

Ublažitev:

- brez produkcijskih skrivnosti v izvajalnem okolju agenta;
- pregledi skrivnosti;
- lažni placeholderji;
- redigirana telemetrija;
- brez shranjevanja surovih promptov ali payloadov, razen če je to namerno zasnovano.

### Človeška samozadostnost

Končni način odpovedi je človeška samozadostnost. OAP odpove, če človek preneha presojati. Proces lahko zlahka ustvari občutek produktivnosti, medtem ko se sprejema preveč. Prehod v managersko vlogo ne pomeni pasivnosti. Pomeni strožjo disciplino glede ciljev, kriterijev izdaje, dokazov in tveganj.

Ublažitev:

- upočasni se pri vratcih odločanja;
- zahtevaj kratke povzetke dokazov;
- pojdi globlje, ko so dokazi šibki;
- prosi za zunanji pregled;
- vsak merge obravnavaj kot človeško odločitev.

## VII.2 Praktična doktrina OAP

To poglavje zgosti priročnik v doktrino: pravila, ki lahko vodijo resnične projekte.

### Temeljna načela

1. **Človek se pomakne višje po lestvici.** Človek ni več predvsem koder; človek upravlja cilje, kriterije, tveganje in izdajo.
2. **Domensko znanje lahko vodi.** Najboljši človeški vodja je lahko oseba, ki razume domeno, ne oseba, ki piše kodo.
3. **Začni s strateškim odkrivanjem.** Pred kodiranjem vprašaj, kakšen sistem je potreben, katera orodja ustrezajo in kje so meje.
4. **Človek je lastnik namena.** Nikoli ne oddajaj pomena izdelka.
5. **Človek je lastnik tveganja.** Model ne more sprejeti odgovornosti.
6. **Človek je lastnik izdaje.** Agent ne odloča o pripravljenosti.
7. **Človek dela iz kratkega odločitvenega gradiva.** Strateška UI mora podrobnosti stisniti v povzetke, vezane na dokaze.
8. **Strateška UI je kontrolna ravnina.** Uporabi najmočnejši praktični dolgokontekstni model za odkrivanje arhitekture, izbiro tehnologije, spomin, kritiko, prevajanje domene, delovne naloge in dokaze.
9. **Izvajalni agent je zavržljivo delo.** Njegov kontekst naj traja eno nalogo velikosti PR-ja.
10. **Strategija in izvedba sta ločeni.** Načrtovanje in mutacija repozitorija naj bosta različni vlogi.
11. **Konstitucija vlada.** Trajna pravila premagajo ponavljajoče opomnike.
12. **Avtonomija živi znotraj obnovljive meje.** Visoki privilegiji so sprejemljivi samo v utrjenem zavržljivem izvajalnem okolju.
13. **Oddaljeni repozitorij je resnica.** Virtualka je zavržljiva; veje, PR-ji, CI, dokumenti in handoffi so trajni.
14. **PR je enota.** Delo mora biti pregledljivo, povrnljivo in dokazano.
15. **Necilji so varnostna orodja.** Povej, česa ni dovoljeno narediti.
16. **Testi so dokaz, ne ritual.** Ujemi teste s trditvami.
17. **Preskočeno ni uspešno.** Neznano ostaja neznano.
18. **Dokumentacija je del artefakta.** Vedenje in trditve se morajo ujemati.
19. **Revizija je normalna.** Zunanja kritika ni neuspeh.
20. **Jezik izdaje mora biti pošten.** Beta pomeni beta.
21. **Hitrost ne sme prehiteti presoje.** Hitrejše kodiranje poveča odgovornost validacije.
22. **Nikoli ne dovoli, da agent vodi človeka.** Če človek opravlja rutinsko pripravo namesto agenta, preoblikuj izvajalno okolje.

### Minimalno vzdržen OAP

Za majhen, a resen projekt:

- opravi pogovor strateškega odkrivanja;
- odloči obliko izdelka, sklad, meje zaupanja in obseg prve izdaje;
- ustvari `AGENTS.md`;
- uporabi zmogljiv strateški model kot človeku obrnjen kontrolni vmesnik;
- uporabi namensko vejo za vsako nalogo;
- piši delovne naloge s ciljem, necilji, testi in obliko poročila;
- poganjaj usmerjene teste;
- zahtevaj PR;
- pred mergeanjem pripravi kratek povzetek odločitve;
- človek pred mergeanjem zaslišuje dokaze;
- vodi preprost handoff dokument.

### Zrel OAP

Za večji projekt:

- dokumentirano strateško odkrivanje in utemeljitev arhitekture;
- večslojne konstitucije;
- namensko izvajalno virtualko;
- način visoke avtonomije znotraj utrjenega obnovljivega izvajalnega okolja;
- kjer je varno, brezgeselne lokalne privilegije za pripravo;
- brez produkcijskih skrivnosti ali nenadomestljivih podatkov v virtualki;
- premijski dolgokontekstni strateški model;
- ponastavitev ali kompaktiranje konteksta izvajalca po vsakem PR-ju;
- zaščitene veje;
- vratca CI;
- varnostne preglede;
- zunanji pregled z drugim modelom;
- runbooke;
- ocenjevanje pripravljenosti na izdajo;
- povzetke odločitve o izdaji;
- končni verifikacijski harness;
- arhivirane revizijske ugotovitve.

### Posvojitev v ekipi

Ekipe bi morale začeti z nizkotveganimi nalogami:

- izboljšave dokumentacije;
- dodajanje testov;
- majhni popravki hroščev;
- refaktorji z močnimi testi;
- interna orodja.

Nato naj se razširijo proti funkcionalnemu delu, ko ekipa zaupa:

- kakovosti konstitucije;
- predlogam promptov;
- izolaciji izvajalnega okolja;
- disciplini strateškega pregleda;
- kakovosti povzetkov odločitve;
- pokritosti CI.

Cilj ni takoj maksimirati avtonomije. Cilj je povečati avtonomijo samo tam, kjer jo podpirajo dokazi in meje.

## VII.3 Sklepi

OAP spremeni, kam sodi človeška pozornost. Človeku ni več treba biti oseba, ki namešča vsako odvisnost, piše vsako boilerplate datoteko in sledi vsakemu tracebacku. Človek postane oseba, ki določa cilj, postavlja strateška vprašanja, odloča o sprejemljivem tveganju in zahteva dokaze.

To ni zmanjšanje odgovornosti. To je premestitev odgovornosti. Človek je še vedno odgovoren za to, kar je izdano. Razlika je v tem, da človek upravlja prek arhitekture, konstitucije, delovnih nalogov, testov, revizij in odločitev o izdaji, namesto prek neprekinjenega nizkoravenskega kodiranja.

Trajna lekcija je preprosta:

```text
Strateški model: prevedi namen v arhitekturo in vprašanja o dokazih.
Izvajalni agent: opravi omejeno implementacijsko delo znotraj zavržljivega izvajalnega okolja.
Človeški upravljavec: prevzemi cilj, tveganje, izdajo in domensko pravilnost.
Repozitorij: ohranjaj resnico.
```

Ko ta zanka deluje, postane agentsko programiranje manj podobno klepetu z generatorjem kode in bolj upravljanju hitre, disciplinirane implementacijske delavnice. Ko odpove, praviloma odpove tako, da se hierarhija sesuje: izvajalni agent začne voditi človeka, strateški model žigosa meglena poročila ali pa repozitorij preneha biti izvor resnice.

Metoda torej ni "zaupaj agentu". Metoda je: "zasnuj kontrolni sistem tako, da je agent lahko uporaben, ne da bi mu bilo treba zaupati kot končni avtoriteti."

<Question
  id="oap-doctrine-antipilot"
  question="Katera trditev najbolje ustreza priročnikovi doktrini proti temu, da agent pilotira človeka?"
  options={["Človek bi moral opravljati rutinsko pripravo za agenta, da agent ostane preprost", "Strateški model bi moral brez človeškega pregleda potrditi lastne dokaze", "* Izvajalni agent ne bi smel usmerjati človeka prek nizkoravenskih opravil; kontrolni sistem mora biti zasnovan tako, da človek ostane na odločitveni ravni", "Če agent zveni samozavestno, kontrolna zanka deluje pravilno"]}
  attempts={2}
>
Pravilo proti pilotiranju je v priročniku eksplicitno: če izvajalni agent začne človeka usmerjati skozi rutinsko nizkoravensko delo, se je kontrolna zanka obrnila in delovni tok je treba preoblikovati.
</Question>
