# Del II: Operativna priprava

## II.1 Načela zasnove izvajalnega okolja

Avtonomija izvajalnega agenta ni samo izbira v pozivu. Je odločitev o zasnovi izvajalnega okolja. OAP lahko uporablja previdne načine odobravanja, vendar njegova najbolj značilna oblika uporablja visoko-avtonomnega kodirnega agenta v namenski virtualki ali podobno omejenem strojnem okolju. Virtualki ne zaupamo zato, ker bi bil agent neškodljiv. Zaupamo ji zato, ker je utrjena, izolirana, obnovljiva in ni izvor resnice o projektu.

<ExpandingSideImg
  src="../assets/fig-06-runtime-boundary.svg"
  alt="Visoka avtonomija sodi znotraj namerno postavljene meje izvajalnega okolja."
  caption="Visoka avtonomija sodi znotraj namerno postavljene meje izvajalnega okolja."
/>

### Zakaj je izvajalno okolje pomembno

Agent, ki lahko ureja datoteke, ne more pa poganjati testov, je generator kode z dodatnimi koraki. Agent, ki lahko izvaja ukaze, namešča odvisnosti, zaganja storitve, poganja migracije nad testnimi bazami, pregleduje dnevnike in odpira pull requeste, lahko nadomesti velik del človeškega implementacijskega dela.

Takšno moč je treba omejiti. Izvajalno okolje mora biti zasnovano tako, da je agent lahko učinkovit, ne da bi se približal produkcijskim skrivnostim ali produkcijskim podatkom.

Izvajalno okolje mora varovati tudi človeški čas. Sodoben kodirni agent lahko v času, ko človek prebere eno napako odvisnosti, poskusi več popravkov, zagonov testov, namestitev paketov in popravil. Če ga blokira vsako manjkajoče orodje, človek postane počasni izvrševalnik v sistemu. Delovni tok takrat preneha biti OAP in postane z UI usmerjeno človeško delo.

<Sidenote>
Zasnova izvajalnega okolja v tem priročniku ni samo varnostna tema. Je tudi odločitev o upravljanju: meja naj absorbira rutinsko pripravljalno delo, da človek ostane na odločitveni ravni.
</Sidenote>

### Privilegiji kot meja učinkovitosti

Visoki privilegiji so pogosto obravnavani samo kot varnostni problem. V OAP so tudi meja učinkovitosti. Vprašanje ni: "Kako malo lahko agent naredi?" Vprašanje je: "Kaj lahko agent naredi znotraj prostora, ki smo ga pripravljeni zavreči?"

Če strateška UI odloči, da mora izvajalni agent uporabiti novo knjižnico za testiranje, poganjalnik brskalnika, razširitev baze podatkov, prevajalnik, upravitelja paketov ali migracijsko orodje, bi moral izvajalni agent to praviloma namestiti in nastaviti znotraj izvajalne virtualke. Agent naj dokumentira ukaze in commita trajne spremembe projekta. Človeku ne bi smel nalagati ročnega lovljenja odvisnosti, razen če dejanje prečka namerno postavljeno varnostno mejo.

Ta razlika je pomembna, ker je delo z odvisnostmi natanko tista nizkoravenska opravila, ki jih OAP skuša odstraniti iz človekovega dela. Manjkajoča sistemska knjižnica, Docker dovoljenje, Playwright brskalnik, Python wheel, Node paket ali priprava podatkov za bazo lahko porabijo ure. To je slaba raba časa vodilnega človeka, če se lahko delo opravi v zavržljivi virtualki.

Prednostna zasnova je torej:

- visoki privilegiji znotraj izvajalne virtualke;
- brez produkcijskih skrivnosti znotraj izvajalne virtualke;
- brez nenadomestljivih podatkov znotraj izvajalne virtualke;
- oddaljeni repozitorij in PR-ji kot trajna resnica;
- ukazi za pripravo, ki jih dokumentira agent;
- možnost obnove virtualke iz repozitorija in pripravljalnih zapiskov;
- možnost opustitve pokvarjene virtualke brez izgube stanja projekta.

