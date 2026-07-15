# Del IV: Kodiranje in preverjanje

## IV.1 Izvedbena plast

Izvedbena plast je kodirni agent, ki deluje nad repozitorijem. Dragocena je zato, ker lahko opravlja implementacijsko delo: premika se po datotekah, ureja kodo, namešča orodja, poganja testne ukaze, razlaga napake in iterira. Ni dragocena zato, ker bi si za vedno zapomnila celoten projekt. Kontinuiteta pripada strateški plasti in repozitoriju.

### Kaj mora imeti izvajalec v lasti

Izvajalec bi moral biti lastnik:

- mehanske implementacije;
- lokalnega raziskovanja;
- lokalne priprave odvisnosti in orodij znotraj izvajalne virtualke;
- priprave zavržljivih storitev za teste;
- ustvarjanja ali posodabljanja testov;
- izvajanja določenega preverjanja;
- popravljanja neuspehov znotraj obsega;
- dokumentiranja spremenjenega vedenja;
- ustvarjanja commitov in PR-jev;
- poročanja o natančnih izidih.

Izvajalec ne bi smel biti lastnik:

- strategije izdelka;
- trditev o izdaji;
- varnostnih izjem;
- odločitev o dostopu do produkcije;
- širokega širjenja obsega;
- končnih odločitev o mergeanju;
- dolgoročnega projektnega spomina;
- dodeljevanja rutinskih okoljskih opravil človeku.

### Izvajalec kot omejen implementator

Kodirni agent je najbolj uporaben, kadar je naloga dovolj ozka, da je uspeh mogoče oceniti. "Izboljšaj sistem" je preveč meglena zahteva. "Dodaj fail-closed preverjanje za neznane cene in teste, ki dokazujejo, da pred zavrnitvijo ne pride do nobenega klica k ponudniku" je boljše.

Izvajalcu ne bi smelo biti treba sklepati o načrtu izdaje. Ne bi smel odločati, ali funkcionalnost sodi v RC2. Prejeti mora omejeno nalogo in vrniti dokaze. Če za dokončanje te naloge potrebuje orodje, ga mora namestiti ali konfigurirati znotraj dovoljene izvedbene meje in o spremembi poročati.

### Ena naloga, en kontekst

Kontekst izvajalnega agenta je treba obravnavati kot potrošni delovni medpomnilnik. Trajati mora dovolj dolgo, da dokonča trenutno nalogo velikosti PR-ja, in nič dlje. Med nalogami je mogoče agenta kompaktirati, ponastaviti ali mu dati svež delovni nalog strateškega modela.

To preprečuje dve pogosti odpovedi:

- izvajalec kopiči zastarele predpostavke iz prejšnjega dela;
- človek skuša ohranjati kontekst tako, da izvajalcu ročno pripoveduje vsako podrobnost.

Strateški model nosi kontinuiteto. Izvajalec nosi akcijo. Repozitorij nosi resnico.

### Zahtevano poročilo izvajalca

Vsaka izvajalna naloga bi se morala končati s poročilom, kot je:

```markdown
## Poročilo agenta

Veja: feature/short-name
Commit: abc1234
Pull request: https://github.com/org/repo/pull/123

## Povzetek
- ...

## Spremenjene datoteke
- ...

## Zagnani testi
- ukaz: rezultat
- ukaz: rezultat

## Vpliv na dokumentacijo
- ...

## Varnostne potrditve
- Nobena produkcijska skrivnost ni bila commitana.
- Nobena nepovezana datoteka ni bila spremenjena.
- Noben preskočen test ni poročan kot uspešen.
- Nova lokalna orodja ali odvisnosti so nameščeni samo znotraj dovoljenega izvajalnega prostora.

## Znane omejitve
- ...

## Priporočeno nadaljevanje
- ...
```

To poročilo samo po sebi ni dokaz. Je kazalo do dokazov, ki jih lahko strateški model pregleda in ki jih lahko človek zaslišuje.

### Disciplina izvajalca

Izvajalni agenti bi morali:

