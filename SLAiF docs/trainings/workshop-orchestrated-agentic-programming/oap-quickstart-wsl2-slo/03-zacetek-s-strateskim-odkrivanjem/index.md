# 3. Začetek s strateškim odkrivanjem

Ne začni tako, da Codex CLI z ukazom `codex --yolo` ali Claude Code CLI z ukazom `claude --dangerously-skip-permissions` prosiš, naj "zgradi aplikacijo". Začni tako, da strateški model vprašaš, kakšen sistem domenski problem sploh zahteva.

To je ključna poteza za domenske strokovnjake. Operativni problem lahko poznaš zelo dobro, ne da bi poznal najboljšo arhitekturo. Strateški model lahko pomaga prevesti domenski namen v tehnično obliko.

Za ta pogovor uporabi močan splošni model. To je lahko ChatGPT, Claude ali drug model z dovolj sklepanja in konteksta. Ta strateški pogovor ni izvedbeni zagon. Opravi ga, preden zaženeš visokoavtonomnega CLI agenta.

Najprej prenesi [strategic_model_init_material.md](../../strategic_model_init_material.md), odpri nov chat in izberi dovolj zmogljiv model. Dobre izbire so GPT-5.5 Thinking z nastavitvijo thinking effort na Extended, GPT-5.5 Pro, Claude Opus 4.8 ali Claude Sonnet 4.6. Če uporabljaš Claude, nastavi effort na High ali Max in vključi Thinking. Nato datoteko naloži v pogovor in začni z navodilom: "Preberi si priloženi tekst, ki opisuje koncept OAP, in povej, ali lahko igraš vlogo strateškega modela." V tem delovnem toku je to priporočeni prvi pripravljalni korak pred tem pogovorom.

Kopiraj ta prompt:

```text
Želim uporabljati Orkestrirano agentno programiranje.

Moj domenski problem je:
<opiši dejanski operativni problem>

Uporabniki so:
<kdo to uporablja>

Pomembne omejitve:
<varnost, zasebnost, stroški, namestitev, skladnost, strojna oprema, roki>

Kakšen programski sistem je to v resnici?
Katera arhitektura in sklad sta primerna?
Katere meje zaupanja so pomembne?
Česa ne bi smeli graditi v prvem rezu?
Kateri testi bi dokazali prvo uporabno vedenje?
Kaj mora iti v AGENTS.md in CLAUDE.md, preden začne izvedbeni agent?
Katera je prva naloga velikosti enega PR-ja?
```

Dober strateški odgovor ne poimenuje le ogrodja. Pojasni:

- kategorijo produkta;
- podatkovni model;
- meje zaupanja;
- dolgočasne in robustne izbire sklada;
- operativna tveganja;
- ne-cilje;
- prvi uporaben rez;
- kaj mora izvedbeni agent dokazati.

Če strateški model poda nejasen odgovor, ga pritisni:

```text
Bodi konkreten. Poimenuj arhitekturo, sklad, podatkovni model, prvi mejnik,
prepovedana dejanja in teste. To moram pretvoriti v AGENTS.md,
CLAUDE.md in en izvedbeni delovni nalog.
```

Človeška odločitev je še vedno tvoja. Model predlaga; človek sprejme, zavrne ali preusmeri.
