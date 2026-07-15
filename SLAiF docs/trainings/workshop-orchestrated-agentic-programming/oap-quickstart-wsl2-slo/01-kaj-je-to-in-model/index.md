# Kaj je to

To je hitri vodič za ljudi, ki želijo preizkusiti **Orkestrirano agentno programiranje**, ne da bi prej prebrali celoten priročnik. Podpira samo eno postavitev:

- gostitelja Windows;
- izvedbeno okolje WSL2 Ubuntu;
- Git repozitorij, kloniran znotraj datotečnega sistema Linux v WSL2;
- visokoavtonomno izvajanje s Codex CLI z ukazom `codex --yolo`;
- enakovredno visokoavtonomno izvajanje s Claude Code CLI z ukazom `claude --dangerously-skip-permissions` ali `claude --permission-mode bypassPermissions`.

Ta quickstart namerno ignorira druge veljavne postavitve: Linux VM-je, macOS VM-je, kontejnerje, Windows Sandbox, trajne Windows VM-je, cloud agente in agentne roje. Tudi to je uporabno pozneje. Prvi zagon mora biti ozek.

Cilj je preprost: po branju tega vodiča naj bi domenski strokovnjak ali vodja projekta znal postaviti omejen delovni prostor v WSL2, vprašati strateški model, kaj je treba zgraditi, ustvariti trajna projektna navodila, delegirati eno majhno nalogo Codex CLI ali Claude Code CLI in pregledati rezultat, ne da bi postal terminalski asistent agenta.

Metoda ni "zaupaj agentu". Metoda je:

1. Postavi izvedbenega agenta v omejeno okolje.
2. Uporabi strateški model za načrtovanje in revizijo.
3. Izvedbenemu agentu daj majhen delovni nalog.
4. Zahtevaj dokaze.
5. Človek sprejme odločitev.

# 1. Model

OAP ima tri vloge.

**Človek je vodja.** Človek je lastnik domenskega problema, prioritet, tveganj, kriterijev sprejema in odločitve o izdaji. Ni nujno, da je profesionalni arhitekt programske opreme. To je v redu. V OAP človek prispeva domensko znanje in presojo, nato pa z močnim strateškim modelom to prevede v arhitekturo, izbiro orodij in delovne naloge.

**Strateški model je kontrolna ravnina.** Pomaga odgovoriti na vprašanja, kot so:

- Kakšen sistem je to v resnici?
- Kateri sklad je primeren?
- Katere meje zaupanja so pomembne?
- Česa še ne smemo graditi?
- Česa izvedbeni agent nikoli ne sme improvizirati?
- Ali je agentovo poročilo podprto z dokazi?

**Izvedbeni agent je potrošno implementacijsko delo.** V tem quickstartu je izvedbeni agent bodisi Codex CLI z ukazom `codex --yolo` bodisi Claude Code CLI z ukazom `claude --dangerously-skip-permissions` ali `claude --permission-mode bypassPermissions`. Ureja datoteke, namešča orodja, zaganja teste, zažene storitve, commit-a delo in napiše poročilo.

Človek ne bi smel ves dan tipkati ukazov za odvisnosti namesto agenta. Če agent v WSL2 potrebuje testno odvisnost, browser driver, paket, lokalno podatkovno bazo ali prevajalnik, naj to praviloma namesti sam in poroča, kaj je naredil. Meja je WSL2 plus Git, ne pa stalno človeško odobravanje vsakega ukaza lupine.

Trajna resnica ni klepet in ni WSL2 stroj. Trajna resnica je:

- Git repozitorij;
- `AGENTS.md` in `CLAUDE.md`;
- commit-i;
- pull requesti;
- izhod testov;
- dokumentacija;
- opombe pregleda;
- odločitve o izdaji.

Osnovna zanka je:

```text
domenski problem
  -> strateško odkrivanje
  -> AGENTS.md / CLAUDE.md
  -> majhen delovni nalog
  -> Codex CLI / Claude Code CLI run
  -> poročilo z dokazi
  -> strateška revizija
  -> človeška odločitev
  -> naslednji delovni nalog
```

Ta zanka naj bo kratka. Ena naloga mora biti dovolj majhna, da človek razume diff in dokaze.