- začeti iz pravilne veje;
- pregledati stanje pred urejanjem;
- ustvarjati majhne commite;
- uporabljati obstoječe projektne vzorce;
- izogibati se širokim refaktorjem, razen če so zahtevani;
- najprej poganjati usmerjene teste, širše pa po potrebi;
- nameščati dovoljene odvisnosti brez vpletanja človeka v rutinsko pripravo;
- ustaviti se in poročati o resničnih blokadah;
- nikoli ponarediti URL-ja PR-ja;
- nikoli trditi, da obstajajo CI rezultati, ki niso na voljo.

Najnevarnejši izvajalec ni tisti, ki odpove. Je tisti, ki glasno uspe, medtem ko tiho krši obseg.

## IV.2 Delegiranje v velikosti PR-ja

Atomska enota OAP je pull request. PR je dovolj majhen, da ga lahko strateški model globoko pregleda, dovolj velik, da ohrani uporaben implementacijski kontekst, in dovolj strukturiran, da nosi dokaze. Človeku ni treba privzeto prebrati vsake vrstice, vendar mora biti PR dovolj koherenten, da lahko človek od njega zahteva natančne odgovore.

<ExpandingSideImg
  src="../assets/fig-04-pr-pipeline.svg"
  alt="Cevovod delegiranja v velikosti PR-ja."
  caption="Cevovod delegiranja v velikosti PR-ja."
/>

### Zakaj deluje delo v velikosti PR-ja

Delegiranje v velikosti PR-ja ima več prednosti:

- prisili obseg;
- ustvari trajen diff;
- podpira CI;
- vabi k strateškemu pregledu in človeškemu zasliševanju;
- mogoče ga je povrniti;
- ohranja zgodovino;
- ločuje implementacijo od avtoritete za merge.

Zato je "en prompt, en PR" pogosto dobra privzeta izbira. Obstajajo izjeme: naloge, namenjene samo preiskavi, zagoni samo za preverjanje ali načrtovanje dokumentacije morda ne potrebujejo PR-jev. Implementacijsko delo pa bi praviloma moralo ustvariti pregledljivo vejo, ki jo lahko strateški model povzema, izziva in povezuje s testi.

### Anatomija naloge v velikosti PR-ja

Dobra naloga ima:

- ime;
- razlog;
- definiran obseg;
- eksplicitne necilje;
- relevantne datoteke;
- kriterije sprejema;
- teste;
- vpliv na dokumentacijo;
- zahteve za poročilo;
- dovoljeno lokalno pripravo ali delo z odvisnostmi.

Primer:

```text
Naloga: Dodaj preverjanje dovoljenj za endpoint brisanja elementa pogovora.

Trenutno stanje:
- Reference pogovorov obstajajo.
- Ustvarjanje/seznam/pridobivanje elementov je implementirano.

Cilj:
- Brisanje mora zahtevati eksplicitno dovoljenje za element pogovora.
- Neznani ali neposedovani ID-ji pogovorov morajo vrniti OpenAI-oblikovan 404 pred posredovanjem k ponudniku.

Necilji:
- Ne implementiraj posodabljanja pogovora.
- Ne spreminjaj Chat Completions.
- Ne dodajaj lokalne hrambe vsebine.

Testi:
- Dodaj unit teste za zavrnitev dovoljenja.
- Dodaj test posredovanja k ponudniku, ki dokazuje, da pri neposedovanem ID-ju ne pride do zunanjega klica.
- Poženi usmerjene teste in `ruff`.

PR:
- Nova veja iz `main`.
- Commitaj samo povezane datoteke.
- Odpri PR.
- Ne mergaj.
```

### Nadzor obsega

Najpomembnejši razdelek je pogosto "Necilji". Agenti so naučeni pomagati. Brez eksplicitnih neciljev se pomočljivost spremeni v širjenje obsega.

Necilji bi morali poimenovati:

- funkcionalnosti, ki se jih ne sme implementirati;
- datoteke, ki se jih ne sme dotikati;
- API-je, ki se jih ne sme spreminjati;
- migracije, ki se jih ne sme ustvarjati;
- odvisnosti, ki se jih ne sme dodajati;
- teste, ki se jih ne sme preskakovati;
- trditve, ki se jih ne sme podajati.

