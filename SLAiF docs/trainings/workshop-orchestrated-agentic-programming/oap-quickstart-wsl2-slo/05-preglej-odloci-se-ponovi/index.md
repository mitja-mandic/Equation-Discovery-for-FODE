# 5. Preglej, odloči se, ponovi

Poročila Codex CLI iz `codex --yolo` ali poročila Claude Code CLI iz `claude --dangerously-skip-permissions` ne obravnavaj kot dokaz. Obravnavaj ga kot trditev.

Najprej preglej delovno drevo:

```bash
git status
git diff --stat
git diff
```

Če je tveganje visoko, sam zaženi ali ponovno zaženi ustrezne teste:

```bash
<test command>
```

Nato strateški model prosi, naj revidira rezultat:

```text
Uporabil sem OAP. Izvedbeni agent je dokončal to nalogo.

Izvirni delovni nalog:
<prilepi delovni nalog>

Končno poročilo agenta:
<prilepi poročilo>

Povzetek diffa:
<prilepi git diff --stat>

Izhod testov:
<prilepi ustrezen izhod>

Preglej to kot reviewer in inženirski vodja:
- Ali je cilj dosežen?
- Ali so bili ne-cilji spoštovani?
- Ali so testi smiselni?
- Ali poročilo pretirava?
- Ali obstajajo varnostna ali arhitekturna tveganja?
- Ali naj to sprejmem, popravim, zavrnem ali zahtevam še en majhen PR?
```

Strateška revizija naj dokaze stisne v obliko, ki človeku omogoča hitro odločitev. Človek je še vedno lastnik odločitve.

<Sidenote>
Ključna poanta tega koraka ni, da strateški model "potrdi" agenta, ampak da hitreje izlušči, kje so dokazi, kje so luknje in kakšna odločitev se v resnici zahteva od človeka.
</Sidenote>

Uporabi štiri izide:

**Sprejmi.** Diff je majhen, testi so smiselni, dokumentacija je poštena, tveganja pa sprejemljiva.

**Popravi.** Delo je večinoma pravilno, vendar potrebuje ozko popravilo. Ustvari drugi delovni nalog za Codex CLI z `codex --yolo` ali za Claude Code CLI z `claude --dangerously-skip-permissions`.

**Zavrni.** Sprememba krši arhitekturo, posega v nepovezana področja, ne prestane testov ali rešuje napačen problem. Opusti vejo ali pa naj agent sam povrne svoje spremembe.

**Nadaljuj.** Naloga je dobra, vendar po zasnovi nepopolna. Strateški model naj predlaga naslednjo nalogo velikosti enega PR-ja.

<Sidenote>
`PR-sized` tukaj pomeni nekaj dovolj majhnega, da je diff mogoče dejansko razumeti in pregledati kot eno koherentno spremembo. Če je rezultat prevelik, je bil delovni nalog verjetno preširok.
</Sidenote>

Vsako zanko zaključi s trajno resnico:

```bash
git status
git log --oneline -5
```

Če je naloga sprejeta:

```bash
git push -u origin oap-first-task
```

Če je to del tvojega delovnega toka, odpri pull request. Agent ne sme mergati lastnega PR-ja. Izdaja ostaja človeška odločitev.
