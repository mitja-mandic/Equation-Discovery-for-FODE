# Del VI: Študije primerov in uporabe

## VI.1 Študija primera: SLAIF API Gateway

To poglavje uporablja javni projekt kot ilustrativen primer: OpenAI-združljiv API gateway za izdajo omejenih ključev gatewaya, pri čemer so izvorne poverilnice ponudnikov zaščitene [[37]](#ref-slaif-repo). Bistvo ni specifična domena. Bistvo je delovni tok.

### Oblika problema

Problemski okvir izdelka ni bil "naredi aplikacijo". Šlo je za resen sistem:

- OpenAI-združljivo vedenje odjemalca;
- ključi, ki jih izdaja gateway;
- uveljavljanje kvot;
- usmerjanje k ponudnikom;
- obračunavanje uporabe;
- administratorske operacije;
- varno ravnanje s ključi;
- dokumentacijo za namestitev in operaterje.

Takšen sistem je dober kandidat za OAP, ker ima jasne invariante, veliko mehanskih implementacijskih rezin in visoko varnostno tveganje. Hkrati je dober primer, zakaj se mora človek pomakniti višje po lestvici: pomembno človeško delo ni tipkanje CRUD handlerjev, ampak upravljanje invariantov, trditev o izdaji, varnostne drže in dokazov.

### Arhitekturno odkrivanje

Prvo managersko dejanje ni bilo, da bi agenta prosili za generiranje endpointov. Bilo je vprašanje strateškemu modelu, kakšen sistem domenski problem sploh zahteva in katere tehnične sestavine so primerne. Človek je podal domensko potrebo: veliko uporabnikov potrebuje praktičen dostop do LLM API-ja, institucija pa mora zaščititi poverilnice ponudnikov, uveljavljati omejitve porabe, obračunavati uporabo in sistem varno upravljati. Strateški model je to prevedel v arhitekturo: OpenAI-združljiv gateway, strežniški ključi ponudnikov, ključi, ki jih izdaja gateway, PostgreSQL-podprte trde kvote in obračunavanje, Redis kot neobvezno operativno omejevanje, admin tokove, ozadna opravila, teste in dokumentacijo za namestitev.

To je pomembno, ker lahko domenski strokovnjak problem razume globoko, ne da bi poznal trenutno najboljši programski sklad. OAP uporablja strateški model za premostitev te vrzeli. Človek ostane upravljavec in domenska avtoriteta; strateški model predlaga arhitekturo in kompromisne odločitve; izvajalni agent kasneje implementira omejene rezine.

Enak vzorec se pojavi v primeru naprave DHCP/IPAM. Domenski problem ni bil "naredi DHCP spletni vmesnik". Bil je "varno upravljaj stanje DHCP/IPAM/DNS na zamenljivih robnih napravah Raspberry Pi". Strateško odkrivanje je spremenilo obliko programske opreme: strežniški izvor resnice, odhodne povezave robnih naprav, podpisani artefakti želenega stanja, minimalen lokalni pomočnik za uporabo nastavitev, validacija `dnsmasq`, rollback, revizijski dnevniki in javni pogled, ki mora biti očiščeni posnetek, ne pa skriti administratorski nadzor. Ta arhitektura je managerski izhod, še preden postane implementacijska naloga.

### Najprej konstitucija

Zgodnji artefakt ni bila koda. Bil je podroben implementacijski brief in datoteka upravljalnih navodil, nastala v fazi strateškega odkrivanja. To je izvajalnemu agentu omogočilo delo znotraj omejitev, namesto da bi arhitekturo odkrival z improvizacijo.

Konstitucija je kodirala:

- izbire sklada;
- varnostna pravila;
- pričakovanja o testiranju;
- PR delovni tok;
- zahteve glede dokumentacije;
- prepoved uporabe pravih ključev ponudnikov;
- prepoved shranjevanja ključev gatewaya v čistem besedilu;
- prepoved pretiravanja s trditvami o produkcijski pripravljenosti.

### Zaporedje PR-jev

Projekt je napredoval skozi veliko majhnih PR-jev. Vsak PR je implementiral ali utrdil eno rezino: shemo, storitev za ključe, rezervacijo kvote, usmerjanje k ponudnikom, admin UI, dokumentacijo, teste, runbooke, družine funkcionalnosti in preverjanje izdaje.

To je pomembno, ker agentsko delo postane pregledljivo, ko je narezano. Velika avtonomna implementacija bi ji bilo veliko težje zaupati. Rezanje je hkrati ščitilo kontekst: izvajalni agent se je lahko osredotočil na eno nalogo, medtem ko sta strateški model in dokumentacija ohranjala širšo zgodbo.

### Kontrolna ravnina v praksi

Človeku obrnjeno delo ni bilo neprekinjen neposreden pogovor z izvajalnim agentom. Koristna človeška vprašanja so bila managerska:

- Ali se gateway še vedno zapira v fail-closed načinu?
- Kateri testi dokazujejo uveljavljanje kvot?
- Katere skrivnosti bi lahko uhajale?
- Kaj je implementirano in kaj je samo dokumentirano?
- Kaj še manjka pred izdajo?

Ta vprašanja sodijo v strateško plast. Strateški model jih pretvori v delovne naloge, povzetke pregledov, sezname sanacije in povzetke pripravljenosti na izdajo. Izvajalni agent delovne naloge pretvori v veje, teste in PR-je.

### Revizija in odprava pomanjkljivosti

Zunanji pregled z modelom je bil uporabljen za oceno arhitekture, varnostne drže, pokritosti s testi, dokumentacije in produkcijske pripravljenosti. Ugotovitve so bile pretvorjene v sanacijsko delo, ne pa obravnavane kot pohvala. Javni arhiv pregledov in matrika sanacije sta pomembna zato, ker naredita revizijsko zanko pregledljivo, ne pa anekdotično [[43]](#ref-slaif-reviews-archive); [[44]](#ref-slaif-remediation-matrix).

Revizija RC1 ni zgolj rekla, da je projekt dober. Podala je managersko presojo: implementirani obseg je verodostojen kot RC-beta, ne pa kot produkcijska certifikacija, skladnostna attestacija ali penetracijsko testiranje. Ugotovila je tudi konkretno preostalo delo, vključno z ocenjevanjem vhodnih tokenov/stroškov pri Chat Completions zunaj polj message, testi invariant za kvote/obračunavanje/usklajevanje in produkcijskimi runbooki [[45]](#ref-slaif-review6). Te ugotovitve so postale omejeno delo:

- problem ocenjevanja vhodov, ki niso del message, je bil popravljen kot usmerjena sanacija politike, cen, kvot in posredovanja k ponudnikom;
- dodani so bili testi invariant za kvote, obračunavanje, usklajevanje, idempotentnost ter varne metapodatke knjige in revizije;
- dodani so bili operaterski runbooki za rotacijo ključev, odziv na razkritje ključa, ravnanje s HMAC in enkratnimi skrivnostmi, backup/restore, usklajevanje, izpad Redisa, pripravljenost PostgreSQL, metrike, odpravljanje težav pri namestitvi in RC-beta nadgradnje.

To pokaže osrednjo trditev OAP: človeku ni treba osebno implementirati vsakega popravka, vendar mora človek upravljati zanko kakovosti. Človek odloča, katere revizijske ugotovitve so napake trenutnega obsega, katere sodijo v prihodnje delo, katere zahtevajo teste in katere trditve o izdaji so dovoljene. Strateška UI to odločitev pretvori v natančne delovne naloge. Izvajalni agent opravi implementacijo in preverjanje. Repozitorij ohrani dokaze.

To je OAP pregledna zanka:

1. Zgradi z izvajalnim agentom.
2. Preglej s strateškim modelom.
3. Revidiraj z zunanjim modelom ali pregledovalcem.
4. Postavi človeška managerska vprašanja o cilju, tveganju in kriterijih izdaje.
5. Ugotovitve pretvori v delo velikosti PR-ja.
6. Preveri in dokumentiraj zaprtje.

### Nauki

Primer ilustrira več splošnih naukov:

- Kodirni agent lahko opravi veliko količino implementacijskega dela.
- Človek ne izgine; človek postane bolj managerski in pomembnejši pri vratcih odločanja.
- Domensko znanje ostaja odločilno: človek mora razumeti, zakaj so pomembni kvota, izolacija ključev ponudnikov, izdaja uporabniških ključev, obračunavanje in delavniške operacije.
- Strateški model mora dokaze stisniti v kratko odločitveno gradivo.
- Izvajalno okolje mora agentu omogočiti pripravljalno delo brez vpletanja človeka.
- Dokumentacija in runbooki niso naknadna misel.
- Testi postanejo jezik zaupanja.
- Poštenost izdaje preprečuje, da bi se agentska hitrost spremenila v lažno zrelost.

## VI.2 Uporaba OAP pri drugih projektih

OAP ni omejen na API gatewaye. Metoda se posploši po vzorcu: prepoznaj domenski cilj, napiši konstitucijo, nareži delo v PR-je, ohrani izvajalno okolje zavržljivo, ohrani resnico repozitorija in pregleduj prek dokazov. Javni repozitoriji se lahko nato uporabljajo kot primeri primerov uporabe, ne pa kot dokaz, da je vsak projekt dokončan ali produkcijsko certificiran.

Spodnje primere je treba brati na dveh ravneh:

1. **splošni primer uporabe**, ki je ponovno uporabno vodilo;
2. **vidni primer repozitorija**, kjer javni repozitorij obstaja in prikazuje vzorec.

Zasebni ali interni projekti lahko še vedno informirajo vzorec, vendar jih ne bi smeli predstavljati kot javne primere. Če repozitorij ni viden, opiši primer uporabe brez pretvarjanja, da obstaja javni URL.

### Konceptualne demonstracije skozi primere

**Človek kot upravljavec in domenski strokovnjak.** To je prikazano v primerih API gatewaya, SLAIF Connect in naprave DHCP/IPAM. Človek je določil produktne invariante: zaščititi ključe ponudnikov, ne zbirati SSH poverilnic, ne izpostaviti vhodnega upravljanja Pi-jev in ohraniti poštene trditve o izdaji.

**Strateško odkrivanje in izbira orodij.** Najjasneje je prikazano v primerih API gatewaya in DHCP/IPAM. Človek je vprašal, kakšen sistem je potreben in katera orodja ustrezajo domeni; strateški model je to prevedel v arhitekturo gatewaya, odločitve o kvotah/obračunavanju, strežniške meje in meje kontrolne ravnine, meje robnega agenta in varne prve mejnike.

**Izvedba po načelu najprej konstitucija.** To je prikazano v delih za API gateway in začetni skelet DHCP/IPAM. Agent je pred široko implementacijo prejel arhitekturo, necilje, varnostna pravila, teste in obliko poročila.

**Izvajalni agent kot implementacijsko delo.** To je prikazano s sekvencami javnih PR-jev in imeni vej v vidnih repozitorijih. Izvajalec je skrbel za spremembe v repozitoriju, teste, dokumentacijo in mehaniko PR-jev, človek pa je ostal osredotočen na odločitve.

**PR kot enota dela.** To je prikazano v primerih API gatewaya, SLAIF Connect in DHCP/IPAM. Delo je ostalo pregledljivo, povrnljivo in pripisljivo. Kasnejše revizijske ugotovitve so se lahko spremenile v ozke PR-je namesto v meglene popravljalne kampanje.

**Oddaljeni repozitorij kot resnica projekta.** To je prikazano prek javnih GitHub repozitorijev in arhivov pregledov. Trajna resnica je živela v vejah, PR-jih, dokumentih, CI, preglednih datotekah in matrikah sanacije, ne pa v lokalni virtualki agenta.

**Križna revizija med modeli in sanacija.** To je prikazano v arhivu pregledov SLAIF API Gatewaya. Zunanja kritika je našla za izdajo pomembne težave, ki so bile pretvorjene v sanacijsko delo z dokaznim gradivom preverjanja.

**Poštenost izdaje.** To je prikazano z jezikom RC-beta pri SLAIF API Gatewayu. Projekt je lahko trdil RC-beta pripravljenost za implementirani obseg, ne da bi se pretvarjal, da je produkcijsko certificiran.

**Upravljanje validacijskega dolga.** To je prikazano prek testov, matrik združljivosti, runbookov in matrik sanacije. Hitra implementacija je bila uravnotežena z močnejšimi dokazi, dokumentacijo za operaterje in eksplicitnimi znanimi omejitvami.

### Pisanje nove programske opreme

Splošni koncept: OAP dobro deluje pri greenfield programski opremi, kadar človek lahko definira močan produktni cilj in začne s strateškim odkrivanjem. Prvi praktični artefakt je lahko konstitucija, prvi intelektualni artefakt pa je razprava o arhitekturi: kakšen sistem je to, katera orodja ustrezajo, kje so meje zaupanja in česa prva izdaja ne bi smela poskušati.

Ključna managerska poteza je izogniti se promptu "naredi mi aplikacijo". Človek bi moral namesto tega definirati:

- čemu je izdelek namenjen;
- katera kategorija izdelka ali arhitektura je primerna;
- katera orodja in ogrodja so verjetna;
- kaj se nikoli ne sme zgoditi;
- kaj sme trditi prva izdaja;
- kako se bodo preverjali dokazi;
- kateri deli so namenoma izven obsega.

Vidni primeri:

- **SLAIF API Gateway**: javni OpenAI-združljiv gateway za institucionalni dostop do LLM-jev, uveljavljanje kvot, usmerjanje k ponudnikom, obračunavanje uporabe in operaterske tokove [[37]](#ref-slaif-repo). Prikazuje greenfield OAP na ravni resnega izdelka: najprej specifikacija, nato veliko implementacijskih rezin velikosti PR-ja, močni varnostni invarianti, široki testi, dokumentacija, release notei in zunanji pregled.
- **Managed DHCP/IPAM Edge Appliance**: javni repozitorij za zgodnjo fazo upravljanja robnih naprav DHCP/IPAM [[46]](#ref-dhcp-web-interface-repo). To ni primer dokončanega izdelka. Pokaže, kako bi moral OAP začeti tvegan infrastrukturni izdelek: najprej skelet in meje zaupanja, ne pa prehiten spletni vmesnik, ki lahko mutira omrežno infrastrukturo.

Kako so koncepti pomagali:

- Človeški upravljavec je določil domenske nevarnosti, ki bi jih generični koder lahko spregledal.
- Strateški model je te nevarnosti prevedel v arhitekturo in izbiro orodij.
- Konstitucija je preprečila, da bi nevarne bližnjice postale arhitektura.
- Prvi PR-ji so ustvarili pregledljive temelje, ne pa velikega nepregledljivega implementacijskega izpisa.
- Izvajalni agent je lahko delal avtonomno, ker je bilo delo omejeno.

### Prevzem obstoječe programske opreme

Splošni koncept: OAP je uporaben, kadar ima obstoječa koda, fork, raziskovalno orodje ali akademski projekt vrednost, vendar nima profesionalne strukture. Metoda se ne bi smela začeti s prepisom vsega. Začeti bi se morala z vprašanjem, kaj je treba ohraniti, kaj je nevarno, kaj je naključna kompleksnost in kateri dokazi dokazujejo varen prehod.

Strateška UI je tu posebej uporabna, ker lahko primerja stari sistem z želenim:

- kaj je resnična produktna logika;
- kaj je prototipni skelet;
- kaj je kopirana izvorna koda od drugod;
- kaj bi moralo postati odvisnost namesto kode v lasti projekta;
- kateri testi so potrebni pred zamenjavo vedenja.

Viden primer:

- **SLAIF Connect**: javni projekt za dostop do SSH in oddaljenega računanja prek brskalnika [[47]](#ref-slaif-connect-repo). Projekt se je začel okoli forka/prototipa dobro znanega SSH sklada za brskalnik, vendar ga je analiza OAP potisnila proti čistejši arhitekturi: ne-fork razširitev, pripet upstream `libapps` kot build-time odvisnost, WebSocket-to-TCP relay, host politika na strani razširitve in pravilo, da SLAIF storitev ne sme prejemati SSH poverilnic.

Kako so koncepti pomagali:

- Človeški domenski upravljavec je podal pravi invariant: SLAIF lahko orkestrira HPC delo, ne sme pa postati nosilec SSH poverilnic.
- Strateška plast je ločila uporabno prototipno znanje od napačnega dolgoročnega lastništva.
- Izvedbeni načrt se je izognil nenadzorovanemu forku tako, da je upstream kodo spremenil v pripeto odvisnost, SLAIF vedenje pa v projektno lastno razširitev, relay, politiko in teste.

### Prepis napačno zastavljene ali spodletele programske opreme

Splošni koncept: včasih stari sistem ni samo nedokončan; v sebi nosi napačno obliko. V takem primeru OAP ne bi smel prositi agenta, naj ga neskončno krpa. Zamrzniti bi moral staro implementacijo kot referenco, izluščiti domenske invariante, napisati novo konstitucijo in ponovno zgraditi sistem v majhnih PR-jih.

To se razlikuje od mimobežnega prepisa. Prepis pod OAP potrebuje:

- jasen razlog, zakaj stara arhitektura ne more nositi naslednje faze;
- seznam vedenj in domenskega znanja, ki jih je treba ohraniti;
- eksplicitne necilje za prvi novi mejnik;
- testabilne migracijske kontrolne točke;
- javno ali interno revizijsko sled, ki razlaga izbiro.

Viden primer:

- **SLAIF Connect** ponovno ilustrira ta vzorec [[47]](#ref-slaif-connect-repo). Napačno zastavljena pot je bila ohranjanje divergentnega splošnonamenskega forka Secure Shell kot samega izdelka. Pot OAP je ohranila pravi domenski cilj, medtem ko je spremenila arhitekturo: SSH na strani brskalnika ostane, poverilnice ostanejo lokalne pri uporabniku in HPC strežniku, relay posreduje šifrirane bajte, projektno specifična politika pa živi zunaj upstream izvorne kode.

Kako so koncepti pomagali:

- Človek ni prosil agenta, naj "dokonča fork". Človek je upravljal cilj in sprejel strateški arhitekturni popravek.
- Strateška UI je neurejeno vprašanje forka pretvorila v migracijski načrt.
- Izvajalec je nato novo pot lahko gradil postopoma skozi skelet, vendoring, relay teste, validacijo v brskalniku, podpisano politiko in delo za pilotsko pripravljenost.

### Utrjevanje obstoječega resnega sistema

Splošni koncept: OAP ni samo za ustvarjanje. Zelo močan je tudi za utrjevanje sistema, ki že deluje, vendar potrebuje disciplino izdaje. Na tej stopnji postane človeška managerska vloga pomembnejša, ne manj. Vprašanje se premakne z "ali ga agent lahko zgradi?" na "kateri dokazi nam dovoljujejo trditi, da je pripravljen?"

Viden primer:

- **SLAIF API Gateway** prikazuje utrjevanje, vodeno z revizijo [[37]](#ref-slaif-repo). Revizija Review 6.0 / RC1 je odkrila resnični preostali problem pri ocenah kvot/stroškov in priporočila teste invariant ter produkcijske runbooke [[45]](#ref-slaif-review6). Matriko sanacije so nato uporabili za sledenje nastalim popravkom in njihovemu dokaznemu gradivu preverjanja [[44]](#ref-slaif-remediation-matrix).

Kako so koncepti pomagali:

- Križna revizija med modeli je projekt izzvala na pravi ravni: arhitektura, obračunavanje, varnost, testi in jezik izdaje.
- Človek je revizijske ugotovitve razvrstil v sanacijo trenutnega obsega proti prihodnjemu delu.
- Strateška UI je ugotovitve pretvorila v prompta velikosti PR-ja.
- Izvajalni agent je popravil, testiral, dokumentiral in poročal.
- Jezik izdaje je ostal pošten: RC-beta za implementirani obseg, ne pa produkcijska certifikacija.

### Produkti za upravljanje infrastrukture

Splošni koncept: produkti za upravljanje infrastrukture potrebujejo dodatno previdnost, ker lahko agent hitro zgradi nadzorno ploščo, ki deluje uporabno, hkrati pa skriva nevarne kontrolne kanale. OAP bi moral prisiliti arhitekturo, da loči želeno stanje, validacijo, privilegiran lokalni apply, revizijske dnevnike in rollback, še preden avtomatizacija doseže resnično infrastrukturo.

Viden primer:

- **Managed DHCP/IPAM Edge Appliance** [[46]](#ref-dhcp-web-interface-repo) kaže ta konzervativni začetek, ne pa dokončanega izdelka. Javni README opisuje strežniško kontrolno ravnino, odhodno komunikacijo robnih naprav, podpisane artefakte želenega stanja, lokalnega privilegiranega pomočnika za apply in pravilo, da Pi ne sme izpostavljati vhodnega upravljanja ali poganjati omrežno dosegljivega daemon-a kot root.

Kako so koncepti pomagali:

- Domenski upravljavec je definiral infrastrukturno nevarnost pred implementacijo.
- Agent je bil najprej zaprošen za skelet in backend temelje, ne pa za privilegirano logiko nameščanja ali produkcijsko DHCP avtomatizacijo.
- Arhitektura je lokalnega pomočnika za apply naredila majhnega, revizabilnega in ločenega od omrežne komunikacije.
- Javni pogledi brez prijave so bili obravnavani kot očiščeni objavljeni posnetki, ne kot različice administratorskih API-jev s skritimi gumbi.

### Obstoječa akademska ali domenska programska oprema

Splošni koncept: akademska in domenska programska oprema pogosto vsebuje uporabne algoritme ali delovne tokove, vendar šibko pakiranje, teste, CI, privzete nastavitve zasebnosti, dokumentacijo, proces izdaje in uporabniško/operatersko izkušnjo. OAP lahko takšno programsko opremo profesionalizira skozi fazno delo:

- napiši ali prenovi `AGENTS.md`;
- popiši obstoječe datoteke in tveganja;
- najprej popravi privzete nastavitve zasebnosti in poverilnic;
- dodaj usmerjene teste pred širokimi refaktorji;
- dodaj CI in pakiranje;
- ohrani znanstveno ali domensko semantiko;
- pomakni se proti kontrolnim seznamom za izdajo in ponovljivim delovnim tokom.

Če je repozitorij zaseben, ga ne navajaj kot javni primer. Vzorec ostaja veljaven, vendar naj ga javni bralci razumejo kot vodilo, ne pa kot imenovano vidno študijo primera.

### Kdaj je OAP pretežek

OAP je lahko pretežek za:

- enkratne skripte;
- zavržljive prototipe;
- eksperimente brez dolgoročne vrednosti;
- osebna orodja z nizkim tveganjem;
- naloge, kjer je neposredno človeško urejanje hitrejše od definiranja procesa.

Metoda ima režijske stroške. Uporabi jo takrat, ko ti ti stroški prinesejo varnost, kontinuiteto ali obseg.

### Kdaj je OAP posebej uporaben

OAP je posebej uporaben, kadar:

- ima projekt varnostne omejitve;
- ima sistem več komponent;
- je dokumentacija pomembna;
- se delo razteza čez veliko PR-jev;
- testi lahko dokazujejo vedenje;
- domenski strokovnjak lahko presoja namen, ne more pa vsega implementirati ročno;
- domenski strokovnjak pozna problem, ne pa nujno najboljše trenutne arhitekture ali izbire orodij;
- so uporabniki in domenski strokovnjaki bližje problemu kot razpoložljivi programski inženirji;
- je pripravljenost na izdajo pomembna.

<Question
  id="oap-case-study-pattern"
  question="Kakšen ponavljajoč se vzorec uporabljajo študije primerov za uporabo OAP v resničnih sistemih?"
  options={["Začni s široko avtonomno implementacijo in arhitekturo razberi pozneje", "* Uporabi domensko vodeno strateško odkrivanje, napiši konstitucijo, nareži delo v PR-je in pregleduj prek dokazov", "Izogibaj se repozitorijem in resnico ohranjaj v izvajalnem okolju", "Zunanje revizije obravnavaj predvsem kot marketinško validacijo"]}
  attempts={2}
>
V študijah primerov je ponovljiv vzorec OAP vedno isti: najprej strateško odkrivanje, nato omejena izvedba, skozi ves čas pa pregled, podprt z dokazi.
</Question>
