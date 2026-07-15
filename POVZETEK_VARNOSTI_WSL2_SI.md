# Navodila za vzpostavitev varnega WSL2 razvojnega okolja

**Datum prvotne izvedbe:** 14. julij 2026

**Okolje:** Linux gost v WSL2 na gostiteljskem sistemu Windows

## Namen in cilj

Linux uporabnik `mitjam` mora imeti možnost opravljati skrbniška opravila v gostujočem sistemu, vključno z uporabo `sudo` brez gesla. Hkrati naj bodo odstranjene privzete WSL2 poti, prek katerih bi lahko proces v Linuxu dostopal do datotek Windows ali zaganjal programe Windows.

Ta dokument opisuje dejansko izvedeni postopek. Ukazi in nastavitve veljajo za WSL2; pred uporabo na drugem sistemu je treba preveriti lokalne zahteve in način prenosa datotek.

## Postopek vzpostavitve

### 1. Določitev meje zaupanja

Najprej se preveri, da je okolje WSL2 gost na Windows, in opredeli cilj: polne skrbniške pravice znotraj Linux gosta, brez običajnih poti do gostiteljevih datotek in programov. To je pomembno zato, ker sta v privzeti namestitvi WSL2 pogosto omogočena samodejni priklop diskov Windows in medsebojno povezovanje z Windows.

### 2. Omogočanje skrbništva v Linux gostu

Za uporabnika `mitjam` se ustvari preverjena datoteka `sudoers`, ki omogoči `sudo` brez gesla. Skript je treba pognati z `sudo`; zapis se ustvari v `/etc/sudoers.d/mitjam`, nastavi na dovoljenje `0440` in preveri z `visudo`.

### 3. Utrditev WSL2

V `/etc/wsl.conf` se izklopijo Windows interop, uvoz Windows `PATH`, samodejni priklop Windows diskov in obdelava `/etc/fstab`. Sistem se nato znova zažene na način, ki ponovno naloži konfiguracijo WSL. S tem Linux gost ohrani običajno skrbniško uporabnost, vendar izgubi glavne priročne poti do Windows gostitelja.

### 4. Preverjanje po spremembi

Preveri se uspešnost `sudo`, vsebina aktivne `/etc/wsl.conf` in seznam priklopov. Pričakovano stanje je odsotnost priklopov DrvFS, kot je `/mnt/c`. WSL-ovi lastni priklopi, na primer `/mnt/wsl` in WSLg, niso priklopi diskov Windows in lahko ostanejo prisotni.

### 5. Razvojna orodja in dokumentacija

Po utrditvi se namesti in overi GitHub CLI, klonirata potrebna repozitorija, preberejo lokalna navodila projekta in zažene lokalni strežnik za dokumentacijo. Ta korak je ločen od utrditve: deluje znotraj gosta in ne zahteva ponovnega omogočanja Windows interopa ali samodejnega priklopa diskov.

## Končna konfiguracija

Aktivna datoteka `/etc/wsl.conf` določa naslednje nastavitve:

| Nastavitev | Učinek |
| --- | --- |
| `interop.enabled=false` | Linux procesi ne morejo neposredno zaganjati izvršljivih datotek Windows prek običajnega WSL medsebojnega povezovanja. |
| `appendWindowsPath=false` | Poti do programov Windows se ne dodajo samodejno v spremenljivko `PATH` v Linuxu. |
| `automount.enabled=false` | Pogoni Windows, kot je `C:`, se ne priklopijo samodejno pod `/mnt/c`. Zato Linux procesi nimajo običajnega neposrednega dostopa do datotek gostitelja prek DrvFS. |
| `mountFsTab=false` | WSL ob zagonu ne obdela `/etc/fstab`; s tem se zmanjša možnost, da bi kasnejši vnos znova priklopil datotečni sistem gostitelja. |
| `systemd=true` | V gostu ostane na voljo običajno okolje Linux storitev. |
| `default=mitjam` | Privzeti uporabnik WSL je `mitjam`. |

## Skrbniške pravice v gostu

Za račun `mitjam` je bila ustvarjena datoteka `/etc/sudoers.d/mitjam` z dovoljenjem `0440`. Omogoča uporabo `sudo` brez gesla samo v gostujočem Linux sistemu. Nastavitev je preverjena z orodjem `visudo`, kadar je to na voljo.

Ta pravica ne daje skrbniških pravic v Windows in sama po sebi ne odpira dostopa do datotek gostitelja.

## Preverjanje

Po izvedbi je bilo potrjeno:

- aktivna `/etc/wsl.conf` vsebuje zgornje omejitve;
- priklopov Windows DrvFS, na primer `/mnt/c`, ni;
- prisotni so le WSL-ovi lastni izvajalni priklopi, kot sta `/mnt/wsl` in podporni priklopi WSLg;
- uporabnik `mitjam` ostane običajen privzeti uporabnik v Linux gostu.

## Meja zaščite

Ti ukrepi odstranijo pogoste in priročne poti iz gosta v Windows: samodejno priklopljene diske, uvoženo pot Windows in neposredno zaganjanje programov Windows. WSL2 pa ni popoln peskovnik za nezaupanja vredno kodo. Gostiteljski Windows in njegova WSL upravljalna plast sta še vedno privilegiranejša od Linux gosta.

Pri prihodnjem prenosu datotek iz Windows v WSL je treba uporabiti izrecen, nadzorovan postopek prenosa. Ne omogočajte znova medsebojnega povezovanja z Windows ali samodejnega priklopa diskov samo zaradi prenosa datotek.

## Dobesedna navodila, uporabljena med vzpostavitvijo

Spodnji pozivi so prepis ključnih navodil iz prvotne seje. So navodila za agenta oziroma skrbnika, ne ukazi, ki bi jih bilo treba neposredno izvajati v terminalu.

### Pregled okolja in načrt utrditve

```text
in which environment do you run? is it a virtual machine?
```

```text
it is important that you check what you can do here
```

```text
check that document, you are running in wsl2 on windows and please verify if isolation is solid, as described here: https://edu.slaif.si/trainings/workshop-orchestrated-agentic-programming/oap-manual
```

```text
propose how to harden the isolation according to the document and my architecture/vm
```

### Skrbniške pravice in odločitev o meji zaščite

```text
tell me how to enable passwordless sudo. one copypastable line
```

```text
this does not work, create script in this folder I will execute with sudo.
```

```text
check passwordless sudo
```

```text
can you now fortify this vm according to the document? please tell me what you will do in 5 senteces and i will approve it
```

```text
THE KEY IS: my account in guest VM should be able to do anything, including passwordless sudo, but NOT be able to access the host in any way, neither read nor write!
```

```text
WSL2 hardening only!
```

```text
yes do it
```

### GitHub, repozitoriji in lokalni strežnik

```text
install gh!
```

```text
is gh properly authenticated?
```

```text
clone https://github.com/slaif-edu/trainings
```

```text
Clone this too https://github.com/biolab/notes-server
```

```text
let's enter trainings and read AGENTS.md
```

```text
I want to run local notes server for cloned trainings!
```