Če agent uniči virtualko, je neuspeh samo operativni šum. Če človek porabi ure za delo z odvisnostmi namesto agenta, se je kontrolna zanka obrnila narobe.

### Omejen vzorec visoke avtonomije

Osrednji vzorec je:

1. Uporabi namensko virtualko, vsebnik, devcontainer ali oblačni sandbox.
2. Vanj postavi samo predvideni repozitorij in testne podatke.
3. Agentu daj dovolj dovoljenj za nameščanje, gradnjo, testiranje in poganjanje lokalnih storitev.
4. Produkcijskih poverilnic ne vključuj.
5. Uporabljaj ločene testne baze in zavržljive storitve.
6. Vse spremembe naj bodo vidne prek verzijskega nadzora.
7. Zahtevaj pull requeste namesto neposrednih sprememb glavne veje.
8. Oddaljeni repozitorij, ne virtualka, naj bo izvor resnice.

Tako je način visoke avtonomije lahko uporaben, ne da bi se pretvarjali, da je neškodljiv. Dokumentacija Codexa označuje `--dangerously-bypass-approvals-and-sandbox`, znan tudi kot `--yolo`, kot nevaren polni dostop: brez sandboxa in brez odobritev [[15]](#ref-codex-security). Claude Code dokumentira enakovreden način za obvoz dovoljenj visoke avtonomije kot `--dangerously-skip-permissions`, ekvivalent `--permission-mode bypassPermissions` [[16]](#ref-claude-code-cli-reference). OAP lahko tak način uporablja samo, kadar je zunanji strojni rob dejanski varnostni mehanizem.

### Brez gesla za sudo ni isto kot brez meje

Fraza "brez gesla za sudo" lahko pomeni dve različni stvari:

- agent nima možnosti povišanja pravic in je omejen z uporabniškim računom;
- agent lahko uporablja `sudo` brez gesla za izbrane ukaze ali za širša administrativna dejanja.

OAP mora to izraziti jasno. Dobra izvajalna virtualka lahko dovoli uporabo brezgeselnega dostopa za lokalne testne priprave, nameščanje paketov, Docker za zavržljive storitve, odvisnosti brskalnikov ali pripravo podatkov za bazo. Slaba izvajalna virtualka da široka korenska pooblastila v bližini produkcijskih podatkov ali dragocenih osebnih datotek.

Pravo vprašanje ni: "Ali ima agent sudo?" Prava vprašanja so:

- Kaj lahko agent uniči?
- Katere skrivnosti lahko prebere?
- Do katerih omrežij lahko dostopa?
- Katere trajne sisteme lahko spremeni?
- Ali je vsako spremembo mogoče razveljaviti?
- Ali je vsak zunanji učinek mogoče revidirati?
- Ali je virtualko mogoče obnoviti, če se poškoduje?
- Ali agent od človeka zahteva delo, ki bi ga moral biti sposoben varno opraviti znotraj virtualke?

### Kontrolni seznam izvajalnega okolja

Pred izvajanjem v načinu visoke avtonomije preveri:

- repozitorij je pod verzijskim nadzorom;
- agent začne iz čistega delovnega drevesa ali pa poroča o obstoječih spremembah;
- produkcijske skrivnosti niso prisotne;
- testne skrivnosti so očitno lažne ali zavržljive;
- baze podatkov so testne baze;
- zunanji API-ji so mockani, razen če so izrecno potrebni;
- dostop do omrežja je nameren;
- pravila za nameščanje paketov so jasna;
- Docker ali dovoljenja storitev so razumljena;
- koraki za obnovo virtualke so dokumentirani;
- oddaljeni repozitorij in PR-ji vsebujejo trajno resnico projekta;
- agent ne more neposredno pushati v zaščitene veje;
- končni rezultat mora biti veja in PR, ne pa nesleden lokalni poseg.

### Proti-vzorci izvajalnega okolja

Izogibaj se:

- poganjanju visoko-avtonomnega agenta na razvijalskem prenosniku, polnem nepovezanih skrivnosti;
- dostopu do produkcijskih baz podatkov;
- temu, da agentu podeliš oblačne poverilnice s širokimi pravicami;
- temu, da agent spreminja skrivnosti CI;
- temu, da agent mergne svoj lastni PR;
- temu, da mora agent človeka prositi za rutinsko nameščanje odvisnosti;
- sprejemanju trditve "testi so uspešni" brez izpisa ukaza ali potrditve iz CI;
- poganjanju visoke avtonomije v mapi, ki ni pod verzijskim nadzorom.

Visoka avtonomija ni nevarna zato, ker je visoka avtonomija. Nevarna je, kadar okoliški sistem predpostavlja, da se bo agent vedel kot skrben človek, ali kadar izvajalno okolje vsebuje sredstva, ki nikoli ne bi smela biti znotraj območja udarca. V dobro zasnovanem OAP okolju je agent lahko močan prav zato, ker je okolje zavržljivo, trajno stanje pa je drugje.

## II.2 Osnovna postavitev agentne virtualke

Operativna priprava je delo, ki se opravi, preden izvajalni agent prejme nalogo kodiranja. Odgovarja na eno vprašanje: ali lahko agent deluje z dovolj moči, da je uporaben, ne da bi pri tem lahko poškodoval človekovo delovno postajo, gostiteljev domači imenik ali dolgožive poverilnice?

To ni problem zadrževanja zlonamerne kode. OAP ne predpostavlja, da so kodirni agenti zlonamerni. Predpostavlja pa, da je lahko avtonomno izvajanje ukazov napačno, preširoko, zmedeno zaradi navodil v repozitoriju ali potisnjeno v nevarne poti s skriptami odvisnosti. Razumen cilj je:

- agent lahko znotraj svojega okolja namešča orodja in poganja teste;
- agent ne more brati ali prepisovati človekovega običajnega domačega imenika;
- agent ne more doseči dolgoživih SSH, oblačnih, brskalniških, upravljalnikov gesel ali produkcijskih poverilnic;
- agent je mogoče poceni ponastaviti;
- trajno delo živi v Gitu, ne v zavržljivem stroju.

Za terminalske kodirne agente je to najpomembnejše pri uporabi načinov polnega dostopa ali obvoza dovoljenj. Codex dokumentira `--dangerously-bypass-approvals-and-sandbox`, znan tudi kot `--yolo`, kot izvajanje ukazov brez odobritev ali sandboxa in pravi, da naj se uporablja samo znotraj zunanje utrjenega okolja [[17]](#ref-codex-cli-reference). Claude Code dokumentira `--dangerously-skip-permissions` kot preskok potrditvenih vprašanj za dovoljenja in kot ekvivalent `--permission-mode bypassPermissions` [[16]](#ref-claude-code-cli-reference). Odgovor OAP je, da trdo mejo postavi zunaj CLI agenta: gostujoči stroj, distribucija, sandbox ali virtualka so varnostna meja.

### Osnovna postavitev Linux gosta

Ta vzorec uporabi znotraj zavržljive Ubuntu virtualke, uvožene distribucije WSL2, Lime virtualke, Multipass virtualke, Linux virtualke v Hyper-V ali podobnega gosta:

```bash
sudo adduser agent
sudo usermod -aG sudo agent
sudo visudo -f /etc/sudoers.d/90-agent-nopasswd
```

Dodaj:

```txt
agent ALL=(ALL) NOPASSWD:ALL
```

Nato preveri:

```bash
sudo chmod 0440 /etc/sudoers.d/90-agent-nopasswd
sudo visudo -c
su - agent
sudo -n true && echo "passwordless sudo works"
```

Stanje agenta naj ostane lokalno pri gostu:

```bash
mkdir -p "$HOME/.codex-agent"
export CODEX_HOME="$HOME/.codex-agent"
mkdir -p "$HOME/.claude-agent"
export CLAUDE_CONFIG_DIR="$HOME/.claude-agent"
```

Za zagon Codex CLI v načinu visoke avtonomije znotraj tega gosta:

```bash
cd ~/work/project
codex --yolo
```

Ekvivalentna dolga oblika Codex CLI je:

```bash
codex --dangerously-bypass-approvals-and-sandbox
```

Za isto izvajalno vlogo s Claude Code CLI:

```bash
cd ~/work/project
claude --dangerously-skip-permissions
```

Ekvivalentna nastavitev v obliki Claude Code CLI je:

```bash
claude --permission-mode bypassPermissions
```

Repozitorij naj bo kloniran v datotečni sistem gosta ali v ozek projektni mount. Domačega imenika gostitelja ne montiraj z dovoljenjem za pisanje. Ne montiraj gostiteljevih SSH ključev, imenikov z oblačnimi poverilnicami, profilov brskalnika, datotek upravljalnika gesel, Docker socketa ali produkcijskih `.env` datotek. Gostujoča lokalna datoteka `~/.ssh/authorized_keys` za vhodni dostop je v redu; gostiteljevi zasebni ključi in produkcijske SSH poverilnice pa niso.

### SSH dostop do gosta

Pri delovnih tokovih z dostopom prek SSH namesti OpenSSH znotraj gosta in se poveži z gostitelja:

```bash
sudo apt update
sudo apt install -y openssh-server
sudo systemctl enable --now ssh || sudo service ssh start
mkdir -p ~/.ssh
chmod 700 ~/.ssh
```

Nato dodaj gostiteljev javni ključ v `~/.ssh/authorized_keys` znotraj gosta. Daj prednost prijavi s SSH ključi pred gesli. Za lokalno virtualko po možnosti veži posredovana vrata na localhost:

```text
host localhost:2222 -> guest port 22
```

SSH meja je meja udobja, ne pa varnostna meja. Varnostna meja so še vedno izolacija gosta, pravila montiranja datotečnih sistemov in odsotnost gostiteljskih skrivnosti. V SSH-dostopni virtualki ali sandboxu bo `~/.ssh` praviloma obstajal. Njegov obstoj ni napaka operativne priprave; kopirane gostiteljske identitete, produkcijski zasebni ključi, agent forwarding v gosta ali široki mounti poverilnic pa so napaka.

### Posnetek in ponastavitev

Operativna priprava ni popolna, dokler ponastavitev ni poceni:

```text
before run:
  snapshot/export/checkpoint the guest

after broken run:
  destroy or revert the guest

after useful run:
  preserve only Git commits, PRs, logs, and documented setup changes
```

Če okolje zahteva ure za ponovno vzpostavitev, bodo ljudje v skušnjavi, da ga začnejo obravnavati kot nenadomestljivo delovno postajo. OAP okolja je treba namesto tega upravljati kot zamenljive izvajalne enote: dragocene med delom, obnovljive po poškodbi.

## II.3 Recepti za platforme

Naslednji recepti so izhodišča, ne pa zahteve za skladnost. Izberi najšibkejšo postavitev, ki še vedno varuje podatke gostitelja in agentu omogoča resnično delo. Privzeto priporočilo je Linux virtualka ali WSL2 distribucija za posamezni projekt pri Linux-usmerjenem delu, trajna Windows virtualka pa samo, kadar so potrebna izvorna Windows orodja.

<ExpandingSideImg
  src="../assets/fig-07-preflight-platforms.svg"
  alt="Izbire platforme za operativno pripravo."
  caption="Izbire platforme za operativno pripravo."
/>

### Windows možnost A: WSL2 Ubuntu za posamezen projekt

WSL2 je priročno Linux okolje, gostovano znotraj Windows. Microsoft dokumentira `wsl --install` kot privzeto pot namestitve in navaja, da nove namestitve privzeto uporabljajo WSL2 [[18]](#ref-microsoft-wsl-install). Za delo s kodirnimi agenti:

```powershell
wsl --install -d Ubuntu
wsl -l -v
wsl --set-version Ubuntu 2
```

Znotraj Ubuntuja:

```bash
sudo apt update
sudo apt upgrade -y
sudo apt install -y build-essential git curl wget unzip zip ca-certificates openssh-server
```

Linux projekte hrani v Linux datotečnem sistemu, ne pod `/mnt/c`, ker Microsoft zaradi zmogljivosti priporoča, da projekti za Linux ukazno vrstico ostanejo v datotečnem sistemu WSL [[19]](#ref-microsoft-wsl-filesystems):

```bash
mkdir -p ~/work
cd ~/work
git clone <repo-url>
```

Za utrjeno agentsko distribucijo zmanjša naključno vezanost na gostitelja v `/etc/wsl.conf`:

```ini
[automount]
enabled=false

[interop]
enabled=false
appendWindowsPath=false

[user]
default=agent
```

Nastavitve WSL so razdeljene med distribucijsko datoteko `/etc/wsl.conf` in uporabniško `.wslconfig`; Microsoft dokumentira, da spremembe stopijo v veljavo po popolni zaustavitvi in ponovnem zagonu distribucije [[20]](#ref-microsoft-wsl-config).

Za SSH v WSL2 iz Windows poganjaj `sshd` znotraj distribucije in se poveži na njen naslov ali na posredovana vrata. Na sodobnem Windows 11 lahko zrcaljeno omreženje pomeni, da je WSL bolj naravno dosegljiv iz lokalnega omrežja, vendar Microsoft dokumentira tudi požarne zidove za vhodni dostop [[21]](#ref-microsoft-wsl-networking). Za preprosto samo-lokalno postavitev raje uporabi:

```powershell
ssh -p 2222 agent localhost
```

z izrecnim Windows port proxyjem ali pravilom za posredovanje v orodju za virtualke, če localhost posredovanje v ciljni različici Windows/WSL ni samodejno.

### Windows možnost B: Linux VM v Hyper-V

Pravo Linux virtualko uporabi, kadar je obnašanje datotečnega sistema in omrežja v WSL2 preveč povezano z gostiteljem ali kadar želiš posnetke oziroma checkpoint-e z jasnejšo mejo:

```text
Windows gostitelj
+-- Ubuntu virtualka v Hyper-V
    +-- repozitorij kloniran znotraj virtualke
    +-- OpenSSH omogočen
    +-- agentski uporabnik z brezgeselnim sudo
    +-- brez deljenih profilnih map gostitelja
    +-- checkpoint pred vsakim večjim zagonom
```

Poveži se prek SSH, pred vsako agentsko sejo uporabi checkpoint virtualke in oddaljeni repozitorij ohrani kot trajno resnico.

### Windows možnost C: Windows Sandbox za efemerno nativeno delo

Windows Sandbox je uporaben za zavržljive izvorno-Windows smoke teste ali enkratne agentske zagone. Podpira konfiguracijo `.wsb` z omrežjem, mapiranimi mapami in ukazom ob prijavi; mapirane mape so na voljo, še preden se ukaz ob prijavi zažene [[22]](#ref-microsoft-windows-sandbox-config). Okolje je namerno efemerno. Ko se sandbox zapre, izginejo nameščena orodja, uporabniki, gostiteljski ključi OpenSSH, kloni repozitorija in namestitve Build Tools.

Primer `AgentSandbox.wsb`:

```xml
<Configuration>
  <Networking>Enable</Networking>
  <MappedFolders>
    <MappedFolder>
      <HostFolder>C:\agent-sandbox\in</HostFolder>
      <SandboxFolder>C:\agent-in</SandboxFolder>
      <ReadOnly>true</ReadOnly>
    </MappedFolder>
    <MappedFolder>
      <HostFolder>C:\agent-sandbox\out</HostFolder>
      <SandboxFolder>C:\agent-out</SandboxFolder>
      <ReadOnly>false</ReadOnly>
    </MappedFolder>
  </MappedFolders>
  <LogonCommand>
    <Command>powershell.exe -ExecutionPolicy Bypass -File C:\agent-in\bootstrap.ps1</Command>
  </LogonCommand>
  <MemoryInMB>8192</MemoryInMB>
</Configuration>
```

Znotraj `bootstrap.ps1` je mogoče namestiti in zagnati OpenSSH Server z ukazi za opcijske Windows zmožnosti, ki jih dokumentira Microsoft [[23]](#ref-microsoft-openssh-windows):

```powershell
Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0
Start-Service sshd
Set-Service -Name sshd -StartupType Automatic

if (!(Get-NetFirewallRule -Name "OpenSSH-Server-In-TCP" -ErrorAction SilentlyContinue)) {
  New-NetFirewallRule -Name "OpenSSH-Server-In-TCP" `
    -DisplayName "OpenSSH Server (sshd)" `
    -Enabled True `
    -Direction Inbound `
    -Protocol TCP `
    -Action Allow `
    -LocalPort 22
}

ipconfig | Out-File C:\agent-out\sandbox-network.txt
```

V Windows 11 24H2 in novejših lahko CLI za Windows Sandbox našteje sandboxe in poroča o njihovem IP naslovu [[24]](#ref-microsoft-windows-sandbox-cli):

```powershell
wsb list
wsb ip --id <sandbox-id>
```

Tudi Visual Studio Build Tools je mogoče namestiti brez interakcije. Microsoft dokumentira tihe parametre ukazne vrstice, kot so `--quiet`, `--wait` in `--norestart`, ter objavlja identifikatorje workloadov in komponent za Build Tools [[25]](#ref-microsoft-vs-install); [[26]](#ref-microsoft-vs-buildtools):

```powershell
$vsArgs = @(
  "--quiet", "--wait", "--norestart", "--nocache",
  "--installPath", "C:\BuildTools",
  "--add", "Microsoft.VisualStudio.Workload.VCTools",
  "--includeRecommended"
)
Start-Process C:\agent-in\vs_BuildTools.exe -Wait -ArgumentList $vsArgs
```

To je tehnično izvedljivo, vendar počasno, če se pogosto ponavlja. Uporabi ga takrat, ko je ravno efemernost bistvo.

### Windows možnost D: trajna Windows virtualka z OpenSSH

Trajno Windows virtualko uporabi, kadar projekt potrebuje ponavljajoče se izvorno Windows delo: MSVC, Windows SDK-je, COM, PowerShell-only avtomatizacijo, obnašanje Windows storitev ali predpomnilnike Visual Studio Build Tools. Nastavi jo kot pravo agentsko virtualko:

```text
Windows gostitelj ali Linux hipervizor
+-- Windows gostujoča virtualka
    +-- OpenSSH Server omogočen
    +-- namenski lokalni agentski račun
    +-- Visual Studio Build Tools nameščen enkrat
    +-- checkpoint pred delom v visoki avtonomiji
    +-- brez deljenega domačega imenika/profila gostitelja
    +-- repozitorij kloniran znotraj virtualke
```

Ta virtualka je trajna, zato jo obravnavaj kot upravljan razvojni stroj. Posodabljaj jo, snapshotaj, rotiraj poverilnice in jo občasno ponovno zgradi. Upoštevaj tudi licenčno mejo: trajen Windows gost običajno zahteva ustrezno Windows licenco, ločeno od gostitelja ali od pravice do Windows Sandboxa. Microsoftova licenčna navodila ločujejo pravice za virtualizacijo namiznega Windows in pravice VDA od običajnih pravic lokalne namestitve [[27]](#ref-microsoft-windows-licensing). Ta priročnik ne daje pravnega nasveta; pred standardizacijo trajne Windows virtualke preveri licenčni model.

### Linux možnost A: KVM/libvirt virtualka

Na Linux delovni postaji je KVM/libvirt virtualka najčistejša privzeta izbira. Ubuntu dokumentira Virtual Machine Manager kot grafični vmesnik za upravljanje lokalnih in oddaljenih virtualk z orodji, kot so `virt-install`, `virt-clone` in `virt-viewer` [[28]](#ref-ubuntu-virt-manager). Praktična postavitev je:

```bash
sudo apt update
sudo apt install -y qemu-kvm libvirt-daemon-system virt-manager openssh-client
```

Ustvari Ubuntu virtualko, v njej omogoči OpenSSH in se poveži z gostitelja. Za razvoj, omejen na gostitelja, običajno zadošča NAT in SSH. Za dostop iz omrežja uporabi bridge omreženje ali izrecno posredovanje vrat. libvirt dokumentira pogosta modela "virtual network" in "shared physical device", njegov XML format za omrežja pa je avtoritativna referenca za definicije omrežij [[29]](#ref-libvirt-networking); [[30]](#ref-libvirt-network-xml).

### Linux možnost B: Multipass ali LXD virtualka

Za hitrejšo Ubuntu virtualko, naravno za CLI, je Multipass razumna izbira. Canonical opisuje Multipass kot orodje za hitro ustvarjanje Ubuntu virtualk v slogu oblačnih instanc na Linuxu, macOS in Windows [[31]](#ref-canonical-multipass):

```bash
sudo snap install multipass
multipass launch 24.04 --name agent --cpus 6 --memory 12G --disk 80G
multipass shell agent
```

Nato nastavi gostujočega uporabnika, SSH in brezgeselni sudo. LXD virtualke so druga možnost, kadar organizacija že uporablja LXD; Ubuntu dokumentira LXD kot sistem za upravljanje tako sistemskih vsebnikov kot virtualk [[32]](#ref-ubuntu-lxd).

### Linux možnost C: omejen vsebnik za zaupanja vredno delo

Vsebniki so priročni za zaupanja vredne repozitorije, vendar predstavljajo šibkejšo mejo kot virtualka pri neomejenih agentih. Izogibaj se:

```text
--privileged
-v /:/host
-v ~/.ssh:/home/agent/.ssh
-v /var/run/docker.sock:/var/run/docker.sock
--net=host
```

Vsebnik je lahko uporaben za ozke naloge, podobne CI, vendar polni `--yolo` kodirni agent z nameščanjem paketov in poljubnim izvajanjem ukazov sodi v virtualko, razen če sta repozitorij in skripte odvisnosti že zaupanja vredni.

### Linux možnost D: OverlayFS in chroot kot mehanizem ponastavitve

OverlayFS lahko zagotovi hitro plast za ponastavitev datotečnega sistema:

```bash
sudo mkdir -p /srv/agent/base /srv/agent/upper /srv/agent/work /srv/agent/merged

sudo mount -t overlay overlay \
  -o lowerdir=/srv/agent/base,upperdir=/srv/agent/upper,workdir=/srv/agent/work \
  /srv/agent/merged

sudo chroot /srv/agent/merged /bin/bash
```

Dokumentacija Linux jedra opisuje imenike lower, upper, work in merged, ki jih uporablja OverlayFS [[33]](#ref-linux-overlayfs). To je uporabno kot mehanizem ponastavitve, ne pa kot močna varnostna meja za privilegiran avtonomen agent. `systemd-nspawn` je močnejši od golega chroota in uporaben za lahke strojne vsebnike, vendar še vedno ne nadomesti virtualke za nezaupanja vredno delo s polnim dostopom [[34]](#ref-systemd-nspawn).

### macOS možnost A: Lima Ubuntu virtualka

Na macOS uporabi Linux virtualko, namesto da agentu omogočiš dostop do macOS gostitelja. Lima je dobra privzeta izbira za ukazno vrstico. Njena dokumentacija kaže, da so gostiteljevi domači imeniki privzeto montirani samo za branje ter da jih je mogoče izrecno narediti pisljive ali povsem izključiti [[35]](#ref-lima-usage). Za OAP raje uporabi ozek pisljiv share ali pa brez host mounta.

Primer `agent.yaml`:

```yaml
images:
- location: "https://cloud-images.ubuntu.com/releases/24.04/release/ubuntu-24.04-server-cloudimg-arm64.img"
  arch: "aarch64"
- location: "https://cloud-images.ubuntu.com/releases/24.04/release/ubuntu-24.04-server-cloudimg-amd64.img"
  arch: "x86_64"

cpus: 6
memory: "12GiB"
disk: "80GiB"

mounts:
- location: "~"
  writable: false
- location: "/tmp/lima-agent-share"
  writable: true
```

Zaženi in vstopi:

```bash
brew install lima
limactl start ./agent.yaml --name agent
limactl shell agent
```

Lima dokumentira več načinov mountanja gostiteljskega datotečnega sistema, med drugim reverse-sshfs, 9p in virtiofs, odvisno od različice in zaledja virtualke [[36]](#ref-lima-mounts). Te mounte ohrani ozke.

### macOS možnost B: Multipass ali UTM

Multipass je na voljo tudi na macOS in ponuja preprosto Ubuntu virtualko:

```bash
brew install --cask multipass
multipass launch 24.04 --name agent --cpus 6 --memory 12G --disk 80G
multipass shell agent
```

UTM, VMware Fusion ali Parallels uporabi, kadar jih organizacija že standardno uporablja. Načelo OAP ostane enako: agentu ne daj širokega pisalnega dostopa do domačega imenika macOS ali do dolgoživih gostiteljskih poverilnic.

## II.4 Kontrolni seznam pred začetkom

Pred zagonom neomejenega načina delovanja agenta mora biti izvajalec sposoben potrditi vse spodnje točke:

```text
[ ] Agent teče znotraj zavržljive virtualke/distribucije/sandboxa, ne v običajnem računu gostitelja
[ ] Agentski uporabnik je namenski
[ ] Brezgeselni sudo/admin obstaja samo znotraj gosta
[ ] Repozitorij je znotraj gosta ali v ozkem pisljivem mountu
[ ] Domači imenik gostitelja ni montiran z dovoljenjem za pisanje
[ ] Nobeni zasebni SSH ključi gostitelja/produkcije niso montirani ali kopirani v gosta
[ ] Nobene oblačne, kube ali Docker poverilnice gostitelja/produkcije niso v gostu
[ ] Nobene datoteke upravljalnika gesel, profila brskalnika ali produkcijskega `.env` ni v gostu
[ ] Gostujoči lokalni `~/.ssh` je pričakovan pri gostih z dostopom prek SSH
[ ] Gostujoči lokalni `~/.ssh` vsebuje samo gradivo za dostop do virtualke/sandboxa
[ ] `CODEX_HOME` je lokalen za gosta
[ ] Omrežna politika je razumljena
[ ] Snapshot/export/checkpoint obstaja
[ ] Git delovno drevo začne čisto ali z znanim naborom sprememb
[ ] Dnevniki so omogočeni
[ ] Poverilnice, če obstajajo, so kratkožive in z najmanjšimi potrebnimi pravicami
[ ] Agent ne more mergati svojega lastnega PR-ja
[ ] Pot za obnovo je bila vsaj enkrat preizkušena
```

Operativna priprava je lahko kratka, ker OAP ne zahteva popolne izolacije. Zahteva mejo, zaradi katere je pričakovani neuspeh še vedno preživetven. Razumen povzetek je:

> Agent je lahko znotraj gosta zelo zmogljiv, vendar gost ne sme vsebovati ničesar, česar si človek ne more privoščiti izgubiti ali zamenjati.

<Question
  id="oap-preflight-boundary"
  question="Kaj je glavni razlog, da OAP za izvajalnega agenta z visoko avtonomijo daje prednost utrjenemu in obnovljivemu gostujočemu izvajalnemu okolju?"
  options={["Ker gost postane avtoritativni izvor resnice o projektu", "* Ker lahko agent deluje z uporabno avtonomijo znotraj okolja, ki je zavržljivo in ločeno od skrivnosti gostitelja", "Ker znotraj gosta sudo brez gesla nikoli ni potreben", "Ker virtualka zagotavlja, da agent ne more narediti napak"]}
  attempts={2}
>
Meja gosta ni namenjena predpostavki popolne varnosti. Namenjena je omejevanju tveganja, hkrati pa agentu omogoča, da opravi resnično pripravljalno delo, testiranje in implementacijo, ne da bi človeka vlekel v rutinske operacije.
</Question>
