# Dodatek A: Predletalni kontrolni seznam

To uporabi pred vsakim zagonom Codex CLI z `codex --yolo` ali Claude Code CLI z `claude --dangerously-skip-permissions`.

```text
[ ] Sem znotraj WSL2 Ubuntu, ne v običajni lupini Windows.
[ ] Repozitorij je pod ~/work ali na drugi poti znotraj datotečnega sistema Linux.
[ ] Git remote je nastavljen.
[ ] Delovno drevo je čisto ali pa je namerno umazano.
[ ] AGENTS.md obstaja za Codex CLI.
[ ] CLAUDE.md obstaja za Claude Code CLI.
[ ] Produkcijska .env datoteka ni prisotna.
[ ] Zasebni SSH ključi gostitelja ali produkcije niso bili kopirani v WSL2.
[ ] Lokalni ~/.ssh v gostu je pričakovan in vsebuje samo gradivo z omejenim obsegom.
[ ] Cloud, kube, Docker, brskalniške ali password-manager skrivnosti niso prisotne, razen če so izrecno omejene.
[ ] Prva naloga je velikosti enega PR-ja.
[ ] Delovni nalog vsebuje cilj, kriterije sprejema, ne-cilje, teste in zahteve za poročilo.
[ ] Vem, kako opustiti to vejo.
[ ] Izvedbeni agent ne more mergati lastnega PR-ja.
```

# Dodatek B: Prompti za kopiraj-prilepi

## Prompt za strateško odkrivanje

```text
Začenjam OAP projekt.

Domenski problem:
<problem>

Uporabniki:
<users>

Omejitve:
<varnost, zasebnost, stroški, namestitev, operacije>

Prosim, povej mi:
1. Kakšen sistem je to v resnici.
2. Katera arhitektura in sklad sta primerna.
3. Katere meje zaupanja so pomembne.
4. Kaj mora biti izključeno iz prvega reza.
5. Kateri testi naj dokažejo prvo uporabno vedenje.
6. Katera pravila sodijo v AGENTS.md in CLAUDE.md.
7. Katera je prva izvedbena naloga velikosti enega PR-ja.
```

## Prompt za izvedbeni delovni nalog

```text
Najprej preberi AGENTS.md in CLAUDE.md.

Trenutno stanje:
<state>

Cilj:
<ena majhna naloga>

Kriteriji sprejema:
<criteria>

Ne-cilji:
<explicit exclusions>

Dovoljeno lokalno okolje:
V tem okolju WSL2 Ubuntu smeš namestiti potrebna lokalna razvojna orodja.
Dokumentiraj, kaj namestiš. Ne prosi me, naj izvajam rutinske ukaze za pripravo
okolja, razen če te blokira resnična varnostna meja.

Testi:
<commands>

Delovni tok:
Diff naj ostane majhen. Commit-aj samo povezane datoteke. Ne mergaj.

Poročilo:
Povzetek, spremenjene datoteke, zagnani ukazi, rezultati testov, nameščena
orodja, tveganja in predlagana naslednja naloga.
```

## Prompt za popravilo

```text
To je naloga popravila.

Izvirni cilj:
<goal>

Problem, najden v pregledu:
<problem>

Popravi samo ta problem:
<narrow repair>

Ne refaktoriraj nepovezane kode.
Ne širi obsega.
Zaženi ustrezne teste in poročaj natančne rezultate.
```

## Prompt za strateško revizijo

```text
Preglej ta izvedbeni rezultat OAP.

Delovni nalog:
<paste>

Poročilo agenta:
<paste>

Povzetek diffa:
<paste>

Izhod testov:
<paste>

Povej mi:
1. Ali je cilj dosežen.
2. Ali so bili ne-cilji spoštovani.
3. Ali so testi smiselni.
4. Ali poročilo pretirava.
5. Ali ostajajo tveganja.
6. Ali naj sprejmem, popravim, zavrnem ali nadaljujem.
```

# Dodatek C: Minimalna projektna konstitucija

