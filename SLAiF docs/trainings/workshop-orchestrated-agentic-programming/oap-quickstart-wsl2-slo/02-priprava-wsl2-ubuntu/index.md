# 2. Priprava WSL2 Ubuntu

Ta quickstart obravnava WSL2 Ubuntu kot izvedbeno okolje. To ni popolna izolacija in ni varnostni produkt. Je pa praktična prva meja: agent dela v Linuxu, repozitorij živi v datotečnem sistemu Linux, skrivnosti gostitelja pa niso kopirane v gosta.

<Sidenote>
WSL2 tukaj ni predstavljen kot idealna varnostna rešitev, ampak kot pragmatična prva meja za hitro uvedbo. Glavni namen je, da agent ne dela neposredno v običajnem Windows uporabniškem okolju.
</Sidenote>

Namesti WSL2 Ubuntu iz PowerShella:

```powershell
wsl --install -d Ubuntu
wsl -l -v
wsl --set-version Ubuntu 2
```

Odpri Ubuntu in namesti osnovni toolchain:

```bash
sudo apt update
sudo apt upgrade -y
sudo apt install -y build-essential git curl wget unzip zip ca-certificates openssh-client
```

Ustvari delovni imenik na strani Linuxa:

```bash
mkdir -p ~/work
cd ~/work
git clone <repo-url>
cd <repo-name>
```

Repozitorij obdrži pod `~/work`, ne pod `/mnt/c/...`. WSL2 lahko dostopa do datotečnega sistema Windows, vendar je za delo s coding agenti datotečni sistem Linux čistejši in hitrejši. Agent ne bi smel dobiti širokih pravic pisanja v profil uporabnika Windows na gostitelju.

<Sidenote>
To je ena od najpomembnejših praktičnih odločitev v tem vodiču. Že sama postavitev repozitorija v Linux datotečni sistem pogosto odstrani veliko skritega trenja in nenamernega dostopa do gostitelja.
</Sidenote>

Če želiš zmanjšati nenamerno vezanost na Windows, uredi `/etc/wsl.conf`:

```ini
[automount]
enabled=false

[interop]
enabled=false
appendWindowsPath=false
```

Nato iz PowerShella ponovno zaženi WSL:

```powershell
wsl --shutdown
```

To je pri prvem poskusu opcijsko. Koristno pa je, ko želiš čistejšo mejo in manj nenamernih odvisnosti od gostitelja.

## Namesti agentska CLI orodja

Namesti in avtenticiraj Codex CLI v skladu z aktualno dokumentacijo OpenAI Codex. Ukaz, ki ga ta quickstart uporablja za visokoavtonomno izvajanje, je:

```bash
codex --yolo
```

Za isto izvedbeno vlogo s Claude Code CLI namesti in avtenticiraj Claude Code v skladu z aktualno dokumentacijo Anthropic. Enakovredni visokoavtonomni ukaz je:

```bash
claude --dangerously-skip-permissions
```

Claude Code dokumentira tudi enakovredno obliko nastavitve:

```bash
claude --permission-mode bypassPermissions
```

Lokalno stanje posameznega CLI-ja naj ostane znotraj WSL2. Če želiš, da so poti stanja stabilne, dodaj te vrstice v `~/.bashrc`, preden se prijaviš v orodja:

```bash
mkdir -p "$HOME/.codex-agent" "$HOME/.claude-agent"
export CODEX_HOME="$HOME/.codex-agent"
export CLAUDE_CONFIG_DIR="$HOME/.claude-agent"
```

Nato ponovno naloži lupino:

```bash
source ~/.bashrc
```

V tem quickstartu, kadar delovni nalog pravi "zaženi izvedbenega agenta", uporabi bodisi:

```bash
codex --yolo
```

ali:

```bash
claude --dangerously-skip-permissions
```

Nobenega od teh ukazov ne zaganjaj v običajnem domačem imeniku Windows. Zaženi ju znotraj projektnega imenika WSL2, ki si ga pripravil za agentsko delo.

## Ne vnašaj skrivnosti

Za prvi zagon uporabi najpreprostejše pravilo:

```text
Izvedbeno okolje agenta v WSL2 ne sme vsebovati ničesar, česar si ne moreš privoščiti izgubiti ali zamenjati.
```

To pomeni:

- ne kopiraj zasebnih SSH ključev produkcijskega gostitelja v WSL2;
- ne kopiraj cloud poverilnic v WSL2;
- ne kopiraj konfiguracij Kubernetes v WSL2;
- ne postavljaj produkcijskih `.env` datotek v repozitorij;
- ne priklapljaj in ne izpostavljaj profilov brskalnika ali datotek upravljalnika gesel;
- agentu ne daj poverilnic, s katerimi lahko spreminja produkcijske sisteme.

Lokalni imenik `~/.ssh` v gostu je normalen. Morda je potreben za Git prek SSH. Njegov obstoj ni problem. Problem je kopiranje zasebnih ključev gostitelja ali produkcije vanj. Raje uporabi ločen ključ za to okolje WSL2 ali pa HTTPS/token-based Git poverilnice z omejenim obsegom.

<Sidenote>
Razlika ni v tem, ali ključ obstaja, ampak od kod prihaja in kaj odpira. Ločen ključ za WSL2 pomeni manjši domet škode, če agent ali okolje odpovesta.
</Sidenote>

## Opcijski sudo brez gesla

OAP najbolje deluje, kadar lahko izvedbeni agent v izvedbenem okolju namesti običajna lokalna razvojna orodja. V WSL2 se lahko odločiš, da uporabniku WSL dovoliš sudo brez gesla:

```bash
sudo visudo -f /etc/sudoers.d/90-agent-nopasswd
```

Dodaj:

```txt
%sudo ALL=(ALL) NOPASSWD:ALL
```

Nato preveri:

```bash
sudo chmod 0440 /etc/sudoers.d/90-agent-nopasswd
sudo visudo -c
sudo -n true && echo "passwordless sudo works"
```

To je močna pravica. Sprejemljiva je samo zato, ker je agent v izbranem izvedbenem okolju WSL2 in ker je repozitorij trajna resnica. Ni sprejemljiva, če WSL2 vsebuje skrivnosti gostitelja, produkcijske poverilnice ali nenadomestljive podatke.

<Sidenote>
`NOPASSWD` ni splošno priporočilo za vsak Linux sistem. V tem vodiču je sprejemljiv samo v kombinaciji z omejenim, zavržljivim okoljem in jasno prepovedjo produkcijskih skrivnosti.
</Sidenote>
