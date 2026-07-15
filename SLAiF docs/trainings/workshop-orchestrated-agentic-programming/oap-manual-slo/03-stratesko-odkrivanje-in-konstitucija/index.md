# Del III: Strateško odkrivanje in konstitucija

## III.1 Prvi pogovor s strateškim modelom

Strateška plast je mesto, kjer se OAP najbolj razlikuje od običajne rabe kodirnih agentov. Mnogi delovni tokovi delegirajo nalogo neposredno kodirnemu agentu. OAP vstavi plast razmisleka pred izvedbo in po njej ter to plast razmisleka naredi za glavni človeški vmesnik do projekta.

Človek praviloma ne bi smel neposredno upravljati izvajalnega agenta. Neposredno upravljanje je mamljivo, ker daje občutek natančnosti: prilepi to napako, poženi tisti ukaz, poglej tisto datoteko. Toda to porablja omejeno človeško pozornost na napačni ravni. To je še posebej pomembno, kadar je človek domenski strokovnjak in ne profesionalni razvijalec. Strateška UI bi morala absorbirati poročila izvajalca, pregledovati dokaze iz repozitorija, prevajati tehnične trditve v domensko relevantne pojme in odgovarjati na človekova vprašanja na visoki ravni.

Pred prvo sejo s strateškim modelom prenesite [strategic_model_init_material.md](../../strategic_model_init_material.md), odprite nov chat in izberite dovolj zmogljiv model. Dobre izbire so GPT-5.5 Thinking z nastavitvijo thinking effort na Extended, GPT-5.5 Pro, Claude Opus 4.8 ali Claude Sonnet 4.6. Če uporabljate Claude, nastavite effort na High ali Max in vključite Thinking. Nato datoteko naložite v pogovor in začnite z navodilom: "Preberi si priloženi tekst, ki opisuje koncept OAP, in povej, ali lahko igraš vlogo strateškega modela." V OAP naj bo to prvi pripravljalni korak za strateški model.

<Sidenote>
To je poglavje, v katerem OAP najjasneje odstopi od običajne rabe kodirnih agentov: strateški model ni pomočnik, pripet na izvedbo, ampak primarni vmesnik, prek katerega človek upravlja projekt.
</Sidenote>

<ExpandingSideImg
  src="../assets/fig-08-strategic-discovery.svg"
  alt="Strateško odkrivanje pretvarja domenski namen v izvršljivo projektno pravo."
  caption="Strateško odkrivanje pretvarja domenski namen v izvršljivo projektno pravo."
/>

### Pogovor odkrivanja

Strateško odkrivanje se začne z domenskim problemom človeka, ne pa s tehnološkim skladom. Človek najmočnejši razpoložljivi strateški model vpraša, kakšen programski sistem je sploh potreben, katera orodja so primerna, katera profesionalna pravila naj vodijo delo in česa izvajalni agent ne sme improvizirati.

Pogovor mora biti dovolj ekspliciten, da je iz njega pozneje mogoče sestaviti `AGENTS.md`. Uporabno zaporedje je:

1. Opiši domenski problem v operativnem jeziku.
2. Vprašaj, za kakšen sistem v resnici gre.
3. Vprašaj, katera arhitektura in katere meje zaupanja so primerne.
4. Vprašaj, kateri sklad je dolgočasen, robusten in primeren.
5. Vprašaj, kakšen podatkovni model, ozadna opravila, admin tokovi in testi bi jih pričakovala profesionalna ekipa.
6. Vprašaj, kaj naj bo izločeno iz prve izdaje.
7. Prosi model, naj te odločitve pretvori v `AGENTS.md`, oblikovalske dokumente in prve delovne naloge.

Človeku odgovora ni treba poznati vnaprej. Domeno pa mora poznati dovolj dobro, da zna napačen odgovor zavrniti.

### Primer odkrivanja za API Gateway

Delo na SLAIF API Gatewayu jasno pokaže ta vzorec. Začetni človeški problem ni bil "napiši FastAPI aplikacijo". Bil je problem usposabljanja in upravljanja: za delavnice SLAIF/WP6 so udeleženci potrebovali dostop do LLM API-ja z omejenimi stroški, revizijsko sledjo uporabe in brez razkritja pravih ključev ponudnikov.

