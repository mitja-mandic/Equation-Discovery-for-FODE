# Dodatki

## Dodatek A: Primer strukture `AGENTS.md` / `CLAUDE.md`

```markdown
# AGENTS.md or CLAUDE.md

## Poslanstvo
Ta repozitorij implementira <izdelek>. Ohrani <temeljno obljubo>.

## Povzetek odkrivanja
- Domenski problem:
- Oblika izdelka:
- Izbrana arhitektura:
- Utemeljitev sklada in orodij:
- Zavržene alternative:
- Obseg prve izdaje:
- Eksplicitni necilji:

## Domena
- Domenski strokovnjak:
- Domensko besedišče:
- Domenski delovni tokovi:
- Domenski načini odpovedi:

## Arhitektura
- Zaledje:
- Frontend:
- Baza podatkov:
- Ozadna opravila:
- Zunanje storitve:

## Nepogajljiva pravila
- ...

## Varnost
- Nikoli ne commitaj skrivnosti.
- Nikoli ne beleži surovih poverilnic v dnevnike.
- V dokumentaciji in testih uporabljaj lažne placeholderje.

## Delovni tok
- Ustvari vejo iz trenutne `main`.
- Commitaj samo povezane datoteke.
- Odpri pull request.
- Ne mergaj svojega lastnega PR-ja.

## Lokalna postavitev
- Manjkajoča lokalna orodja nameščaj samo znotraj odobrenega izvajalnega okolja.
- Dokumentiraj pripravljalne ukaze, ki bi morali postati trajno projektno znanje.
- Človeka ne prosi za rutinsko pripravo, razen če to blokira varnostna meja.

## Testi
- Unit:
- Integracija:
- E2E:
- Lint:

## Dokumentacija
- Posodobi dokumentacijo, ko se vedenje spremeni.
- Brez odobritve izdaje ne trdi produkcijske pripravljenosti.

## Končno poročilo
- Veja:
- Commit:
- PR:
- Testi:
- Nameščena lokalna orodja ali odvisnosti:
- Tveganja:
```

## Dodatek B: Predloga prompta za kodirnega agenta

```text
Najprej preberi AGENTS.md in CLAUDE.md, če obstajata oba.

Izhodišče strateškega odkrivanja:
- Kategorija izdelka:
- Arhitekturna odločitev:
- Izbira sklada/orodij:
- Meje zaupanja:
- Zavržene alternative:
- Obseg prve izdaje:

Trenutno stanje:
- ...

Cilj:
- ...

Domensko vedenje:
- ...

Kriteriji sprejema:
- ...

Necilji:
- ...

Datoteke za pregled:
- ...

Implementacijske zahteve:
- ...

Lokalna priprava:
- Znotraj izvajalne virtualke smeš namestiti potrebna lokalna orodja ali odvisnosti.
- Dokumentiraj vse, kar je bilo nameščeno ali konfigurirano.
- Človeka ne prosi za izvajanje pripravljalnih ukazov, razen če to blokira eksplicitna varnostna meja.

Testi:
- ...

Dokumentacija:
- ...

Delovni tok:
- Začni iz trenutne `main`.
- Ustvari funkcionalno vejo.
- Commitaj samo povezane datoteke.
- Pushaj in odpri PR.
- Ne mergaj.

Poročilo:
- Veja, commit, URL PR-ja.
- Povzetek.
- Implementirano domensko vedenje.
- Zagnani testi z natančnimi rezultati.
- Spremenjene datoteke.
- Nameščena lokalna orodja ali odvisnosti.
- Spremenjena dokumentacija.
- Preskočeni testi ali blokade.
- Varnostne potrditve.
```

## Dodatek C: Predloga prompta samo za preverjanje