Pri visoko tveganih sistemih omejitve niso birokracija. So del pravilnosti.

### Popravljalni PR-ji

Včasih je PR odprt in potrebuje popravilo. Naslednji delovni nalog ne bi smel začeti nove funkcionalnosti, če ima trenutni PR padajoči CI, nerešene komentarje pregleda, varnostne pomisleke, odmik dokumentacije ali neodgovorjena človeška vprašanja o dokazih.

Popravljalni prompti morajo biti ožji od funkcionalnih:

```text
Popravi samo PR #123.
Ne dodajaj nove funkcionalnosti.
Preberi dnevnike padajočega CI.
Popravi najmanjši potrebni problem.
Padajoči test poženi lokalno.
Pushaj v isto vejo.
Poročaj o natančnem vzroku napake in popravku.
```

To preprečuje, da bi projekt kopičil napol veljavno delo.

## IV.3 Preverjanje in validacijski dolg

UI-kodiranje znižuje strošek generiranja. Ne zmanjšuje pa potrebe po dokazu. V mnogih primerih jo poveča, ker je generirana koda lahko verjetna, široka in hitra. OAP se s tem spopade tako, da loči zbiranje dokazov od predstavitve dokazov: izvajalec ustvari surove dokaze, strateški model jih stisne, človek pa zaslišuje stisnjen rezultat.

<ExpandingSideImg
  src="../assets/fig-05-validation-debt.svg"
  alt="Validacijski dolg."
  caption="Validacijski dolg."
/>

### Kaj pomeni validacijski dolg

Validacijski dolg je breme pregleda, testiranja in razmisleka, ki nastane, ko se koda generira hitreje, kot jo je mogoče razumeti. Podoben je tehničnemu dolgu, vendar se pojavlja na ravni procesa.

Validacijski dolg se kopiči, kadar:

- se veliki diffi generirajo hitro;
- so testi plitvi;
- agent spremeni nepovezane datoteke;
- poročilo pretirava z gotovostjo;
- pregledovalci zaupajo slogu namesto vsebini;
- dokumentacija trdi več, kot koda dokazuje.

Rešitev ni, da prenehamo uporabljati agente. Rešitev je omejiti delovno enoto, zahtevati dokaze in ohranjati človeško pregledno površino dovolj majhno, da podpira resnično presojo.

### Testi kot dokaz

Testi so dokaz samo, kadar pokrivajo trditev. Unit test dokazuje ozko vedenje. Integracijski test dokazuje interakcijo komponent. E2E test dokazuje uporabniško pot. Brskalniški smoke test dokazuje, da se naloži vsaj en vizualni delovni tok. Noben od njih ne dokazuje vsega.

Poročila OAP bi morala poimenovati obseg testov:

```markdown
Zagnani testi:
- `python -m pytest tests/unit/test_policy.py`: 18 uspešnih.
- `python -m pytest tests/integration/test_quota.py`: ni bilo pognano; `TEST_DATABASE_URL` ni konfiguriran.
- `ruff check app tests`: uspešno.
```

To je boljše kot:

```markdown
Vsi testi so uspešni.
```

### Preskočeni testi so neznanka

Eno najpomembnejših pravil OAP je:

> Preskočen test ni uspešen test. Test, ki ni bil pognan, ni dokaz.

To pravilo bi se moralo pojaviti v konstituciji. Agenti so pogosto željni pomoči in povzamejo delni uspeh kot uspeh. Takšno vedenje je treba popraviti.

### Smiselni testi

Kakovost testa je pomembna. Test je lahko nesmiseln, če:

- preverja implementacijske podrobnosti, ne da bi preverjal vedenje;
- preverja le, da funkcija nekaj vrne;
- z mocki odstrani samo tveganje, ki bi ga moral testirati;
- reproducira trenutno napako kot pričakovano vedenje;
- uporablja generiran pričakovani izhod brez neodvisnega sklepanja.

Strateška plast bi morala vprašati: če bi bila ta funkcionalnost pokvarjena na nevaren način, ali bi test odpovedal? Človek bi moral biti sposoben zastaviti isto vprašanje in dobiti jedrnat odgovor s kazalcem na relevantni test.