Strateški model je najprej razjasnil omejitev na strani ponudnikov: običajni API ključi ponudnikov in projektni proračuni niso zadostovali za stroge trde kvote po posameznem ključu. To je premaknilo kategorijo izdelka. Sistem ni bil več "nabor ključev" ali "skripta za uporabnike". Postal je nadzorovan OpenAI-združljiv prehod: uporabniki dobijo ključe, ki jih izda gateway, uporabljajo običajne OpenAI SDK konvencije, zaledni sistem pa avtenticira, preverja kvote, usmerja k ponudnikom, zamenja poverilnice ponudnikov s strežniškimi, beleži uporabo in se zapre v varno stanje, kadar politika ali cene niso znane. Javni repozitorij zdaj odraža prav takšno obliko izdelka [[37]](#ref-slaif-repo).

Veriga odkrivanja je bila videti takole:

| Domensko vprašanje | Strateški prevod | Posledična projektna odločitev |
| --- | --- | --- |
| Ali imajo lahko uporabniki stroge omejitve porabe OpenAI po posameznem ključu? | Izvorni nadzor ponudnikov ne zadostuje za stroge delavniške omejitve po uporabniku. | Zgradi lokalni gateway, ki uveljavlja kvote. |
| Ali lahko uporabniki obdržijo običajne OpenAI primere? | Združljivost je pomembnejša od prilagojenega poimenovanja. | Uporabi `OPENAI_API_KEY` in `OPENAI_BASE_URL`; izpostavi `/v1`. |
| Kako naj bodo shranjeni ključi? | Ključe gatewaya obravnavaj kot bearer tokene in nikoli ne shranjuj čistega besedila. | Shranjuj HMAC-izpeljane hashe tokenov s strežniškim pepperjem. |
| Kako lahko stroga kvota preživi sočasnost? | Ocenjuj pred posredovanjem in zaključi po vrnitvi podatkov o uporabi od ponudnika. | Implementiraj rezerva-nato-zaključi obračunavanje in kvote. |
| Kateri zaledni sklad ustreza? | Async HTTP posredovanje, streaming, transakcije baze in admin delovni tokovi so osrednji. | FastAPI/Starlette, `httpx`, PostgreSQL, Redis/Celery, SQLAlchemy/Alembic. |
| Kako naj administratorji upravljajo delavnice? | Sistem potrebuje tako spletne kot terminalske operacije. | Strežniško renderirana admin nadzorna plošča in Typer CLI. |
| Kako naj bo usmerjen izvajalec? | Arhitektura in invarianti morajo postati repozitorijsko pravo pred široko implementacijo. | Napiši `AGENTS.md`, shematsko dokumentacijo, matriko združljivosti, teste in PR delovni tok. |

Pomembna točka je, da model ni le odgovarjal na vprašanja o sintaksi. Domenskemu strokovnjaku je pomagal odkriti kategorijo izdelka, nato arhitekturo in nato še implementacijsko konstitucijo.

### Primeri človeških promptov

V pogovorih o API Gatewayu so bili človeški prompti kratki, vendar upravljavski. Zastavljali so vprašanja, kot so:

```text
Is hard per-key spend control possible?

If not, can I build my own API server, issue my own keys,
do the accounting, and forward allowed requests to OpenAI?

Can the client remain the ordinary OpenAI Python client
with no code changes?

Before writing AGENTS.md, tell me how cost and token
accounting per key should work.

Now specify the building blocks and tools:
database, framework, admin UI, CLI, email, tests, deployment.

Should the database schema be placed in the repo before
the execution agent starts?
```

To niso prompti za nizkoravensko implementacijo. To so upravljavski prompti. Človek prispeva domenski namen, omejitve in pritisk sprejemljivosti. Strateški model prispeva arhitekturne možnosti in profesionalne privzete izbire. Izvajalni agent kasneje prejme omejeno delo.

### Tehnične odločitve, ki jih proizvede odkrivanje

Dober strateški model mora tehnične odločitve narediti razumljive domenskemu strokovnjaku. V primeru API Gatewaya je model pojasnil ne le kaj uporabiti, ampak tudi zakaj:

- **FastAPI, Starlette streaming, Uvicorn/Gunicorn**: asinhrona API logika, posredovanje Server-Sent Events in upravljanje produkcijskih workerjev.
- **PostgreSQL, SQLAlchemy async, asyncpg, Alembic**: trajna resnica o kvotah in obračunavanju, neblokirni dostop do baze ter ponovljiv razvoj sheme.
- **Redis in Celery**: kratkoživa koordinacija, omejitve hitrosti, rezervacije in ozadna opravila, kot so e-pošta in poročila.
- **Jinja2, HTMX, Tailwind, Typer**: preprosta administratorska nadzorna plošča in CLI, ne da bi se projekt spremenil v veliko frontend aplikacijo.
- **pytest, pytest-asyncio, respx/pytest-httpx, testcontainers, Hypothesis, Playwright**: testi za async kodo, mockane zunanje API-je, realno vedenje baze/Redisa, računovodske invariants in admin UI tokove.
- **Docker Compose**: ponovljiva majhna namestitev z API-jem, bazo, Redisom, workerjem, planerjem in po potrebi obratnim posrednikom.

Domenskemu strokovnjaku ni bilo treba poznati vseh teh komponent vnaprej. Moral pa je presoditi, ali vsaka komponenta služi cilju domene: omejenim delavniškim ključem, tajnosti ključev ponudnikov, dokazom o uporabi, OpenAI-združljivim primerom in poštenosti izdaje.

### Artefakti odkrivanja

Izhod strateškega odkrivanja mora biti zapisan, preden izvajalni agent začne široko implementacijo. V zrelem projektu OAP odkrivanje ustvari vsaj:

- kratek arhitekturni zapis;
- konstitucijo `AGENTS.md`;
- podatkovni model ali dokument sheme;
- matriko združljivosti, kadar se emulirajo zunanji API-ji;
- strategijo testiranja;
- osnutek namestitve;
- prvo zaporedje implementacije v velikosti enega PR-ja;
- eksplicitne necilje.

Za API Gateway je bil eden odločilnih artefaktov odkrivanja podatkovna shema. Strateški model je svetoval, da se v repozitorij doda človeku berljiv `docs/database-schema.md`, še preden Codex implementira SQLAlchemy modele in Alembic migracije. To je pravi OAP refleks: strateško odločitev naredi trajno, preden prosiš izvajalca, naj začne proizvajati kodo.

### Strateške odgovornosti

Strateška plast bi morala:

- razumeti cilj izdelka;
- ohranjati domenske predpostavke;
- prevajati domenski jezik v tehnične delovne naloge;
- ohranjati dolgoročni kontekst projekta;
- prepoznavati manjkajoče predpostavke;
- varno zaporejati delo;
- izbirati naslednji ozek PR;
- pisati eksplicitne delovne naloge;
- interpretirati agentska poročila;
- primerjati rezultate s konstitucijo;
- povezovati trditve s konkretnimi dokazi;
- odgovarjati na človekova vprašanja o pripravljenosti;
- razlagati tehnične dokaze v domenskih pojmih;
- odločati, ali je treba popraviti, nadaljevati ali ustaviti;
- vzdrževati povzetke stanja projekta;
- ustvarjati handoffe, ko kontekst postane prevelik.

Strateška plast ni nujno za vedno en sam model. Projekt lahko uporablja en model za načrtovanje, drugega za pregled kode, tretjega za kritiko dokumentacije in četrtega za zunanjo revizijo. Pomembno je, da človeški vodja nadzoruje, kdaj in zakaj so ti modeli vključeni, ter da ena strateška nit ostane odgovorna za zgodbo projekta.

### Izbira modela in ekonomika konteksta

OAP naj za strateško plast praviloma uporablja najmočnejši praktični model. To pomeni model z dobrim sklepanjem, dolgim kontekstom, zanesljivim sledenjem navodilom, dobrim razumevanjem kode in dovolj potrpežljivosti za primerjanje trditev z dokazi. Prav na strateški plasti so dragi tokeni najbolj dragoceni.

Razlog je ekonomika konteksta. Kontekst strateškega modela izgoreva počasi. Vsebuje:

- cilj izdelka;
- domensko besedišče in omejitve;
- arhitekturne odločitve;
- nerešena tveganja;
- izide prejšnjih PR-jev;
- trenutno stanje izdaje;
- sledove dokazov;
- človeške preference;
- povzetke handoffov;
- odprta vprašanja.

Kontekst izvajalnega agenta izgoreva hitro, ker bere datoteke, ureja kodo, vidi izhod ukazov, ponavlja poskuse ob neuspehih in raziskuje lokalno stanje. To je sprejemljivo. Izvajalec potrebuje le toliko konteksta, da dokonča eno nalogo velikosti PR-ja. Strateški model pa mora ohranjati kontinuiteto čez veliko takih nalog.

Želeno operativno stanje je:

- strateška UI ne izgublja konteksta;
- človek ne izgublja cilja;
- izvajalnemu agentu ni treba pomniti ničesar prek trenutnega PR-ja;
- trajno stanje se zapisuje nazaj v repozitorij, PR-je, issueje, dokumente in handoffe.

### Strateški izhod: delovni nalog

Najpomembnejši izhod strateške plasti ni koda. Je delovni nalog, ki mu lahko izvajalni agent sledi, ne da bi improviziral izdelek in ne da bi človeka prosil za nizkoravensko delo. Kadar je človek domenski strokovnjak, je delovni nalog tudi prevodni artefakt: domenski namen pretvori v izvedljivo programsko vedenje, hkrati pa ohranja kriterije sprejema.

Dober delovni nalog vsebuje:

- trenutno preverjeno stanje projekta;
- natančen cilj naloge;
- domensko vedenje, ki ga je treba ohraniti;
- kriterije sprejema v domenskem jeziku;
- datoteke ali področja za pregled;
- omejitve in necilje;
- zahtevano implementacijsko vedenje;
- teste, ki jih je treba dodati ali pognati;
- orodja, odvisnosti ali lokalne storitve, ki jih sme agent namestiti znotraj izvajalne virtualke;
- posodobitve dokumentacije;
- navodila za vejo in PR;
- obliko končnega poročila.

To je eden od razlogov, da OAP ni "prompt engineering" v plitkem smislu. Prompt je artefakt upravljanja programske opreme. Vsebuje obseg, tveganje, preverjanje in delovni tok.

### Strateški pregled agentskih poročil

Po izvedbi strateška plast pregleda:

- Ali je agent opravil zahtevano nalogo?
- Ali je opravil dodatno delo?
- Ali se je dotaknil nepovezanih datotek?
- Ali so testi smiselni?
- Ali so preskočeni testi pošteno poročani?
- Ali se je dokumentacija spremenila skupaj z vedenjem?
- Ali je sprememba ohranila arhitekturo?
- Ali je uvedla novo tveganje?
- Ali je agent človeka prosil za delo, ki bi moralo soditi v izvajalno virtualko?
- Ali je pred mergeanjem potreben popravljalni prompt?

Strateški model opravi prvi pregled in pripravi odgovore za človeka. Človek mora ta pregled presoditi. Model lahko spregleda tveganja. Model lahko pretirano hvali. Model lahko racionalizira. Človeški vodja mora ostati skeptičen, vendar naj se skeptičnost izraža kot poizvedovanje na visoki ravni:

- Pokaži mi točen dokaz o testih.
- Pokaži mi datoteke, ki uveljavljajo invariant.
- Pojasni, zakaj to ne izpostavlja skrivnosti.
- Pojasni, zakaj je ta odvisnost potrebna.
- Pojasni, kaj bi odpovedalo, če bi bilo to vedenje pokvarjeno.
- Povej mi, v kaj si najmanj prepričan.

### Strateška kontinuiteta

Dolgoročni projekti potrebujejo kontinuiteto. Strateška plast bi morala periodično ustvarjati jedrnate handoffe stanja. To niso samo zapiski za ljudi. So artefakti za ohranjanje konteksta v prihodnjih strateških sejah:

```markdown
# Projektni handoff

## Trenutna resnica
- Stanje glavne veje:
- Odprti PR-ji:
- Nedavno mergani PR-ji:
- Znano stanje CI:

## Cilj produkta
- Trenutni mejnik:
- Ciljna izdaja:

## Implementirano
- ...

## Manjkajoče
- ...

## Nepogajljiva pravila
- ...

## Naslednja priporočena naloga
- ...

## Naslednje ne počni
- ...
```

Handoff ni nadomestilo za preverjanje trenutnega stanja repozitorija. Je pripomoček za spomin. Vsaka nova strateška seja bi morala živi repozitorij obravnavati kot avtoritativen.

## III.2 Pisanje projektne konstitucije

Projektna konstitucija je trajen nabor pravil, ki agentom pove, kako naj delajo v repozitoriju. V Codexu je neposredni mehanizem `AGENTS.md`: Codex takšne datoteke prebere pred začetkom dela in po precedenci sloji globalna, projektna in gnezdena navodila [[1]](#ref-codex-agents-md). V Claude Code je analogen mehanizem projektnih navodil `CLAUDE.md`, ki ga Anthropic dokumentira kot trajna navodila, naložena na začetku seje [[38]](#ref-claude-code-memory). Druga orodja uporabljajo sorodne mehanizme: prilagojena repozitorijska navodila ali datoteke pravil [[39]](#ref-github-copilot-agent); [[40]](#ref-cursor).

Kadar lahko na projektu delata tako Codex CLI kot Claude Code CLI, naj bosta `AGENTS.md` in `CLAUDE.md` usklajena. Ni nujno, da sta beseda za besedo identična, vendar mora biti operativno pravo isto: poslanstvo, arhitektura, prepovedana dejanja, testi, delovni tok in zahteve za končno poročilo.

OAP konstitucijo obravnava kot prvovrsten artefakt.

<ExpandingSideImg
  src="../assets/fig-03-project-constitution.svg"
  alt="Projektna konstitucija kot večslojno operativno vodenje."
  caption="Projektna konstitucija kot večslojno operativno vodenje."
/>

### Odkrivanje pred konstitucijo

Konstitucija bi morala biti napisana po strateškem odkrivanju, ne pa pred njim. V nasprotnem primeru `AGENTS.md` postane seznam arbitrarnih preferenc namesto operativnega prava resničnega izdelka.

Domenski strokovnjak bi moral najprej uporabiti strateški model za raziskovanje:

- kategorije izdelka;
- uporabniškega delovnega toka;
- operativnih omejitev;
- mej varnosti in zasebnosti;
- verjetnih arhitektur;
- izbir sklada in alternativ;
- najmanjšega obsega smiselne prve izdaje;
- eksplicitnih neciljev.

Rezultat tega pogovora postane konstitucija. Strateški model jo lahko osnuje, vendar mora človek presoditi, ali odraža resnično domeno. Zato je uvodna faza OAP upravljavska. Človek ne sprašuje: "napiši mi Django kodo." Človek sprašuje: "glede na to domeno in te omejitve, ali naj bo to Django, FastAPI, Go, razširitev za brskalnik, lokalni agent, sistem na čakalnih vrstah, sistem podpisanih artefaktov ali nekaj tretjega?"

### Kaj je konstitucija

Konstitucija ni README. README projekt razloži uporabnikom in sodelavcem. Konstitucija agentu narekuje, kako naj se vede med spreminjanjem projekta.

Konstitucija ni en sam prompt. Prompt je začasen. Konstitucija ostaja čez več nalog in postane del operativnega spomina repozitorija.

Konstitucija ni zgolj slogovno vodilo. Vključevati bi morala arhitekturo, varnostna pravila, teste, pogodbe o dokumentaciji, delovni tok in definicijo dokončanosti.

### Minimalna struktura konstitucije

Resna OAP konstitucija bi morala vključevati:

```markdown
# AGENTS.md ali CLAUDE.md

## Povzetek odkrivanja
- Domenski problem.
- Izbrana oblika izdelka.
- Utemeljitev arhitekture in sklada.
- Pomembne zavrnjene alternative.
- Obseg prve izdaje.

## Poslanstvo
- Čemu je ta repozitorij namenjen.
- Katera obljuba uporabniku se ne sme prelomiti.

## Arhitektura
- Glavne komponente.
- Sklad in različice.
- Meje odgovornosti.
- Predpostavke o pretoku podatkov.

## Nepogajljivi invarianti
- Varnostna pravila.
- Pravila zasebnosti.
- Pravila hrambe podatkov.
- Pravila povratne združljivosti.

## Prepovedana dejanja
- Datoteke ali sistemi, ki se jih ne sme dotakniti.
- Odvisnosti, ki se jih ne sme dodajati.
- Skrivnosti, ki jih ni dovoljeno logirati ali commitati.
- Produkcijski viri, do katerih se ne sme dostopati.

## Delovni tok
- Zahteve za veje.
- Zahteve za commite.
- Zahteve za pull requeste.
- Brez neposrednih commitov v glavno vejo.

## Testiranje
- Zahtevani unit testi.
- Zahtevani integracijski testi.
- Kdaj so potrebni brskalniški/E2E testi.
- Kako poročati o preskočenih ali blokiranih testih.

## Dokumentacija
- Kateri dokumenti se morajo spremeniti skupaj z vedenjem.
- Kje živijo matrike združljivosti.
- Kako navesti omejitve.

## Poročanje
- Zahtevana oblika končnega poročila.
- Zahtevani dokazi.
- Zahtevan razdelek o tveganjih in naslednjih korakih.
```

### Konstitucija kot spomin

Dolgoročni projekti, podprti z UI, trpijo zaradi razpada konteksta. Zgodovine pogovorov postanejo predolge. Naložene datoteke potečejo. Modeli pozabijo podrobnosti. Konstitucija temu nasprotuje tako, da stabilno projektno pravo postavi v repozitorij.

Konstitucija bi se morala razvijati, ko se pojavljajo ponavljajoči popravki. Če agent večkrat odstrani zahtevan blok v README-ju, dodaj pravilo. Če agent večkrat trdi, da so preskočeni testi uspešni, dodaj jezik za poročanje. Če varnostni pregled najde razred nevarnega vedenja, ga zakodiraj kot prepovedano dejanje in kot zahtevo za test.

Uradna dokumentacija Codexa `AGENTS.md` izrecno predstavlja kot trajno projektno vodilo in priporoča njegovo uporabo za ukaze gradnje in testiranja, pričakovanja pregleda, konvencije in ponavljajoče povratne informacije [[1]](#ref-codex-agents-md). OAP to idejo razširi: pri resnem delu je konstitucija središče upravljanja.

### Testi vonja za konstitucijo

Konstitucija je prešibka, če:

- govori samo "piši dobro kodo";
- ne poimenuje testov;
- ne definira prepovedanega vedenja;
- ne razloži izdaje ali PR delovnega toka;
- ne omenja skrivnosti;
- ne pove, katere dokaze mora agent poročati;
- ne more pomagati novemu strateškemu modelu nadaljevati projekta.

Konstitucija je prevelika, če:

- vsebuje zastarel zgodovinski klepet;
- ponavlja dokumentacijo, ki je bolje shranjena drugje;
- presega kontekstne omejitve orodij;
- vsebuje protislovna pravila;
- jo agenti rutinsko ignorirajo, ker je preveč razpršena.

Rešitev je večslojno vodenje: vrhnja pravila za celoten repozitorij, gnezdena pravila za specializirane imenike in ločeni dokumenti za daljše ozadje.

## III.3 Inženiring delovnih nalogov

Promptanje v OAP ni stvar domiselnega fraziranja. Gre za inženiring delovnih nalogov. Delovni nalog strateško presojo pretvori v izvršljiva navodila. V zrelem OAP človek tega prompta za izvajalnega agenta običajno ne piše neposredno. Človek strateški UI razloži namen in vprašanja; strateška UI pa iz tega sestavi delovni nalog za izvajalca.

To je skladno s trenutno prakso kodirnih agentov: trajna priprava, dejanski delovni imenik in specifičnost navodil so skoraj tako pomembni kot sam priklic modela [[41]](#ref-codex-best-practices).

### Predloga delovnega naloga

```markdown
# Delovni nalog za kodirnega agenta

Delaš v repozitoriju: `<repo>`.

## Upravljalna navodila
- Najprej preberi `AGENTS.md`.
- Sledi delovnemu toku repozitorija.
- Če se živo stanje repozitorija razlikuje od tega prompta, poročaj o razliki.

## Trenutno preverjeno stanje
- ...

## Cilj
- ...

## Obseg
- ...

## Necilji
- ...

## Datoteke za pregled
- ...

## Zahtevano vedenje
- ...

## Zahtevani testi
- ...

## Dovoljena lokalna priprava
- Po potrebi namesti manjkajoča testna orodja znotraj izvajalne virtualke.
- Dokumentiraj vsako izvedeno pripravo paketov, brskalnikov, baze ali storitev.
- Človeka ne prosi za rutinsko pripravo odvisnosti, razen če to blokira varnostna meja.

## Zahtevana dokumentacija
- ...

## Delovni tok
- Začni iz sveže veje `main`.
- Ustvari funkcionalno vejo.
- Commitaj samo povezane datoteke.
- Pushaj vejo.
- Odpri pull request.
- Ne mergaj.

## Končno poročilo
- Veja.
- Commit.
- URL PR-ja.
- Povzetek.
- Zagnani testi in rezultati.
- Lokalno nameščena orodja ali odvisnosti.
- Spremenjena dokumentacija.
- Tveganja ali preskočeni testi.
```

### Trenutno stanje mora biti res trenutno

Delovni nalog ne bi smel slepo zaupati staremu handoffu. Moral bi povedati, kaj je znano, in agentu naložiti preverjanje. Če se je repozitorij medtem premaknil, bi moral agent to prijaviti, ne pa graditi na zastarelih predpostavkah.

To je še posebej pomembno pri dolgih projektih, kjer je med posameznimi pogovori merganih več PR-jev. Strateška plast bi morala pred pisanjem naslednje naloge preveriti trenutno `main`, odprte PR-je in CI. Človek bi moral biti sposoben vprašati strateški model "kaj je zdaj res?" in dobiti odgovor, utemeljen na stanju repozitorija, ne pa zgolj na spominu.

### Necilji kot varovalne ograje

Agenti naravno ne razumejo mej izdelka. Razumejo besedilo. Če se naloga ne sme dotakniti določenega podsistema, to povej. Če je neka mamljiva funkcionalnost odložena, to povej. Če dokumentacija ne sme pretiravati s trditvami o produkcijski pripravljenosti, to povej.

Dobri necilji so konkretni:

- "Ne dodajaj nove migracije baze."
- "Ne spreminjaj oblike javnega API-ja."
- "Ne shranjuj promptov ali surovih teles odgovorov."
- "Ne poganjaj resničnih klicev do zunanjih API-jev."
- "Preskočenih brskalniških testov ne poročaj kot uspešnih."

### Oblika poročila kot vmesnik

Končno poročilo je vmesnik med izvedbo in strategijo. Če je poročilo nestrukturirano, mora strateški model dokaze ročno rekonstruirati, človek pa bo potegnjen v nizkoravensko revizijsko delo. Če je poročilo strukturirano, lahko strateški model odgovori na človeška vprašanja na visoki ravni hitreje in z manj odmika.

Poročila bi morala razlikovati med:

- uspešno;
- neuspešno;
- preskočeno;
- ni bilo pognano;
- blokirano;
- izven obsega.

Frazi "vsi testi so uspešni" se je treba izogniti, razen če dobesedno pomeni, da je uspešno prešel zahtevani ali celoten relevantni testni nabor. "Usmerjeni testi so uspešni; integracijski testi niso bili pognani" je uporabnejša formulacija.

### Slabi znaki v promptih

Prompt je šibek, če pravi:

- "naredi to boljše";
- "dokončaj funkcionalnost";
- "popravi vse težave";
- "uporabi svojo presojo" brez omejitev;
- "poženi teste" brez navedbe katerih testov;
- "posodobi dokumentacijo" brez poimenovane dokumentacijske pogodbe;
- "vprašaj me, če manjkajo odvisnosti" brez navedenega varnostnega razloga.

Prompt je močnejši, če lahko strateška UI določi uspeh še preden agent začne in če lahko človek pozneje zaslišuje dokaze, ne da bi moral delo ročno rekonstruirati.

<Question
  id="oap-strategic-discovery-first"
  question="Kaj bi se moralo po priročniku zgoditi, preden se začne široka implementacija z izvajalnim agentom?"
  options={["Izvajalni agent bi moral improvizirati arhitekturo iz razporeditve repozitorija", "Človek bi moral najprej ročno namestiti vse verjetne odvisnosti", "* Strateško odkrivanje bi moralo določiti obliko izdelka, arhitekturo, omejitve in artefakte konstitucije", "Projekt bi moral preskočiti delovne naloge in iti neposredno v veliko implementacijsko vejo"]}
  attempts={2}
>
Priročnik vztraja, da mora strateška plast pred začetkom široke implementacije z izvajalnim agentom odkriti obliko sistema in zapisati trajno operativno pravo.
</Question>