```text
To je samo preverjanje.

Ne urejaj datotek.
Ne ustvarjaj veje.
Ne commitaj.
Ne odpiraj PR-ja.

Preveri trenutno `main` s temi ukazi:
- ...

Poročilo:
- Preverjeni SHA commita.
- Zagnani ukazi.
- Natančni rezultati uspeh/neuspeh/preskok.
- Okoljske blokade.
- Ali je REZULTAT `OK`, `FAIL` ali `ENVIRONMENT_BLOCKED`.
```

## Dodatek D: Kontrolni seznam pripravljenosti PR-ja

- [ ] Obseg se ujema s promptom.
- [ ] Nobena nepovezana datoteka ni bila spremenjena.
- [ ] Testi so poimenovani in pognani.
- [ ] Preskočeni testi so poročani kot preskočeni.
- [ ] Dokumentacija je posodobljena ali eksplicitno ni potrebna.
- [ ] Nobena skrivnost ni commitana.
- [ ] Noben produkcijski sistem ni bil dotaknjen.
- [ ] CI je zelen ali pa so neuspehi pojasnjeni.
- [ ] Znane omejitve so dokumentirane.
- [ ] Spremembe lokalne priprave so dokumentirane.
- [ ] Strateški povzetek odločitve je pripravljen.
- [ ] Človek, ki odloča o izdaji ali mergu, razume ujemanje s ciljem, dokaze in tveganje.

## Dodatek E: Kontrolni seznam pripravljenosti na izdajo

- [ ] Cilj izdaje je ekspliciten.
- [ ] Kriteriji izdaje so eksplicitni.
- [ ] Obseg funkcionalnosti je dokončan.
- [ ] Negativne poti so testirane.
- [ ] Pokritost integracijskih/E2E testov je ustrezna.
- [ ] Dokumentacija je usklajena.
- [ ] Runbooki so posodobljeni.
- [ ] Varnostni pregled je zaključen.
- [ ] Znane omejitve so javno navedene.
- [ ] Pot za rollback je znana.
- [ ] Končno preverjanje je zaključeno.
- [ ] Strateški povzetek izdaje je pripravljen.
- [ ] Človeška avtoriteta za izdajo sprejema dokaze.

## Dodatek F: Ukazi za operativno pripravo

Ti ukazi so izhodišča. Imena, vrata, CPU, pomnilnik in velikosti diskov prilagodi lokalnemu stroju in projektu.

### Linux gostujoči uporabnik

```bash
sudo adduser agent
sudo usermod -aG sudo agent
sudo visudo -f /etc/sudoers.d/90-agent-nopasswd
```

Dodaj:

```txt
agent ALL=(ALL) NOPASSWD:ALL
```

Preveri:

```bash
sudo chmod 0440 /etc/sudoers.d/90-agent-nopasswd
sudo visudo -c
su - agent
sudo -n true && echo "passwordless sudo works"
```

### Gostujoče lokalno stanje Codexa

```bash
mkdir -p "$HOME/.codex-agent"
export CODEX_HOME="$HOME/.codex-agent"
```

### Namestitev WSL2 Ubuntu

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
mkdir -p ~/work
```

### Izhodišče za utrditev WSL2

`/etc/wsl.conf`:

```ini
[automount]
enabled=false

[interop]
enabled=false
appendWindowsPath=false

[user]
default=agent
```

Restart WSL:

```powershell
wsl --shutdown
```

### Linux OpenSSH znotraj gosta

```bash
sudo apt update
sudo apt install -y openssh-server
sudo systemctl enable --now ssh || sudo service ssh start
mkdir -p ~/.ssh
chmod 700 ~/.ssh
```

### Windows Sandbox OpenSSH začetna postavitev

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
```

### Začetna postavitev Visual Studio Build Tools

```powershell
$vsArgs = @(
  "--quiet", "--wait", "--norestart", "--nocache",
  "--installPath", "C:\BuildTools",
  "--add", "Microsoft.VisualStudio.Workload.VCTools",
  "--includeRecommended"
)
Start-Process C:\agent-in\vs_BuildTools.exe -Wait -ArgumentList $vsArgs
```

### Multipass Ubuntu virtualka