Ustvari `AGENTS.md` in `CLAUDE.md` iz te predloge. Naj bosta dovolj kratka, da jima bo agent dejansko sledil.

```markdown
# Projektna navodila

## Poslanstvo
Ta repozitorij implementira <produkt>. Ohrani <osrednjo obljubo>.

## Povzetek odkrivanja
- Domenski problem:
- Oblika produkta:
- Izbrana arhitektura:
- Utemeljitev sklada/orodij:
- Obseg prve izdaje:
- Eksplicitni ne-cilji:

## Arhitektura
- Glavne komponente:
- Podatkovni tok:
- Meje zaupanja:
- Zunanje storitve:

## Nepogajalska pravila
- Nikoli ne commit-aj skrivnosti.
- Nikoli ne logiraj surovih poverilnic.
- Ne dostopaj do produkcijskih sistemov.
- Ne mergaj lastnega PR-ja.
- Spremembe naj ostanejo velikosti enega PR-ja.

## Delovni tok
- Začni iz trenutnega main.
- Ustvari feature vejo.
- Commit-aj samo povezane datoteke.
- Končno poročilo naj ostane dejstveno.

## Lokalna priprava
- Manjkajoča lokalna razvojna orodja namesti samo znotraj odobrenega okolja WSL2 Ubuntu.
- Dokumentiraj nameščene pakete in ukaze za pripravo okolja.
- Človeka ne prosi za rutinsko pripravo, razen če te blokira resnična varnostna meja.

## Testi
- Zahtevani enotski testi:
- Zahtevani integracijski testi:
- Zahtevani lint/type checki:
- Če testa ni mogoče zagnati, poročaj natančen blocker.

## Dokumentacija
- Posodobi dokumentacijo, kadar se vedenje spremeni.
- Ne trdi, da je izdaja pripravljena brez človeške odobritve.

## Končno poročilo
- Veja:
- Commit:
- Povzetek:
- Spremenjene datoteke:
- Zagnani ukazi:
- Rezultati testov:
- Nameščena lokalna orodja:
- Tveganja:
- Predlagana naslednja naloga:
```

# Dodatek D: Opombe o virih

Ta quickstart je destilat dokumenta `final/orchestrated-agentic-programming-v1.0.1-2026-06-14.md`.

Trditve, specifične za orodja, so bile 2026-06-14 preverjene glede na aktualno javno dokumentacijo:

- OpenAI Codex CLI dokumentira `--dangerously-bypass-approvals-and-sandbox, --yolo` kot zagon brez odobritev ali peskovnika in pravi, da ga uporabljaj samo znotraj zunanje utrjenega okolja: [referenca za Codex CLI](https://developers.openai.com/codex/cli/reference)
- OpenAI Codex dokumentira `AGENTS.md` kot projektna navodila po meri: [vodič za AGENTS.md](https://developers.openai.com/codex/guides/agents-md)
- Anthropic Claude Code CLI dokumentira `--dangerously-skip-permissions` kot preskok permission promptov in kot ekvivalent `--permission-mode bypassPermissions`: [referenca za Claude Code CLI](https://code.claude.com/docs/en/cli-reference)
- Anthropic dokumentira `CLAUDE.md` kot trajna projektna/uporabniška navodila za Claude Code: [dokumentacija za pomnilnik Claude Code](https://code.claude.com/docs/en/memory)
- Microsoft reference za namestitev in konfiguracijo WSL: [namestitev WSL](https://learn.microsoft.com/en-us/windows/wsl/install), [datotečni sistemi WSL](https://learn.microsoft.com/en-us/windows/wsl/filesystems), [konfiguracija WSL](https://learn.microsoft.com/en-us/windows/wsl/wsl-config)

# Zahvala

Zahvaljujemo se EC/EuroHPC JU in Ministrstvu za visoko šolstvo, znanost in inovacije Republike Slovenije za podporo prek projekta SLAIF (številka nepovratnih sredstev 101254461).
