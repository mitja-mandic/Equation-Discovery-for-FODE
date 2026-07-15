# Povzetek varnostnih ukrepov v WSL2

**Datum izvedbe:** 14. julij 2026  
**Okolje:** Linux gost v WSL2 na gostiteljskem sistemu Windows

## Cilj

Linux uporabnik `mitjam` mora imeti možnost opravljati skrbniška opravila v gostujočem sistemu, vključno z uporabo `sudo` brez gesla. Hkrati naj bodo odstranjene privzete WSL2 poti, prek katerih bi lahko proces v Linuxu dostopal do datotek Windows ali zaganjal programe Windows.

## Uveljavljeni ukrepi

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

## Drugo opravljeno delo

- Nameščen in overjen je bil GitHub CLI.
- Klonirana sta bila repozitorija SLAiF trainings in BioLab notes-server.
- Prebrana so bila navodila repozitorija trainings in nastavljena lokalna strežba gradiv.