### Zgolj preverjevalni zagoni

Včasih naslednja naloga ne bi smela biti implementacija. Morala bi biti preverjanje. Prompt za zgolj preverjevalni zagon bi moral prepovedati urejanje:

```text
To je zgolj preverjevalni zagon.
Ne ustvarjaj veje.
Ne urejaj datotek.
Ne commitaj.
Poženi določene ukaze preverjanja.
Poročaj o natančnih rezultatih, preskočenih testih in blokadah.
```

Takšni zagoni so uporabni pred izdajo, po velikih mergeih ali kadar strateška plast sumi, da so poročila preozka.

## IV.4 Varnost med implementacijo

OAP predpostavlja, da so agenti lahko dovolj zmogljivi, da povzročijo škodo. Varnostna pravila morajo biti zato eksplicitna, ponovljena, testirana in kodirana v konstituciji.

### Odpovej v zaprto stanje

Vedenje fail-closed pomeni, da se negotova ali nepodprta stanja varno zavrnejo, namesto da bi bila optimistično prepuščena skozi sistem.

Primeri:

- neznane cene zavrnejo zahtevo, omejeno s stroškom;
- neznana sposobnost poti zavrne posredovanje;
- neposedovani ID-ji virov vrnejo odgovor `not found` pred dostopom do ponudnika;
- slabi host ključi ustavijo SSH delovni tok pred vnosom poverilnic;
- manjkajoča testna baza blokira integracijske trditve;
- nepodprte funkcionalnosti ponudnika vrnejo eksplicitne napake o nepodprtosti.

Fail closed je drža zasnove. Še posebej je pomembna takrat, ko bi izvajalni agent sicer skušal "spraviti stvar v delovanje" z rahljanjem validacije.

### Skrivnosti

Izvajalno okolje agenta ne bi smelo vsebovati produkcijskih skrivnosti. Repozitorij ne bi smel vsebovati pravih ključev ponudnikov. Dnevniki ne bi smeli vsebovati poverilnic. Dokumentacija bi morala uporabljati placeholderje.

Konstitucija bi morala reči:

```markdown
## Skrivnosti
- Nikoli ne commitaj pravih ključev ponudnikov.
- Nikoli ne shranjuj ključev gatewaya v čistem besedilu.
- Nikoli ne izpisuj tokenov v izhodu testov.
- Nikoli ne lepi produkcijskih skrivnosti v prompte.
- V dokumentaciji in testih uporabljaj lažne placeholderje.
- Če se skrivnost pojavi v izhodu, se ustavi in poročaj.
```

Pri sistemih s kodirnimi agenti to ni neobvezno. Zgodovina promptov, dnevniki orodij, zgodovina lupine, izhod testov, telemetrija in komentarji v PR-jih lahko vsi postanejo nenamerni kanali razkritja.

### Vratca odobritev

Človeška odobritev je potrebna za:

- produkcijsko namestitev;
- merge v zaščitene veje;
- destruktivne podatkovne operacije;
- rotacijo poverilnic;
- javne trditve o izdaji;
- dodajanje tveganih odvisnosti;
- širjenje dostopa do omrežja;
- spremembo varnostne drže.

