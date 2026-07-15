# Del I: Uvod in motivacija

## I.1 Zakaj OAP obstaja

Kodiranje s pomočjo UI je šlo skozi več prepoznavnih stopenj. Najzgodneje široko sprejeta oblika je bilo dopolnjevanje: orodje je znotraj urejevalnika napovedovalo naslednji token, vrstico ali manjši blok. Človek je ostajal v celoti znotraj samega dejanja pisanja kode. Orodje je pospeševalo tipkanje in včasih predlagalo API-je ali idiome, vendar ni bilo lastnik naloge.

Naslednja stopnja je bilo programiranje v paru z UI. GitHub Copilot je populariziral okvir »UI-programer v paru« in generirane predloge kode vključil v vsakodnevno delo v urejevalniku [[9]](#ref-github-copilot). Nadzorovana raziskava o GitHub Copilotu je pokazala precejšnje pohitrenje pri omejeno definiranem programskem opravilu: obravnavana skupina je nalogo dokončala 55,8 odstotka hitreje kot kontrolna skupina [[10]](#ref-copilot-productivity). Ta rezultat je pomemben, pomemben pa je tudi njegov obseg: raziskoval je določeno obliko naloge, ne pa celotnega problema dostave zanesljive programske opreme.

Kodiranje prek klepeta je spremenilo vmesnik. Razvijalec je lahko namero razložil v naravnem jeziku, prosil za arhitekturne alternative, prilepil napake, zahteval teste in iteriral pogovorno. To je UI naredilo uporabno tudi zunaj samega urejevalnika. Hkrati pa je ustvarilo nov način odpovedi: koda je lahko v pogovoru delovala koherentno, medtem ko je ostala nepreizkušena, nepregledana ali nezdružljiva z dejanskim repozitorijem.

Trenutna stopnja je agentna dostava programske opreme. Kodirni agenti lahko pregledajo repozitorij, spreminjajo več datotek, poganjajo ukaze, izvajajo teste in delajo v okviru issue oziroma pull-request delovnih tokov. SWE-bench je reševanje resničnih GitHub issuejev postavil v središče tega gibanja ter s svojim javnim repozitorijem pomagal standardizirati dostop do benchmarka in ponovljivost [[11]](#ref-swebench-paper); [[12]](#ref-swebench-repo). SWE-agent je pokazal, da vmesnik med agentom in računalnikom bistveno vpliva na uspešnost agenta, ne le model, ki je za njim, njegov odprti repozitorij pa je to delo na agent-računalnik vmesniku naredil pregledljivo [[13]](#ref-sweagent-paper); [[14]](#ref-sweagent-repo). Sistemi s človekom v zanki, kot je HULA, kažejo, da v praksi in raziskavah obstaja interes za agente, ki načrtujejo, kodirajo in odpirajo pull requeste, obenem pa inženirje ohranjajo na ključnih kontrolnih točkah [[2]](#ref-hula).

OAP sodi v to poznejšo stopnjo. Njegova skrb ni zgolj kakovost dopolnjevanja. Njegova skrb je celotna dostavna zanka:

- kdo določi cilj;
- kdo cilj pretvori v varen načrt;
- kdo upravlja repozitorij;
- katere meje zadržujejo izvajalca;
- kateri dokazi potrjujejo, da je bilo delo opravljeno;
- kdo te dokaze pregleda;
- kdo odloči, ali je programska oprema pripravljena.

<Sidenote>
Ključni prehod, opisan tukaj, je premik od lokalne pomoči pri pisanju kode k upravljani dostavi. OAP se začne tam, kjer »koda deluje verjetno pravilno« preneha biti zadosten pogoj za uspeh.
</Sidenote>

Težišče se je premaknilo od »pomagaj mi tipkati kodo« k »pomagaj mi upravljati proces dostave programske opreme«. Prav zaradi tega je treba OAP opisati kot operativno disciplino, ne kot trik s prompti.

### Širjenje zanke

Vsaka generacija orodij je razširila zanko:

| Stopnja | Človeška dejavnost | Zmožnost UI | Glavno tveganje |
|---|---|---|---|
| Dopolnjevanje | Neposredno piše kodo | Predlaga lokalna nadaljevanja | Napačen ali nevaren odlomek je hitro sprejet |
| Programiranje v paru | Sočasno ureja in sprašuje | Predlaga, razlaga, refaktorira | Verjetni odgovori brez dokaza v repozitoriju |
| Kodiranje v klepetu | Opisuje naloge in napake | Generira datoteke, teste, zasnove | Drsenje konteksta med klepetom in repozitorijem |
| Kodirni agent | Delegira repozitorijsko nalogo | Ureja, poganja ukaze, testira | Avtonomija brez upravljanja |
| OAP | Orkestrira celotno dostavno zanko | Strateška kritika in izvedbeno delo | Človeško žigosanje šibkih dokazov |

OAP ni zavračanje prejšnjih stopenj. Uporablja jih. Strateški model je pogosto klepetalne narave. Izvedbeni agent lahko ponuja IDE-podobne operacije. Razlika je v tem, da je delo organizirano okoli odgovorne dostave.

## I.2 Temeljni pojmi OAP

OAP je treba najprej razumeti kot kontrolni sistem. Njegov namen ni zgolj zmanjšati količino tipkanja, medtem ko človek ostane ujet v isti nizkonivojski delovni tok. Njegov namen je ohraniti človeško pozornost pri nameri, tveganju, dokazih in izdaji, medtem ko se implementacijsko delo delegira strojem, ki se lahko gibljejo hitreje kot ljudje.

<ExpandingSideImg
  src="../assets/fig-00-oap-control-plane.svg"
  alt="Kontrolna ravnina OAP."
  caption="Kontrolna ravnina OAP."
/>

### Začnite s strateškim odkrivanjem, ne s kodo

Projekt OAP bi se moral začeti s pogovorom strateškega odkrivanja, ne z izvedbenim agentom in ne s praznim promptom nad repozitorijem. Prvo vprašanje ni »katero kodo naj agent napiše?«. Prvo vprašanje je »kakšen sistem bi sploh moral obstajati?«

To je posebej pomembno, kadar je človek domenski strokovnjak in ne poklicni arhitekt programske opreme. Človek lahko operativno potrebo pozna zelo natančno: institucija mora izdajati omejene LLM API ključe, laboratorij mora upravljati delovne tokove, učitelj mora ocenjevati izpite, HPC storitev mora zaganjati opravila, ne da bi prejemala SSH poverilnice, ali pa mora naprava na Raspberry Pi varno uveljaviti DHCP konfiguracijo. To še ne pomeni, da človek pozna pravi sklad, mejo zaupanja, podatkovni model, sistem ozadnih opravil, model brskalniške razširitve ali obliko namestitve.

Strateški model človeku pomaga postavljati in odgovarjati na vprašanja:

- Katera je resnična kategorija produkta?
- Katera obstoječa orodja ali arhitekture rešujejo sorodne probleme?
- Kateri sklad je za to domeno dovolj dolgočasen in varen?
- Katere komponente morajo biti ločene, ker se njihove meje zaupanja razlikujejo?
- Katere dele je treba odložiti, ker so za prvi rez preveč tvegani?
- Česa izvedbenemu agentu ne smemo nikoli dovoliti improvizirati?

To je managersko dejanje. Strateški model predlaga arhitekture in razlaga kompromise. Človek jih sprejme, zavrne ali preusmeri na podlagi domenskega znanja. Šele po tem odkrivanju OAP izdela konstitucijo in prvi izvedbeni prompt.

### Človek je lastnik cilja, ne terminala

Najpomembnejša naloga človeka je, da projekt ohranja usmerjen v pravi problem. OAP zato človeka premakne višje po organizacijski lestvici. Človek ni več predvsem pisec kode in pogosto niti ne aktivni programski inženir v vsakodnevnem smislu implementacije. Deluje bolj kot lastnik produkta, inženirski vodja, tehnični direktor ali odgovorni pregledovalec dokazov.

To ni zgolj sprememba orodij. To je sprememba vloge. Človek upravlja namero, tveganja, prioritete in sprejemljivost. Ta upravljavska vloga mora biti disciplinirana, ne ceremonialna: človek določi cilje, kriterije sprejema, kriterije izdaje, necilje, proračun tveganja in standarde dokazovanja. To pa mora početi s krajšimi besedili, tesnejšimi povzetki in manj nizkonivojskimi artefakti za pregled. Strateška UI upravlja prevod, spomin, kompresijo in tehnično sintezo. Izvedbeni agent upravlja proizvodnjo kode znotraj omejenega okolja izvajanja.

Človek sprašuje:

- Kaj pravzaprav gradimo?
- Kaj se nikakor ne sme pokvariti?
- Kaj smo dejansko implementirali?
- Kje je dokaz?
- Katera tveganja ostajajo?
- Kaj naj se zgodi naslednje?

Ta vprašanja naj človek praviloma zastavlja strateški UI, ne neposredno izvedbenemu agentu. Neposredni nadzor nad agentom je drag, ker človeka vleče nazaj v delo ukaz za ukazom. Če agent pove, da potrebuje paket, prevajalnik, gonilnik za brskalnik, podatkovno bazo za testni fixture ali lokalno storitev, želeni odgovor OAP ni »naj to namesti človek«. Želeni odgovor je »agent to namesti ali konfigurira v utrjenem izvajalnem prostoru in poroča, kaj se je spremenilo«.

Strateška UI bi morala najprej odgovoriti v stisnjeni obliki: zaključek, dokaz, tveganje in naslednja odločitev. Človek lahko nato poglobljeno odpre datoteke, loge, teste ali vrstice v PR-ju samo takrat, ko je povzetek šibek, tveganje visoko ali odgovor ne deluje smiselno.

### Človek je lahko domenski strokovnjak

Človek v OAP ni nujno poklicni programski inženir. V mnogih primerih je najboljši človeški vodja prav domenski strokovnjak: zdravnik, učitelj, znanstvenik, operater infrastrukture, strokovnjak za skladnost, proizvodni inženir, raziskovalec, knjižničar ali lastnik procesa v javnem sektorju, ki problem razume bolje kot katerakoli programska ekipa.

To je sorodno end-user software engineeringu in citizen developmentu, vendar nima iste oblike. Tradicionalni end-user development pogosto od domenskega strokovnjaka zahteva, da sam postane graditelj z uporabo preglednic, skript, low-code orodij ali UI-podprtih promptov. OAP gre drugače: domenski strokovnjak postane upravljavec agentnega dostavnega sistema. Strateška UI prevaja domensko namero v tehnične delovne naloge. Izvedbeni agent gradi. Domenski strokovnjak presoja, ali nastali sistem služi dejanski potrebi domene.

To je pomembno, ker programska oprema pogosto odpove v prevodu. Zahteve prehajajo od uporabnikov do analitikov, od analitikov do ticketov, od ticketov do inženirjev, od inženirjev nazaj do pregledovalcev in končno spet do uporabnikov. Pri vsakem prenosu se lahko izgubi domenski pomen. OAP lahko to zanko skrajša. Oseba, ki je domeni najbližja, lahko strateško UI vpraša:

- Ali smo implementirali delovni tok, ki ga uporabniki res potrebujejo?
- Ali to ustreza dejanski operativni omejitvi?
- Katero domensko predpostavko je agent naredil sam?
- Kateri kriterij sprejema dokazuje domensko vedenje?
- Kaj bi to v praksi naredilo nevarno ali neuporabno?

Domenskemu strokovnjaku ni treba pregledati vsakega razreda ali funkcije. Potrebuje discipliniran nadzor nad cilji, kriteriji sprejema, kriteriji izdaje in dokazi.

### Strateška UI pretvarja domensko namero v arhitekturo

Eden najpomembnejših trenutkov OAP se zgodi še preden se izvedbeni agent dotakne repozitorija. Domenski strokovnjak strateškemu modelu postavlja vprašanja, kot so:

- Kakšen sistem pravzaprav potrebujem?
- Katera arhitektura ustreza temu operativnemu problemu?
- Katera orodja, ogrodja, podatkovne baze, izvajalna okolja in protokoli so primerni?
- Katere dele je treba izolirati, ker so dovolj tvegani?
- Kaj je treba zgraditi najprej in kaj mora izrecno počakati?
- Kaj bi profesionalna programska ekipa tukaj prepoznala kot tveganje?

Tu so sodobni visoko-razmišljajoči modeli posebej koristni domenskim strokovnjakom, ki niso specialisti za programsko opremo. Domenski strokovnjak lahko razume pravi delovni tok, stroške napak, omejitve politike in boleče točke uporabnikov, morda pa ne pozna trenutne krajine arhitektur programske opreme. Strateški model lahko deluje kot prevajalec arhitekture in izvidnik tehnologij: domenski problem preslika v verjetne programske oblike, razloži kompromise, identificira standardne komponente in predlaga implementacijsko zaporedje, ki mu lahko izvedbeni agent pozneje sledi.

To še ne pomeni, da je model uradni arhitekt. Lahko se moti, je zastarel ali preveč samozavesten. Človek je še vedno lastnik cilja in mora odgovor izzvati. Toda brez tega začetnega strateškega pogovora OAP oslabi: izvedbeni agent lahko začne graditi iz plitvega prompta namesto iz domensko informirane arhitekture.

### Strateška UI je kontrolna ravnina

Strateška UI je glavni človeški vmesnik do projekta. Človeško namero prevaja v arhitekturo, izbiro orodij, delovne naloge, vprašanja za pregled in dokaze za izdajo. Interpretira poročila agentov, primerja dokaze s cilji in pripravi naslednjo ozko nalogo. Morala bi biti močan, dolgokontekstni model, ker ni namenjena temu, da bi trošila kontekst na tisoče urejanj datotek. Njen kontekst se porablja počasi: človeška razprava, stanje projekta, povzetki PR-jev, arhitekturne odločitve, registri tveganj in vprašanja o dokazih.

V idealnem delovnem toku OAP strateški model projekta skoraj nikoli ne pozabi. Ta ideal ni povsem realističen, vendar je to smer razvoja. Delovni tok bi moral strateški kontekst ohranjati čim dlje, ga po potrebi osveževati s predajami in ga ne zapravljati za mehansko implementacijo.

### Izvedbeni agent je zamenljivo izvedbeno delo

Izvedbeni agent je dragocen zato, ker lahko repozitorij upravlja s strojno hitrostjo. Bere datoteke, spreminja kodo, namešča odvisnosti, zaganja teste, zaganja storitve, piše dokumentacijo, ustvarja commite in odpira PR-je. Ne potrebuje tega, da bi v kontekstu večno nosil celoten projekt. Potrebuje dovolj konteksta, da dokonča eno razrezano nalogo in vrne dokaze.

To ustvari koristno asimetrijo:

- strateška UI naj bo najmočnejši praktično razpoložljivi model z dolgim kontekstom in visoko kakovostjo sklepanja;
- izvedbeni agent je lahko cenejši, hitrejši ali oboje;
- kontekst izvedbenega agenta naj traja eno nalogo v velikosti posameznega PR-ja;
- po PR-ju se lahko izvedbeni kontekst kompaktira, ponastavi ali zavrže;
- trajna resnica mora živeti v oddaljenem repozitoriju, razpravi v PR-ju, CI logih, dokumentaciji in povzetkih predaj.

### Visoke pravice sodijo v utrjeno in obnovljivo virtualko

Pretirano omejevanje agenta, tako da ne more nameščati orodij, ponovno graditi knjižnic, poganjati migracij, zagnati lokalnih storitev ali popravljati lastnega testnega okolja, pogosto zgolj zapravlja človeški čas. Sodobni kodirni agenti so dovolj hitri, da lahko ena manjkajoča odvisnost pomeni ure človeškega dela: lovljenje različic paketov, ponovna gradnja nativnih orodij, postavljanje podatkovnih baz ali posredovanje izpisa terminala. Na tej točki OAP degenerira v nasprotje svojega namena: UI pilotira človeka.

Prednostni vzorec je utrjen izvajalni prostor, nad katerim ima agent širok nadzor, projekt pa si lahko privošči njegovo izgubo. Virtualka ne sme vsebovati produkcijskih skrivnosti, nenadomestljivega stanja ali necommitane projektne resnice. Če jo agent pokvari, jo je mogoče ponovno zgraditi iz oddaljenega repozitorija in dokumentiranih ukazov za postavitev. To naredi visoke privilegije varnejše kot krhko zaklenjeno okolje, ki človeka nenehno rekrutira za rutinska opravila.

### Oddaljeni repozitorij je projektna resnica

OAP je odvisen od ostre ločnice med zamenljivim stanjem izvajalnega okolja in trajno projektno resnico. Izvedbena virtualka je začasna. Oddaljeni repozitorij, veja, PR, CI log, testi, dokumentacija, sled issuejev in release notes so trajni. Lokalno virtualko je mogoče uničiti. Slabo vejo je mogoče zapustiti. Neuspel PR je mogoče zapreti. Toda projektna resnica mora ostati vidna, verzionirana, pregledljiva in rekonstruabilna.

Prav to načelo naredi visoko-avtonomno izvedbo sprejemljivo. Agent je lahko v škatli zelo močan, ker škatla ni vir resnice.

### Pregled postane zasliševanje dokazov

OAP ne zahteva, da človek kot privzeti potek dela ročno prebere vsako vrstico vsakega PR-ja. To je lahko enako potraten pristop kot ročno nameščanje odvisnosti. Namesto tega človek zaslišuje strateški model:

- Ali smo zahtevo implementirali natančno?
- Katere datoteke so se spremenile in zakaj?
- Kateri testi dokazujejo kritično vedenje?
- Katero negativno pot smo testirali?
- Ali se je agent dotaknil skrivnosti ali produkcijskih podatkov?
- Ali dokumentacija pretirano trdi pripravljenost?
- Kaj bi ta PR naredilo nevarnega za merge?

Ročni pregled kode ostaja na voljo za visokorizična področja, nejasna poročila, varnostno občutljive spremembe ali sumljive diffe. Toda privzeta človeška drža ni delo vrstico za vrstico. Privzeta drža je adversarialno spraševanje strateške UI po njenem zemljevidu dokazov.

### Delo je razrezano tako, da se kontekst ne sesuje

Delegiranje v velikosti PR-ja ni le Git navada. Je mehanizem upravljanja konteksta. Razrezana naloga ohrani kontekst izvedbenega agenta dovolj kratek, da ga zanesljivo dokonča. Ohrani kontekst strateške UI dovolj čist, da si zapomni cilj. In človeško pozornost ohrani pri odločitvah namesto pri šumu implementacije.

Ciljno stanje je preprosto: strateška UI ne izgubi konteksta, človek ne izgubi cilja, izvedbenemu agentu pa ni treba ohranjati v spominu ničesar zunaj trenutne naloge.

### Projektna konstitucija je strojno berljivo upravljanje

Projektna konstitucija, navadno `AGENTS.md` ali ekvivalentna datoteka z navodili, pretvori ponavljajoče se človeške popravke v trajno operativno pravo. Agentom pove, kako naj se vedejo, kadar človek ne gleda neposredno. Določa arhitekturo, teste, varnostna pravila, prepovedana dejanja, zahteve glede poročanja in definicijo dokončanosti.

Brez konstitucije OAP razpade v zaporedje domiselnih promptov. S konstitucijo vsak prompt podeduje projektno pravo.

### Validacijski dolg je glavni dolg

UI-kodiranje poceni kodo. Ne poceni pa pravilnosti. Čim hitreje agenti generirajo implementacijo, tem bolj se ozko grlo premika k dokazovanju: testom, CI, arhitekturnim pregledom, varnostnemu pregledu, točnosti dokumentacije in poštenosti izdaje. OAP zato ni predvsem produktivnostni trik. Je metoda upravljanja validacije.

Strateška UI bi morala pomagati nositi to validacijsko breme. Človek ne bi smel sprejeti »končano« kot občutka. Dokaz mora zahtevati skozi strateško kontrolno ravnino.

### Proti-pilotno pravilo

Najbolj strnjeno pravilo OAP je naslednje:

> Človek pilotira strateško UI; strateška UI usmerja izvedbenega agenta; izvedbeni agent upravlja stroj. Če začne izvedbeni agent človeka voditi skozi nizkonivojsko delo, je kontrolna zanka obrnjena in jo je treba preoblikovati.

## I.3 Kaj OAP je

Orchestrated Agentic Programming je delovni tok, v katerem človeški vodja usklajuje najmanj tri plasti:

1. **Človeška namera in presoja.** Človek določi cilj produkta, omejitve, toleranco do tveganja in odločitev o izdaji.
2. **Strateška UI.** Model z močnim sklepanjem in dolgim kontekstom deluje kot arhitekt, načrtovalec, pregledovalec, kritik, spominska plast in prevajalnik promptov.
3. **Izvedbeni agent.** Kodirni agent deluje znotraj omejenega in obnovljivega izvajalnega okolja, ureja repozitorij, namešča orodja, poganja teste, ustvarja commite in odpira pull requeste.

<ExpandingSideImg
  src="../assets/fig-01-oap-loop.svg"
  alt="Operativna zanka OAP."
  caption="Operativna zanka OAP."
/>

Odločilna oblikovalska izbira je, da strateški model in izvedbeni agent nista zlepljena v eno nenadzorovano zanko in da človek ni povlečen v varuško agentu. Človek praviloma komunicira s strateško UI. Strateška UI pretvarja človeško namero v delovne naloge, bere poročila izvedbe, preslika trditve v dokaze in razlaga tveganja. Izvedbeni agent opravlja delo in vrača dokaze. Človek sprejema, zavrača, preusmerja ali izda na podlagi strateškega zasliševanja, ne na podlagi zaupanja v samozavest izvajalca.

### Delovna definicija

**Orchestrated Agentic Programming je človekovo upravljanje, na konstituciji temelječ podtip agentnega programskega inženirstva, v katerem dolgokontekstna strateška UI služi kot kontrolna ravnina, visoko-avtonomen kodirni agent izvaja delo v utrjenem in obnovljivem izvajalnem okolju, človek pa ohranja cilj, tveganje, zahteve po dokazih in avtoriteto za izdajo.**

Ta definicija je namenoma stroga. En sam pogovor s klepetalnim botom ni OAP. Kodirni agent, ki pripravi popravek, še ni dovolj. Večagentni roj brez človeških vrat ni OAP. Tudi človek, ki ročno opravlja nastavitvena opravila za agenta, še ne pomeni zrelega OAP. Metoda zahteva ločitev vlog, trajna pravila, omejeno avtonomijo, obnovljivo izvedbo, dokaze, strateški spomin in človeško odgovornost.

### Zakaj »orkestrirano«

Beseda »orkestrirano« je uporabna zato, ker človek ne zgolj prompta. Človek razporeja vloge, čas, omejitve, povratne zanke, dokaze in ekonomiko konteksta. Programske orkestracije ne določa tipkanje vsake vrstice, nameščanje vsake odvisnosti ali privzeto branje vsake generirane vrstice. Orkestrator je odgovoren za sistem, ki nastane, in za vprašanja, s katerimi strateški model prisili, da dokaže skladnost sistema.

Ta razlika je pomembna. V UI-kodiranju z nizko disciplino človek pogosto le še naroča popravke, dokler demo približno ne deluje. V obrnjenih agentnih delovnih tokovih agent človeka nenehno prosi, naj zaganja ukaze, namešča pakete, lepi loge ali odloča o nizkonivojskih popravilih. V OAP človek določi meje naloge, prepovedane bližnjice in dokazne zahteve; strateški model to prevede v izvedbo; izvajalno okolje pa je dovolj močno, da lahko agent nizkonivojsko delo opravi sam.

### Zakaj »agentno«

Metoda predpostavlja, da izvajalec zna delovati. Bere datoteke, spreminja kodo, zaganja ukaze, opazuje napake in se prilagaja. To je drugačen razred dejavnosti kot generiranje odseka kode v klepetu. Uradna dokumentacija za Codex na primer ločuje med plastmi sandboxa in odobritev, ki določajo, kaj agent tehnično lahko stori in kdaj mora pred dejanjem vprašati [[15]](#ref-codex-security).

OAP je mogoče izvajati s previdnimi nastavitvami odobritev ali v visoko-avtonomnih režimih, kadar je izvajalno okolje namenoma omejeno. Močnejša trditev ni »vedno uporabljaj polno avtonomijo«. Močnejša trditev je »če podeliš avtonomijo, varnost prestavi v mejo izvajalnega okolja, projektno konstitucijo, disciplino PR-jev in strateško zanko dokazov«. Agent z visokimi privilegiji znotraj zamenljive virtualke je lahko varnejši in produktivnejši od šibko opolnomočenega agenta, ki človeka nenehno novači za operativna opravila.

### Zakaj »programiranje«

Programiranje ne izgine. Samo premakne se. Sistem je še vedno sestavljen iz kode, testov, migracij, konfiguracije, dokumentacije in skript za namestitev. Razlika je v tem, da človeku ni več treba biti glavni tipkar ali terminalski pomočnik agenta. Človek programira proces: namero, arhitekturo, omejitve, delovne naloge, zahteve po dokazih in odločitve.

### Kaj OAP ni

OAP ni vibe coding. Vibe coding je uporaben izraz za neformalno ustvarjanje programske opreme, vodeno z naravnim jezikom, kjer razvijalec lahko rezultate sprejema na občutek. OAP se premika v nasprotno smer: več eksplicitnih omejitev, manjši delovni kosi, več testov, močnejši pregledi in bolj pošten jezik o pripravljenosti.

OAP ni običajno programiranje v paru z UI. Programiranje v paru človeka ohranja znotraj implementacijske zanke. OAP lahko človeka odstrani iz večine tipkanja in izvajanja ukazov, obenem pa poveča njegovo vlogo pri strategiji in validaciji.

OAP ni popolnoma avtonomno programsko inženirstvo. Marketing okoli »UI-programskih inženirjev« pogosto poudarja neodvisno izvajanje. OAP poudarja upravljano izvajanje. Agent ima lahko visoko avtonomijo znotraj stroja, vendar ni lastnik pomena produkta niti avtoriteta za izdajo.

## I.4 Premik človeške vloge

Najbolj neprijetno vprašanje v OAP je: če človek ne napiše večine kode in ne nadzira ročno vsakega koraka agenta, kaj torej pravzaprav počne?

Odgovor je, da se človek premakne od implementacijskega dela k upravljavski odgovornosti. To ni degradacija. Gre za bolj abstraktno in pogosto težjo vlogo. V zrelem OAP človek ni več predvsem koder. Lahko je lastnik produkta, inženirski vodja, tehnični vodja, vodja izdaje, domenski strokovnjak ali odgovorni odločevalec. V številnih projektih OAP je domensko znanje pomembnejše od samega znanja kodiranja, ker izvedbeni agent zna proizvajati kodo, medtem ko samo domenski strokovnjak lahko presodi, ali je produkt uporaben, varen in zvest resničnemu delovnemu toku. Takšna vloga lahko in mora izvajati močno disciplino: jasne cilje, eksplicitne kriterije izdaje, pragove sprejemljivosti, necilje, držo do tveganja in zahteve po dokazih. Človek mora razumeti dovolj domene, arhitekture, varnosti, testov in nameščanja, da lahko zaslišuje, ali sistem še vedno ostaja smiseln. To počne predvsem skozi strateško UI, ne tako, da postane počasna ročna ovojnica okoli izvedbenega agenta.

<ExpandingSideImg
  src="../assets/fig-02-role-separation.svg"
  alt="Ločitev vlog v OAP."
  caption="Ločitev vlog v OAP."
/>

### Človeški vodja

Človeški vodja je lastnik:

- definicije problema;
- namena produkta;
- domenske resnice;
- potreb uporabnikov;
- etičnih in pravnih meja;
- apetita po tveganju;
- prioritet;
- kriterijev sprejema;
- odločitev o izdaji;
- odgovornosti, kadar je rezultat napačen.

Tega ni mogoče delegirati modelu. Model lahko pri tem pomaga. Lahko artikulira stvari, izziva nekonsistentnosti, pripravlja kontrolne sezname in primerja alternative. Toda odgovornost ostane pri človeku ali organizaciji, ki metodo uporablja.

Človeški vodja tudi odloča, kdaj strateški odgovor ni dovolj dober. To je ključno. Izvedbeni agent lahko pripravi čist diff, prehajajoče teste in prepričljivo poročilo, pa še vedno rešuje napačen problem. Strateški model lahko to poročilo tekoče povzame in še vedno spregleda domensko tveganje. Samo človeški vodja lahko odloči, ali rezultat služi predvidenemu namenu.

Človeški vodja bi moral strateški UI postavljati neprijetna vprašanja:

- Ali smo implementirali natančno zahtevo ali zgolj nekaj podobnega?
- Ali to ustreza delovnemu toku, ki ga uporabniki dejansko uporabljajo?
- Kateri test bi padel, če bi kritično vedenje regresiralo?
- Ali se je agent dotaknil skrivnosti, migracij, poverilnic ali namestitvenih datotek?
- Katere datoteke so se spremenile iz razlogov, ki niso neposredno vezani na delovni nalog?
- Katere dokaze bi pokazali skeptičnemu zunanjemu pregledovalcu?
- Česa ne bi nikoli dovolili mergati?

Takšna vprašanja imajo večji vzvod kot spraševanje izvedbenega agenta, naj med delom razloži vsak ukaz.

### Strateška UI

Strateška UI se ne uporablja predvsem kot generator kode. Je kontrolna ravnina in spominska plast. Njena dela vključujejo:

- pomoč domenskemu strokovnjaku pri odkrivanju prave oblike programske rešitve;
- primerjanje arhitekturnih in tehnoloških možnosti;
- pretvarjanje široke namere v arhitekturo;
- identificiranje manjkajočih zahtev;
- predlaganje varnega implementacijskega zaporedja;
- pisanje delovnih nalogov za izvedbenega agenta;
- pregledovanje poročil izvedbe;
- opazovanje drsenja dokumentacije;
- prepoznavanje varnostnih in testnih vrzeli;
- pripravo gradiva za predaje;
- ocenjevanje pripravljenosti za izdajo.

Strateški UI bi bilo treba dovoliti razmišljati, kritizirati in se ne strinjati. Ne smemo je zreducirati na lepotilca promptov. V OAP je strateški model najbližje kombinaciji staff inženirja, arhitekta, tehničnega programskega vodje in pregledovalca. Še vedno pa ni odgovoren subjekt. Je svetovalna in sintezna plast.

Ker nosi kontinuiteto projekta, bi moral biti strateški model najmočnejši praktično dostopni model: visoka kakovost sklepanja, dolg kontekst, dobro sledenje navodilom in močna sposobnost primerjave trditev z dokazi. Tukaj se splača porabiti drago kapaciteto modela. Strateški model ne troši konteksta za ponavljajoča se urejanja datotek ali lokalne poskuse; ohranja zgodbo projekta, domenske predpostavke in človekov cilj.

### Izvedbeni agent

Izvedbeni agent je implementacijska delovna sila. Ne sme odločati o produktu. Ne sme tiho širiti obsega. Ne sme mergati lastnih pull requestov. Prav tako ne bi smel rutinsko prositi človeka, naj v njegovem imenu nastavlja okolje. Njegova naloga je izvesti omejen delovni nalog:

- pregledati relevantne datoteke;
- namestiti ali konfigurirati zahtevana lokalna orodja znotraj izvedbene virtualke;
- narediti omejeno spremembo;
- zagnati zahtevane teste;
- posodobiti dokumentacijo, kadar je to zahtevano;
- commitati samo povezane datoteke;
- odpreti pull request;
- natančno poročati, kaj se je zgodilo.

Izvedbeni agent je dragocen zato, ker lahko dolgočasno delo opravlja s strojno hitrostjo. Z enako hitrostjo pa lahko opravlja tudi napačno delo. Zato OAP združuje visoko avtonomijo z ozkim obsegom in zahtevami po dokazih. Kontekst izvajalca mora trajati samo eno nalogo v velikosti posameznega PR-ja. Po tej nalogi ga je mogoče kompaktirati, ponastaviti ali zamenjati.

### Novi človeški nabor veščin

OAP povečuje vrednost:

- razmišljanja o zahtevah;
- arhitekturne presoje;
- varnostnega razmišljanja;
- zasnove testov;
- zasliševanja dokazov;
- razhroščevanja iz poročil;
- upravljanja izdaj;
- discipline dokumentacije;
- oblikovanja promptov in delovnih nalogov;
- sposobnosti vedeti, kdaj ne delegirati.

Zmanjšuje relativni pomen pomnjenja vsakega idiomatičnega vzorca v ogrodju na pamet in vrednost ročnega izvajanja rutinskih nastavitev. Ne odpravlja pa potrebe po razumevanju programske opreme.

### Kaj se zgodi z implementatorji

Trditev, da se človek premakne višje po lestvici, je najjasnejša za osebo, ki upravlja zanko OAP. Za ljudi, katerih prejšnje delo je bilo linijska implementacija, je manj samodejna. Posvojitev OAP se ne sme pretvarjati, da implementacijsko delo ostaja nespremenjeno. Del tega dela se zgosti. Del se avtomatizira. Del pa postane vrednejši, ker sistem zdaj potrebuje močnejšo validacijo, pregled, operacije in domenski prevod.

Pri zdravi posvojitvi se implementatorji premikajo k vlogam z večjim vzvodom:

- prevajanje domenske namere v natančne kriterije sprejema;
- zasnova testov in fixtur, ki dokazujejo vedenje;
- pregled arhitekture, varnosti, zasebnosti in operativnega tveganja;
- vzdrževanje agentskega izvajalnega okolja, projektne konstitucije in CI vrat;
- pretvarjanje revizijskih ugotovitev v omejene delovne naloge;
- pregledovanje visokorizičnih diffov namesto branja vsake generirane vrstice;
- lastništvo release engineeringa in incidentnih runbookov.

Pri nezdravi posvojitvi so implementatorji preprosto odstranjeni iz zanke, preostali človek pa zgolj žigosa izhod agenta. To ni zrel OAP. Metoda deluje samo, če se delo, ki je bilo prej porabljeno za tipkanje in rutinsko nastavitev, reinvestira v presojo, dokaze, domensko pravilnost, varnost in poštenost izdaje.

### Skušnjava gumijastega žiga

Glavni človeški način odpovedi je gumijasto žigosanje. Agent vrne samozavestno poročilo. Testi so zeleni. PR obstaja. Strateški model ga tekoče povzame. Človek si želi napredka. Skušnjava je, da to sprejme.

OAP mora uriti nasprotni refleks: vsako poročilo obravnavaj kot trditev, ne kot dokaz. Prosi strateški model, naj pokaže na dokaze. Vprašaj, ali testi pokrivajo tveganje. Vprašaj, ali dokumentacija preveč obljublja. Vprašaj, ali je sprememba sistem konceptualno očistila ali ga zgolj naredila bolj navidezno popolnega. Preglej diff neposredno, kadar so dokazi šibki, tveganje visoko ali strateški odgovor ne zdrži zasliševanja.

<Question
  id="oap-intro-control-loop"
  question="V OAP, kakšna je v zrelem delovnem toku priporočena vloga človeka?"
  options={["Da ročno nadzoruje vsako namestitev odvisnosti in vsak ukaz", "Da izvedbenemu agentu prepusti odločitev o pripravljenosti za izdajo", "* Da je lastnik namere, tveganja, zahtev po dokazih in odločitev o izdaji, medtem ko delegira implementacijsko delo", "Da nadomesti strateški model kot glavni spomin arhitekture"]}
  attempts={2}
>
Osrednji premik vloge v OAP gre navzgor: človek preneha biti terminalski pomočnik agenta in namesto tega upravlja cilje, dokaze in avtoriteto za izdajo.
</Question>
