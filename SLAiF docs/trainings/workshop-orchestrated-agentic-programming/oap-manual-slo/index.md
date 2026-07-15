---
title: "Priročnik za orkestrirano agentno programiranje (SLO)"
subTitle: "Človeško upravljan delovni tok za strateško UI, visoko-avtonomne kodirne agente in programsko opremo, pripravljeno za pregled in izdajo, različica 1.0.1"
language: "sl"
tocInHeader: true
chapters:
  - ./01-uvod-in-motivacija
  - ./02-operativna-priprava
  - ./03-stratesko-odkrivanje-in-konstitucija
  - ./04-kodiranje-in-preverjanje
  - ./05-pregled-revizija-in-objava
  - ./06-studije-primerov-in-uporabe
  - ./07-razprava-in-doktrina
  - ./08-dodatki
---

**Avtor:** Janez Perš  
**Email:** janez.pers@fe.uni-lj.si  
**Različica:** 1.0.1  
**Datum:** 2026-06-14

> Za inicializacijo strateškega modela si najprej prenesite [strategic_model_init_material.md](../strategic_model_init_material.md), odprite nov chat in izberite dovolj zmogljiv model. Dobre izbire so GPT-5.5 Thinking z nastavitvijo thinking effort na Extended, GPT-5.5 Pro, Claude Opus 4.8 ali Claude Sonnet 4.6. Če uporabljate Claude, nastavite effort na High ali Max in vključite Thinking. Nato datoteko naložite v pogovor in začnite z navodilom: "Preberi si priloženi tekst, ki opisuje koncept OAP, in povej, ali lahko igraš vlogo strateškega modela."

# Povzetek

Orkestrirano agentno programiranje je metoda gradnje programske opreme z UI-kodirnimi agenti, pri kateri človek ohranja upravljavsko vlogo. Loči strateško razmišljanje od operativne izvedbe: zmogljiva strateška UI z dolgim kontekstom pomaga domensko namero pretvoriti v arhitekturo, izbiro orodij, načrte nalog, kritiko in natančne delovne naloge, medtem ko visoko-avtonomen izvedbeni agent deluje znotraj utrjenega in obnovljivega strojnega okolja, kjer ureja datoteke, namešča orodja, poganja ukaze, izvaja teste, ustvarja commite in odpira pull requeste. Človek ostaja točka nadzora nad namero, tveganjem in izdajo, pri tem pa mu ni treba zapravljati časa za vsak nizkonivojski korak.

Ta priročnik predstavi orkestrirano agentno programiranje kot praktičen podtip agentnega programskega inženirstva. Je bolj disciplinirano od vibe codinga, bolj avtonomno od običajnega AI pair programminga in lažje upravljivo od odprtih rojev agentov. Njegovi osrednji artefakti so projektna konstitucija, kot je `AGENTS.md` za Codex CLI ali `CLAUDE.md` za Claude Code CLI, ozki delovni kosi v velikosti posameznega PR-ja, eksplicitni nečilji, ponovljivo preverjanje, poročila pripravljena za revizijo, oddaljeni repozitorij kot vir resnice in trajne predaje znanja. Priročnik zagovarja tezo, da se glavno ozko grlo pri z UI podprtem razvoju programske opreme premika od same proizvodnje kode k validaciji, upravljanju, ohranjanju konteksta in presoji.

Namesto obljube o lahkotnem ustvarjanju programske opreme ta priročnik uči ponovljiv delovni tok, s katerim postane UI-generirana programska oprema pregledljiva, omejena, podprta s testi in usklajena s človeško namero. Gre za vodnik, kako človeka razbremeniti nizkonivojskega implementacijskega dela, ne da bi izgubil visok nivo nadzora. V OAP se človek neizogibno premakne po lestvici navzgor: manj je tipkar kode, manj linijski programski inženir, bolj pa lastnik produkta, domenski strokovnjak, inženirski vodja, pregledovalec dokazov in avtoriteta za izdajo. Človek začne s tem, da strateško UI vpraša, kakšen sistem je sploh potreben in katera arhitektura ter orodja ustrezajo domeni; pozneje isto strateško UI zaslišuje o dokazih, tveganjih in pripravljenosti. Izvedbeni agent opravlja zamenljivo implementacijsko delo v omejenem izvajalnem okolju.

# Predgovor