Codex dokumentira sandbox in plasti odobritev kot ločeni kontroli: način sandboxa določa, kaj agent tehnično lahko stori, politika odobritev pa določa, kdaj mora vprašati [[15]](#ref-codex-security). OAP uporablja isti koncept ločevanja na ravni procesa. Meja izvajalnega okolja nadzira, kaj se lahko zgodi. Človeško vratce nadzira, kaj je sprejeto.

### Varnostni pregledi

Pri varnostno občutljivih projektih bi morala izvajalna poročila vključevati preglede, kot so:

```bash
rg "api_key|Authorization|Bearer|password|secret|token" app tests docs -n
git diff --check
python -m pytest tests/unit
ruff check app tests
```

Točni ukazi so odvisni od sklada. Pomembno je, da so varnostna preverjanja poimenovana in ponovljiva.

### Izogibanje nevarni uslužnosti

Agenti lahko skušajo:

- onemogočiti padajoči test;
- zrahljati validacijo;
- dodati preširok catch-all;
- mockati napačno mejo;
- preskočiti težko integracijsko pot;
- uporabljati resnične storitve, ker so mocki neprijetni;
- narediti dokumentacijo bolj dokončano, kot je resničnost.

Strateška plast mora takšne bližnjice kaznovati. V OAP "deluje" ni dovolj. Sprememba mora delovati znotraj pravil projekta.

## IV.5 Dokumentacija, predaje in spomin

Delovni tokovi z UI potrebujejo trajen spomin. Prepisi klepeta so koristni, vendar niso dovolj. Postanejo dolgi, zastareli, nedostopni ali težko preiskljivi. OAP dokumentacijo obravnava kot operativni spomin za ljudi in agente. Dokumentacija mora tudi zmanjševati bralno breme: kratki povzetki naj kažejo na globlje podrobnosti, namesto da bi moral vsak prihodnji bralec projekt rekonstruirati iz klepeta.

### Vrste dokumentacije

Zrel projekt OAP pogosto potrebuje:

- README;
- quickstart;
- pregled arhitekture;
- varnostni model;
- matriko združljivosti;
- priročnik za namestitev;
- runbooke;
- priročnik za testiranje;
- release notee;
- arhiv pregledov;
- matriko sanacije;
- handoff dokumente.

Vsak projekt ne potrebuje vsega tega. Vsak resen projekt pa potrebuje dovolj dokumentacije, da lahko nov človek, strateški model ali izvajalni agent varno nadaljuje delo.

### Predaje

Handoffi rešujejo prenos konteksta. Pisani bi morali biti za naslednjo strateško sejo, ne za končnega uporabnika. Dober handoff mora biti dovolj kratek za hitro ponovno nalaganje konteksta, hkrati pa mora kazati na trajne dokaze. Vključuje:

- trenutno resnico repozitorija;
- nedavno mergane PR-je;
- odprte PR-je;
- znane blokade;
- implementirani obseg;
- manjkajoči obseg;
- varnostna pravila;
- naslednjo priporočeno nalogo;
- naloge, ki jih eksplicitno ni priporočljivo delati.

Handoffov nikoli ne bi smeli obravnavati kot avtoritativnih nad živim repozitorijem. So posnetki. Prvi korak po branju handoffa je preverjanje.

### Dokumentacija kot pogodba

Dokumentacija mora slediti vedenju. Če je endpoint implementiran, se spremeni matrika združljivosti. Če funkcionalnost namerno ni podprta, naj to dokumenti povedo. Če je izdaja beta, dokumenti ne smejo nakazovati produkcijske certifikacije.

To je del OAP discipline poštenosti. Generirana koda lahko zelo hitro ustvari videz zrelosti. Dokumentacija mora to uravnotežiti z navajanjem dejanskega obsega.

### Operativni priročniki

Runbooki so postopki za odpovedi in operacije:

- rotacija ključev;
- odziv na kompromitiran ključ;
- backup in restore baze;
- izpad Redisa;
- dvoumnost pri e-pošti;
- zaklenjen admin račun;
- rollback namestitve;
- odziv na alarme metrik.

Agenti lahko osnutke runbookov pripravijo, vendar morajo ljudje zagotoviti, da si ne izmišljajo ukazov ali obljubljajo nepodprtih poti za obnovo.

<Question
  id="oap-pr-sized-delegation"
  question="Zakaj OAP daje prednost delegiranju v velikosti PR-ja pred širokimi, odprtimi implementacijskimi nalogami?"
  options={["Ker pull requesti odpravijo potrebo po testih", "* Ker delo v velikosti PR-ja ohranja obseg pregledljiv, ohranja dokaze in omejuje drsenje konteksta", "Ker izvajalnemu agentu omogoča lastništvo strategije izdelka", "Ker odpravi potrebo po strateškem povzetku pregleda"]}
  attempts={2}
>
Naloge velikosti PR-ja so dovolj majhne za pregled in preverjanje, hkrati pa dovolj velike, da nosijo uporaben implementacijski kontekst in trajne dokaze.
</Question>
