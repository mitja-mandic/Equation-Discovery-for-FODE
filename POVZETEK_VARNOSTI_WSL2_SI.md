# Navodila za vzpostavitev varnega WSL2 razvojnega okolja

**Datum prvotne izvedbe:** 14. julij 2026

**Okolje:** Linux gost v WSL2 na gostiteljskem sistemu Windows

## Namen in cilj

Uporabnik `wsluser` mora imeti polne skrbniške pravice v Linux gostu, vključno z uporabo `sudo` brez gesla, vendar brez privzetih WSL2 poti do datotek in programov Windows.

Ime `wsluser` je splošen primer; nadomestiti ga je treba z dejanskim uporabniškim imenom v Linuxu. Nastavitve veljajo za WSL2.

## Postopek vzpostavitve

### 1. Določitev meje zaupanja

**Pozivi:**

```text
in which environment do you run? is it a virtual machine?

it is important that you check what you can do here

check that document, you are running in wsl2 on windows and please verify if isolation is solid, as described here: https://edu.slaif.si/trainings/workshop-orchestrated-agentic-programming/oap-manual

propose how to harden the isolation according to the document and my architecture/vm
```

**Rezultat:** preverjeno je bilo, da je okolje WSL2 gost na Windows, nato pa je bil pripravljen načrt utrditve. Cilj so bile polne skrbniške pravice znotraj Linux gosta brez običajnih poti do gostiteljevih datotek in programov. V privzeti namestitvi WSL2 sta namreč pogosto omogočena samodejni priklop diskov Windows in medsebojno povezovanje z Windows.

### 2. Omogočanje skrbništva v Linux gostu

**Pozivi:**

```text
tell me how to enable passwordless sudo. one copypastable line

this does not work, create script in this folder I will execute with sudo.
```

**Rezultat:** ker enovrstični postopek ni deloval, je bil ustvarjen namenski skript. Skript se požene z `sudo` in za uporabnika `wsluser` ustvari `/etc/sudoers.d/wsluser`, nastavi dovoljenje `0440` ter zapis preveri z `visudo`. Tako je omogočen `sudo` brez gesla znotraj Linux gosta.

### 3. Utrditev WSL2

**Pozivi:**

```text
can you now fortify this vm according to the document? please tell me what you will do in 5 senteces and i will approve it

THE KEY IS: my account in guest VM should be able to do anything, including passwordless sudo, but NOT be able to access the host in any way, neither read nor write!

WSL2 hardening only!

yes do it
```

**Rezultat:** po potrditvi obsega je bila spremenjena `/etc/wsl.conf`. Izklopljeni so bili Windows interop, uvoz Windows `PATH`, samodejni priklop diskov Windows in obdelava `/etc/fstab`. Sistem je bil nato znova zagnan tako, da je WSL ponovno naložil konfiguracijo. Linux gost je ohranil skrbniško uporabnost, izgubil pa glavne priročne poti do Windows gostitelja.

### 4. Preverjanje po spremembi

**Poziv:**

```text
check passwordless sudo
```

**Rezultat:** potrjena je bila uporaba `sudo` brez gesla. Dodatno sta bili preverjeni aktivna `/etc/wsl.conf` in stanje priklopov. Priklopov DrvFS, kot je `/mnt/c`, ni bilo. WSL-ovi lastni priklopi, na primer `/mnt/wsl` in WSLg, niso priklopi diskov Windows in so ostali prisotni.

### 5. Razvojna orodja in dokumentacija

**Pozivi:**

```text
install gh!

is gh properly authenticated?

clone https://github.com/slaif-edu/trainings

Clone this too https://github.com/biolab/notes-server

let's enter trainings and read AGENTS.md

I want to run local notes server for cloned trainings!
```

**Rezultat:** nameščen in overjen je bil GitHub CLI, klonirana sta bila zahtevana repozitorija, prebrana so bila lokalna navodila projekta in zagnan je bil lokalni strežnik za dokumentacijo. Ta korak je ločen od utrditve in ne zahteva ponovnega omogočanja Windows interopa ali samodejnega priklopa diskov.

## Končna konfiguracija

Aktivna datoteka `/etc/wsl.conf` določa naslednje nastavitve:

| Nastavitev | Učinek |
| --- | --- |
| `interop.enabled=false` | Linux procesi ne morejo neposredno zaganjati izvršljivih datotek Windows prek običajnega WSL medsebojnega povezovanja. |
| `appendWindowsPath=false` | Poti do programov Windows se ne dodajo samodejno v spremenljivko `PATH` v Linuxu. |
| `automount.enabled=false` | Pogoni Windows, kot je `C:`, se ne priklopijo samodejno pod `/mnt/c`. Zato Linux procesi nimajo običajnega neposrednega dostopa do datotek gostitelja prek DrvFS. |
| `mountFsTab=false` | WSL ob zagonu ne obdela `/etc/fstab`; s tem se zmanjša možnost, da bi kasnejši vnos znova priklopil datotečni sistem gostitelja. |
| `systemd=true` | V gostu ostane na voljo običajno okolje Linux storitev. |
| `default=wsluser` | Privzeti uporabnik WSL je `wsluser`; ime se prilagodi dejanskemu računu. |

## Meja zaščite

Ti ukrepi odstranijo pogoste in priročne poti iz gosta v Windows: samodejno priklopljene diske, uvoženo pot Windows in neposredno zaganjanje programov Windows. WSL2 pa ni popoln peskovnik za nezaupanja vredno kodo. Gostiteljski Windows in njegova WSL upravljalna plast sta še vedno privilegiranejša od Linux gosta.

Pri prihodnjem prenosu datotek iz Windows v WSL je treba uporabiti izrecen, nadzorovan postopek prenosa. Ne omogočajte znova medsebojnega povezovanja z Windows ali samodejnega priklopa diskov samo zaradi prenosa datotek.