Ta priročnik je namenjen ljudem, ki so že opazili, da sodobna UI-orodja za kodiranje niso več le autocomplete. Znajo pregledovati repozitorije, spreminjati datoteke, poganjati teste, uporabljati terminale in v nekaterih okoljih celo odpirati pull requeste. Praktično vprašanje ni več, ali UI zna proizvajati kodo. Praktično vprašanje je, kako to sposobnost organizirati tako, da je mogoče izdelovati resno programsko opremo, ne da bi pri tem izgubili nadzor nad arhitekturo, varnostjo, pravilnostjo, dokumentacijo in odgovornostjo.

Metoda, opisana tukaj, se imenuje **Orchestrated Agentic Programming**, okrajšano **OAP**. Ime je namenoma operativno. Ne trdi, da je vsaka posamezna komponenta nova. Repozitorijska navodila, kodirni agenti, AI pregled kode, delo po vejah, človeški pregled in raziskovalni sistemi z več agenti že obstajajo [[1]](#ref-codex-agents-md); [[2]](#ref-hula); [[3]](#ref-metagpt); [[4]](#ref-chatdev). Prispevek OAP je v kompoziciji: človeški vodja najprej uporabi strateški model za odkrivanje arhitekture in izbiro orodij, nato za kritiko in oblikovanje delovnih nalogov, implementacijo delegira visoko-avtonomnemu kodirnemu agentu v omejenem izvajalnem okolju, vsako spremembo pa obravnava kot pregledljivo, s testi podprto in revizijsko sledljivo enoto.

To ni priročnik o tem, kako klepetalnemu botu naročiti, naj napiše funkcijo. Prav tako ni priročnik o odstranitvi ljudi iz programskega inženirstva. Je priročnik o premiku človeka v vlogo z večjim vzvodom: domenski strokovnjak, lastnik namere, presojevalec produkta, lastnik tveganja, strateški zasliševalec, avtoriteta za izdajo in oblikovalec procesa. Človek ne sme postati pomočnik agenta, monter odvisnosti ali kurir za tracebacke. Če delovni tok povzroči, da agent človeka vodi skozi nizkonivojska opravila, je orkestracija spodletela.

Priročnik uporablja primere iz več tipov projektov: javni OpenAI-združljivi API prehod, zasebni ocenjevalni delovni tok, javni brskalniški SSH potek dela in javni zgodnji produkt za upravljanje infrastrukture. Zasebni primeri so uporabljeni zgolj kot oblikovno gradivo. Javni viri so citirani tam, kjer se priročnik sklicuje na širšo zgodovino, orodja, benchmarke, repozitorije in raziskave.

## Kako brati ta priročnik

Bralci, ki želijo najkrajšo pot, naj najprej preberejo dele I do V, nato pa še študijo primera SLAIF API Gateway v delu VI. Bralci, ki pripravljajo usposabljanje, naj preberejo celoten dokument in dodatke uporabijo kot delavniške predloge. Bralci, ki metodo presojajo bolj akademsko, naj se osredotočijo na konceptualna poglavja, poglavja o preverjanju in reviziji, študije primerov ter reference.

## Česa ta priročnik ne trdi

Ta priročnik ne trdi, da je OAP nova znanstvena disciplina. Ne trdi niti, da je zgodovinsko nova že sama zamisel, da domenski strokovnjaki gradijo ali oblikujejo programsko opremo; na sorodnem terenu delujejo end-user software engineering, low-code/end-user development, AI-assisted end-user coding in citizen development [[5]](#ref-ko-euse-2011); [[6]](#ref-schenkenfelder-lowcode-eud-2024); [[7]](#ref-weber-ai-eud-2025); [[8]](#ref-mit-ai-citizen-dev-2024). Prav tako ne trdi, da so kodirni agenti dovolj zanesljivi, da bi delovali brez meja. Ne trdi, da je visoko-avtonomna izvedba sama po sebi varna. Ne trdi, da je generiran pull request dokaz dokončanosti. In tudi ne trdi, da mora človek nujno ročno pregledati vsako vrstico vsakega diffa, ki ga je ustvaril agent. Trditev je ožja in močnejša: z ustrezno strateško kontrolno ravnino, projektno konstitucijo, obnovljivo izvajalno mejo, disciplino PR-jev, prakso preverjanja in zasliševanjem dokazov lahko kodirni agenti postanejo resna implementacijska delovna sila, ne da bi se človek spremenil v njihovega operaterja.
