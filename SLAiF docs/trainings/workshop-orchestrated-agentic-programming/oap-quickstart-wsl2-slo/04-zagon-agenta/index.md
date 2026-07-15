# 4. Zagon agenta

Preden zaženeš Codex CLI z ukazom `codex --yolo` ali Claude Code CLI z ukazom `claude --dangerously-skip-permissions`, ustvari navodila repozitorija.

Za Codex CLI je trajna datoteka z navodili `AGENTS.md`. Za Claude Code CLI je trajna datoteka z navodili `CLAUDE.md`. Za ta quickstart naj bosta vsebinsko enakovredni. Najpreprostejši pristop je, da obe datoteki ustvarita isto operativno vsebino:

```bash
cp AGENTS.md CLAUDE.md
git add AGENTS.md CLAUDE.md
git commit -m "Add OAP project constitution"
```

Če repozitorij eno od teh datotek že ima, je ne prepiši na slepo. Strateški model naj pomaga združiti OAP konstitucijo z obstoječimi navodili.

<Sidenote>
Ta korak je pomemben zato, ker so `AGENTS.md` in `CLAUDE.md` trajna navodila repozitorija, ne le enkratna navodila v klepetu. Kar ni zapisano tam, se pri kasnejših zagonih hitro izgubi.
</Sidenote>

Zdaj ustvari vejo:

```bash
git status
git switch -c oap-first-task
```

Nato v korenu repozitorija zaženi enega izvedbenega agenta.

Codex CLI:

```bash
codex --yolo
```

Enakovredno s Claude Code CLI:

```bash
claude --dangerously-skip-permissions
```

Enakovredna oblika nastavitve za Claude Code CLI:

```bash
claude --permission-mode bypassPermissions
```

Prilepi delovni nalog v takšni obliki:

```text
Najprej preberi AGENTS.md in CLAUDE.md.

Trenutno stanje:
- Repozitorij: <ime>
- Veja: oap-first-task
- Pomembne obstoječe datoteke:
  - <files>

Cilj:
- <ena majhna funkcionalnost, popravek, test ali izboljšava dokumentacije>

Kriteriji sprejema:
- <opazno vedenje>
- <testi ali preverjanja, ki morajo uspeti>
- <dokumentacija, ki jo je treba posodobiti>

Ne-cilji:
- Ne spreminjaj <nepovezanega področja>.
- Ne dodajaj <nezaželene odvisnosti>.
- Ne spreminjaj produkcijske namestitve.
- Ne dotikaj se skrivnosti ali pravih poverilnic.

Dovoljeno lokalno okolje:
- V tem okolju WSL2 Ubuntu smeš namestiti lokalna razvojna orodja.
- Dokumentiraj vsak nameščen paket ali orodje.
- Človeka ne prosi, naj izvaja rutinske ukaze za pripravo okolja, razen če te blokira resnična varnostna meja.

Testi:
- Zaženi <ukaz testa>.
- Če testov ni mogoče zagnati, pojasni natančno okoljsko blokado.
- Ne trdi, da so testi uspeli, razen če si jih zagnal ali to dokazuje CI.

Delovni tok:
- Diff naj ostane majhen.
- Commit-aj samo povezane datoteke.
- Ne mergaj.

Končno poročilo:
- Povzetek.
- Spremenjene datoteke.
- Zagnani ukazi.
- Rezultati testov.
- Nameščena lokalna orodja.
- Tveganja in omejitve.
- Predlagana naslednja naloga.
```

Izvedbeni agent naj dela znotraj WSL2. Pusti mu, da pregleda repozitorij, namesti manjkajoča lokalna orodja, zažene teste in ureja datoteke. Ne mikroupravljaj vsakega ukaza. Prekini ga samo, če skuša prečkati mejo: produkcijske poverilnice, skrivnosti gostitelja, nepovezane repozitorije, zaščitene veje ali široka destruktivna dejanja.

<Sidenote>
Če človek začne ročno izvajati vsak drugi ukaz namesto agenta, se OAP zanka hitro poruši. Namen ni popoln nadzor nad vsakim korakom, ampak dober nadzor nad mejo, obsegom in dokazovanjem.
</Sidenote>

Če agent prosi, da namestiš rutinski paket, mu vrni tole:

```text
Tečeš znotraj odobrenega izvedbenega okolja WSL2.
Če gre za običajno lokalno razvojno pripravo, jo namesti sam,
dokumentiraj ukaz in nadaljuj. Prosi me samo, če dejanje preseže
varnostno mejo.
```

Ta stavek pogosto zadošča, da se OAP kontrolna zanka spet vzpostavi.