```bash
sudo snap install multipass
multipass launch 24.04 --name agent --cpus 6 --memory 12G --disk 80G
multipass shell agent
```

### Lima Ubuntu virtualka

```bash
brew install lima
limactl start ./agent.yaml --name agent
limactl shell agent
```

### Ponastavitveni sloj OverlayFS

```bash
sudo mkdir -p /srv/agent/base /srv/agent/upper /srv/agent/work /srv/agent/merged

sudo mount -t overlay overlay \
  -o lowerdir=/srv/agent/base,upperdir=/srv/agent/upper,workdir=/srv/agent/work \
  /srv/agent/merged

sudo chroot /srv/agent/merged /bin/bash
```

## Dodatek G: Reference

Ta dodatek rekonstruira bibliografijo iz lokalne datoteke `references.bib`, ki je spremljala izvorni rokopis. Vgrajeni Pandoc ključi za citiranje so bili pretvorjeni v klikljive, Notes-native reference, ki kažejo sem.

### Ref codex-agents-md

[1] OpenAI. *Custom instructions with AGENTS.md*. OpenAI Developers. 2026.  
URL: [https://developers.openai.com/codex/guides/agents-md](https://developers.openai.com/codex/guides/agents-md)  
Accessed: 2026-06-14

### Ref hula

[2] Takerngsaksiri, Wannita and others. *Human-In-the-Loop Software Development Agents*. 2024.  
URL: [https://arxiv.org/abs/2411.12924](https://arxiv.org/abs/2411.12924)

### Ref metagpt

[3] MetaGPT. *MetaGPT GitHub repository*. 2026.  
URL: [https://github.com/geekan/MetaGPT](https://github.com/geekan/MetaGPT)  
Accessed: 2026-06-14

### Ref chatdev

[4] OpenBMB. *ChatDev GitHub repository*. 2026.  
URL: [https://github.com/OpenBMB/ChatDev](https://github.com/OpenBMB/ChatDev)  
Accessed: 2026-06-14

### Ref ko-euse-2011

[5] Ko, Andrew J. and Abraham, Robin and Beckwith, Laura and Blackwell, Alan and Burnett, Margaret and Erwig, Martin and Scaffidi, Christopher and Lawrance, Joseph and Lieberman, Henry and Myers, Brad and Rosson, Mary Beth and Rothermel, Gregg and Shaw, Mary and Wiedenbeck, Susan. *The State of the Art in End-User Software Engineering*. ACM Computing Surveys. 2011.  
DOI: [10.1145/1922649.1922658](https://doi.org/10.1145/1922649.1922658)  
URL: [https://faculty.washington.edu/ajko/papers/Ko2011EndUserSoftwareEngineering.pdf](https://faculty.washington.edu/ajko/papers/Ko2011EndUserSoftwareEngineering.pdf)

### Ref schenkenfelder-lowcode-eud-2024

[6] Schenkenfelder, Bernhard and Brandstätter, Ulrich and Kirchtag, Harald and Wimmer, Manuel. *Low-Code Development and End-User Development: (How) Are They Different?*. Proceedings of the First International Workshop on Participatory Design and End-User Development - Building Bridges. 2024.  
URL: [https://ceur-ws.org/Vol-3778/short5.pdf](https://ceur-ws.org/Vol-3778/short5.pdf)

### Ref weber-ai-eud-2025

[7] Weber, Irene. *Feasibility of AI-Assisted Programming for End-User Development*. 2025.  
DOI: [10.48550/arXiv.2512.05666](https://doi.org/10.48550/arXiv.2512.05666)  
URL: [https://arxiv.org/abs/2512.05666](https://arxiv.org/abs/2512.05666)

### Ref mit-ai-citizen-dev-2024

[8] Davenport, Thomas H. and Barkin, Ian. *How AI-Empowered Citizen Developers Help Drive Digital Transformation*. MIT Sloan. 2024.  
URL: [https://mitsloan.mit.edu/ideas-made-to-matter/how-ai-empowered-citizen-developers-help-drive-digital-transformation](https://mitsloan.mit.edu/ideas-made-to-matter/how-ai-empowered-citizen-developers-help-drive-digital-transformation)  
Accessed: 2026-06-14

### Ref github-copilot

[9] GitHub. *GitHub Copilot*. 2026.  
URL: [https://github.com/features/copilot](https://github.com/features/copilot)  
Accessed: 2026-06-14

### Ref copilot-productivity

[10] Peng, Sida and Kalliamvakou, Eirini and Cihon, Peter and Demirer, Mert. *The Impact of AI on Developer Productivity: Evidence from GitHub Copilot*. 2023.  
URL: [https://arxiv.org/abs/2302.06590](https://arxiv.org/abs/2302.06590)

### Ref swebench-paper

[11] Jimenez, Carlos E. and Yang, John and Wettig, Alexander and Yao, Shunyu and Pei, Kexin and Press, Ofir and Narasimhan, Karthik. *SWE-bench: Can Language Models Resolve Real-World GitHub Issues?*. 2023.  
URL: [https://arxiv.org/abs/2310.06770](https://arxiv.org/abs/2310.06770)

### Ref swebench-repo

[12] SWE-bench. *SWE-bench GitHub repository*. 2026.  
URL: [https://github.com/SWE-bench/SWE-bench](https://github.com/SWE-bench/SWE-bench)  
Accessed: 2026-06-14

### Ref sweagent-paper

[13] Yang, John and Jimenez, Carlos E. and Wettig, Alexander and Lieret, Kilian and Yao, Shunyu and Narasimhan, Karthik and Press, Ofir. *SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering*. 2024.  
URL: [https://arxiv.org/abs/2405.15793](https://arxiv.org/abs/2405.15793)

### Ref sweagent-repo

[14] SWE-agent. *SWE-agent GitHub repository*. 2026.  
URL: [https://github.com/SWE-agent/SWE-agent](https://github.com/SWE-agent/SWE-agent)  
Accessed: 2026-06-14

### Ref codex-security

[15] OpenAI. *Agent approvals and security*. OpenAI Developers. 2026.  
URL: [https://developers.openai.com/codex/agent-approvals-security](https://developers.openai.com/codex/agent-approvals-security)  
Accessed: 2026-06-14

### Ref claude-code-cli-reference

[16] Anthropic. *Claude Code CLI reference*. 2026.  
URL: [https://code.claude.com/docs/en/cli-reference](https://code.claude.com/docs/en/cli-reference)  
Accessed: 2026-06-14

### Ref codex-cli-reference

[17] OpenAI. *Codex CLI command reference*. OpenAI Developers. 2026.  
URL: [https://developers.openai.com/codex/cli/reference](https://developers.openai.com/codex/cli/reference)  
Accessed: 2026-06-14

### Ref microsoft-wsl-install

[18] Microsoft. *Install WSL*. Microsoft Learn. 2026.  
URL: [https://learn.microsoft.com/en-us/windows/wsl/install](https://learn.microsoft.com/en-us/windows/wsl/install)  
Accessed: 2026-06-14

### Ref microsoft-wsl-filesystems

[19] Microsoft. *Working across Windows and Linux file systems*. Microsoft Learn. 2026.  
URL: [https://learn.microsoft.com/en-us/windows/wsl/filesystems](https://learn.microsoft.com/en-us/windows/wsl/filesystems)  
Accessed: 2026-06-14

### Ref microsoft-wsl-config

[20] Microsoft. *Advanced settings configuration in WSL*. Microsoft Learn. 2026.  
URL: [https://learn.microsoft.com/en-us/windows/wsl/wsl-config](https://learn.microsoft.com/en-us/windows/wsl/wsl-config)  
Accessed: 2026-06-14

### Ref microsoft-wsl-networking

[21] Microsoft. *Accessing network applications with WSL*. Microsoft Learn. 2026.  
URL: [https://learn.microsoft.com/en-us/windows/wsl/networking](https://learn.microsoft.com/en-us/windows/wsl/networking)  
Accessed: 2026-06-14

### Ref microsoft-windows-sandbox-config

[22] Microsoft. *Use and configure Windows Sandbox*. Microsoft Learn. 2026.  
URL: [https://learn.microsoft.com/en-us/windows/security/application-security/application-isolation/windows-sandbox/windows-sandbox-configure-using-wsb-file](https://learn.microsoft.com/en-us/windows/security/application-security/application-isolation/windows-sandbox/windows-sandbox-configure-using-wsb-file)  
Accessed: 2026-06-14

### Ref microsoft-openssh-windows

[23] Microsoft. *Get started with OpenSSH Server for Windows*. Microsoft Learn. 2026.  
URL: [https://learn.microsoft.com/en-us/windows-server/administration/openssh/openssh_install_firstuse](https://learn.microsoft.com/en-us/windows-server/administration/openssh/openssh_install_firstuse)  
Accessed: 2026-06-14

### Ref microsoft-windows-sandbox-cli

[24] Microsoft. *Windows Sandbox command line interface*. Microsoft Learn. 2026.  
URL: [https://learn.microsoft.com/en-us/windows/security/application-security/application-isolation/windows-sandbox/windows-sandbox-cli](https://learn.microsoft.com/en-us/windows/security/application-security/application-isolation/windows-sandbox/windows-sandbox-cli)  
Accessed: 2026-06-14

### Ref microsoft-vs-install

[25] Microsoft. *Use command-line parameters to install Visual Studio*. Microsoft Learn. 2026.  
URL: [https://learn.microsoft.com/en-us/visualstudio/install/use-command-line-parameters-to-install-visual-studio](https://learn.microsoft.com/en-us/visualstudio/install/use-command-line-parameters-to-install-visual-studio)  
Accessed: 2026-06-14

### Ref microsoft-vs-buildtools

[26] Microsoft. *Visual Studio Build Tools workload and component IDs*. Microsoft Learn. 2026.  
URL: [https://learn.microsoft.com/en-us/visualstudio/install/workload-component-id-vs-build-tools](https://learn.microsoft.com/en-us/visualstudio/install/workload-component-id-vs-build-tools)  
Accessed: 2026-06-14

### Ref microsoft-windows-licensing

[27] Microsoft. *Windows Commercial Licensing Overview*. Microsoft Learn. 2026.  
URL: [https://learn.microsoft.com/en-us/windows/whats-new/windows-licensing](https://learn.microsoft.com/en-us/windows/whats-new/windows-licensing)  
Accessed: 2026-06-14

### Ref ubuntu-virt-manager

[28] Canonical. *Virtual Machine Manager*. Ubuntu Server documentation. 2026.  
URL: [https://ubuntu.com/server/docs/how-to/virtualisation/virtual-machine-manager/](https://ubuntu.com/server/docs/how-to/virtualisation/virtual-machine-manager/)  
Accessed: 2026-06-14

### Ref libvirt-networking

[29] libvirt. *NAT forwarding and virtual networks*. 2026.  
URL: [https://wiki.libvirt.org/Networking.html](https://wiki.libvirt.org/Networking.html)  
Accessed: 2026-06-14

### Ref libvirt-network-xml

[30] libvirt. *Network XML format*. 2026.  
URL: [https://libvirt.org/formatnetwork.html](https://libvirt.org/formatnetwork.html)  
Accessed: 2026-06-14

### Ref canonical-multipass

[31] Canonical. *Multipass documentation*. 2026.  
URL: [https://documentation.ubuntu.com/multipass/](https://documentation.ubuntu.com/multipass/)  
Accessed: 2026-06-14

### Ref ubuntu-lxd

[32] Canonical. *LXD containers and virtual machines*. Ubuntu Server documentation. 2026.  
URL: [https://ubuntu.com/server/docs/how-to/virtualisation/lxd/](https://ubuntu.com/server/docs/how-to/virtualisation/lxd/)  
Accessed: 2026-06-14

### Ref linux-overlayfs

[33] Linux Kernel Documentation. *Overlay Filesystem*. 2026.  
URL: [https://docs.kernel.org/filesystems/overlayfs.html](https://docs.kernel.org/filesystems/overlayfs.html)  
Accessed: 2026-06-14

### Ref systemd-nspawn

[34] freedesktop.org. *systemd-nspawn*. 2026.  
URL: [https://www.freedesktop.org/software/systemd/man/latest/systemd-nspawn.html](https://www.freedesktop.org/software/systemd/man/latest/systemd-nspawn.html)  
Accessed: 2026-06-14

### Ref lima-usage

[35] Lima. *Lima usage*. 2026.  
URL: [https://lima-vm.io/docs/usage/](https://lima-vm.io/docs/usage/)  
Accessed: 2026-06-14

### Ref lima-mounts

[36] Lima. *Filesystem mounts*. 2026.  
URL: [https://lima-vm.io/docs/config/mount/](https://lima-vm.io/docs/config/mount/)  
Accessed: 2026-06-14

### Ref slaif-repo

[37] UL-FE LMI. *SLAIF API Gateway GitHub repository*. 2026.  
URL: [https://github.com/ulfe-lmi/slaif-api-gateway](https://github.com/ulfe-lmi/slaif-api-gateway)  
Accessed: 2026-06-14

### Ref claude-code-memory

[38] Anthropic. *How Claude remembers your project*. 2026.  
URL: [https://code.claude.com/docs/en/memory](https://code.claude.com/docs/en/memory)  
Accessed: 2026-06-14

### Ref github-copilot-agent

[39] GitHub Docs. *About GitHub Copilot coding agent*. 2026.  
URL: [https://docs.github.com/en/copilot/concepts/agents/cloud-agent/about-cloud-agent](https://docs.github.com/en/copilot/concepts/agents/cloud-agent/about-cloud-agent)  
Accessed: 2026-06-14

### Ref cursor

[40] Cursor. *Cursor*. 2026.  
URL: [https://cursor.com/](https://cursor.com/)  
Accessed: 2026-06-14

### Ref codex-best-practices

[41] OpenAI. *Codex best practices*. OpenAI Developers. 2026.  
URL: [https://developers.openai.com/codex/learn/best-practices](https://developers.openai.com/codex/learn/best-practices)  
Accessed: 2026-06-14

### Ref codex-github

[42] OpenAI. *Codex code review in GitHub*. OpenAI Developers. 2026.  
URL: [https://developers.openai.com/codex/integrations/github](https://developers.openai.com/codex/integrations/github)  
Accessed: 2026-06-14

### Ref slaif-reviews-archive

[43] UL-FE LMI. *SLAIF API Gateway external review archive*. 2026.  
URL: [https://github.com/ulfe-lmi/slaif-api-gateway/tree/main/docs/security/reviews](https://github.com/ulfe-lmi/slaif-api-gateway/tree/main/docs/security/reviews)  
Accessed: 2026-06-14

### Ref slaif-remediation-matrix

[44] UL-FE LMI. *SLAIF API Gateway review remediation matrix*. 2026.  
URL: [https://github.com/ulfe-lmi/slaif-api-gateway/blob/main/docs/security/reviews/remediation-matrix.md](https://github.com/ulfe-lmi/slaif-api-gateway/blob/main/docs/security/reviews/remediation-matrix.md)  
Accessed: 2026-06-14

### Ref slaif-review6

[45] UL-FE LMI. *External Project Quality Review 6.0 / RC1*. 2026.  
URL: [https://github.com/ulfe-lmi/slaif-api-gateway/blob/main/docs/security/reviews/2026-05-review-6.0-rc1.md](https://github.com/ulfe-lmi/slaif-api-gateway/blob/main/docs/security/reviews/2026-05-review-6.0-rc1.md)  
Accessed: 2026-06-14

### Ref dhcp-web-interface-repo

[46] UL-FE LMI. *Managed DHCP/IPAM Edge Appliance GitHub repository*. 2026.  
URL: [https://github.com/ulfe-lmi/dhcp-web-interface](https://github.com/ulfe-lmi/dhcp-web-interface)  
Accessed: 2026-06-14

### Ref slaif-connect-repo

[47] UL-FE LMI. *SLAIF Connect GitHub repository*. 2026.  
URL: [https://github.com/ulfe-lmi/slaif-connect](https://github.com/ulfe-lmi/slaif-connect)  
Accessed: 2026-06-14

### Ref package-hallucination

[48] Lanyado, Bar and others. *We Have a Package for You! A Comprehensive Analysis of Package Hallucinations by Code Generating LLMs*. 2024.  
URL: [https://arxiv.org/abs/2406.10279](https://arxiv.org/abs/2406.10279)

### Ref microsoft-windows-sandbox

[49] Microsoft. *Windows Sandbox*. Microsoft Learn. 2026.  
URL: [https://learn.microsoft.com/en-us/windows/security/application-security/application-isolation/windows-sandbox/](https://learn.microsoft.com/en-us/windows/security/application-security/application-isolation/windows-sandbox/)  
Accessed: 2026-06-14

## Dodatek H: Pojmovnik

**Agentsko programsko inženirstvo:** Razvoj programske opreme z uporabo UI-sistemov, ki znajo načrtovati, uporabljati orodja, urejati repozitorije, poganjati ukaze in iterirati.

**Izvajalni agent:** Kodirni agent, ki upravlja repozitorij in strojno okolje.

**Strateška UI:** Zmogljiv dolgokontekstni model, uporabljen za načrtovanje, arhitekturo, kritiko, generiranje delovnih nalogov, stiskanje dokazov in podporo odločanju za človeka.

**Strateška kontrolna ravnina:** Plast OAP, v kateri se sintetizirajo človeški namen, projektni kontekst, poročila agentov, dokazi in naslednji delovni nalogi.

**Orkestrator domenskega strokovnjaka:** Človeški vodja, katerega glavna avtoriteta izhaja iz domenskega znanja in ne iz koderske ekspertize ter ki prek strateške UI upravlja cilje, kriterije sprejema, tveganje in izdajo.

**Domenska resnica:** Delovni tok v resničnem svetu, omejitve, besedišče, potrebe uporabnikov, tveganja in kriteriji uspeha, ki jih mora programska oprema ohraniti.

**Projektna konstitucija:** Trajna repozitorijska navodila, ki določajo pravila za agente.

**Validacijski dolg:** Breme preverjanja, ki nastane, ko se generirana koda pojavlja hitreje, kot jo je mogoče pregledati.

**Izvajalno okolje visoke avtonomije:** Agentsko okolje s široko sposobnostjo izvajanja ukazov in spreminjanja datotek, omejeno z virtualko, vsebnikom, sandboxom, poverilnicami in delovnim tokom.

**Obnovljiva izvajalna virtualka:** Utrjeno zavržljivo okolje, v katerem sme agent nameščati orodja in poganjati teste, ker trajna projektna resnica živi zunaj virtualke.

**Delegiranje v velikosti PR-ja:** Delovna enota, omejena tako, da je mogoče rezultat pregledati kot en koherenten pull request.

**Povzetek odločitve:** Kratek strateški povzetek, ki vsebuje priporočilo, ujemanje s ciljem, dokaze, tveganje in zahtevano človeško odločitev.

**Inverzija nadzora:** Način odpovedi, pri katerem izvajalni agent začne človeka usmerjati skozi nizkoravensko pripravo ali odpravljanje napak.

# Zahvala

Zahvaljujemo se za podporo Evropske komisije oziroma EuroHPC JU ter slovenskega ministrstva HESI v okviru projekta SLAIF (številka pogodbe 101254461).
