# Part II: Operational Preflight

## II.1 Runtime Design Principles

The execution agent's autonomy is not only a prompt choice. It is a runtime design decision. OAP can use cautious approval modes, but its most distinctive form uses a high-autonomy coding agent in a dedicated VM or similarly bounded machine environment. The VM is not trusted because the agent is harmless. It is trusted because it is hardened, isolated, reconstructable, and not the source of project truth.

<ExpandingSideImg
  src="../assets/fig-06-runtime-boundary.svg"
  alt="High autonomy belongs inside a deliberate runtime boundary."
  caption="High autonomy belongs inside a deliberate runtime boundary."
/>

### Why runtime matters

An agent that can edit files but cannot run tests is a code generator with extra steps. An agent that can run commands, install dependencies, start services, run migrations against test databases, inspect logs, and open pull requests can replace a large share of human implementation labor.

That power must be contained. The runtime should be designed so that the agent can be effective without being near production secrets or production data.

The runtime must also protect human time. A modern coding agent can attempt many edits, test runs, package installations, and repairs in the time a human spends reading one dependency error. If the agent is blocked by every missing tool, the human becomes the slow actuator in the system. The workflow then stops being OAP and becomes AI-directed human labor.

<Sidenote>
Runtime design is not just a security topic in this manual. It is also a management design choice: the boundary should absorb routine setup work so that the human stays at the decision layer.
</Sidenote>

### Privilege as an efficiency boundary

High privilege is often treated only as a security problem. In OAP it is also an efficiency boundary. The question is not "how little can the agent do?" The question is "what can the agent do inside a space that we are willing to throw away?"

If the strategic AI decides that the execution agent should use a new testing library, browser runner, database extension, compiler, package manager, or migration tool, the execution agent should normally install and configure it inside the execution VM. The agent should document the commands and commit durable project changes. It should not require the human to chase dependencies manually unless the action crosses a deliberate safety boundary.

This distinction matters because dependency work is precisely the kind of low-level labor OAP is meant to remove from the human. A missing native library, Docker permission, Playwright browser, Python wheel, Node package, or database fixture can consume hours. Those hours are poor use of the human lead if the work can happen in a disposable VM.

The preferred design is therefore:

- high privilege inside the execution VM;
- no production secrets inside the execution VM;
- no irreplaceable data inside the execution VM;
- remote repository and PRs as durable truth;
- setup commands documented by the agent;
- ability to rebuild the VM from the repository and setup notes;
- ability to abandon a broken VM without losing project state.

If the agent destroys the VM, the failure is operational noise. If the human spends hours doing dependency work for the agent, the control loop has inverted.

### The bounded high-autonomy pattern

The core pattern is:

1. Use a dedicated VM, container, devcontainer, or cloud sandbox.
2. Put only the intended repository and test fixtures inside it.
3. Give the agent enough permission to install, build, test, and run local services.
4. Keep production credentials out.
5. Use separate test databases and disposable services.
6. Make all changes visible through version control.
7. Require pull requests rather than direct main changes.
8. Treat the remote repository, not the VM, as the source of truth.

This allows a high-autonomy mode to be useful without pretending it is harmless. Codex documentation identifies `--dangerously-bypass-approvals-and-sandbox`, also known as `--yolo`, as dangerous full access: no sandbox and no approvals [[15]](#ref-codex-security). Claude Code documents the equivalent high-autonomy permission-bypass mode as `--dangerously-skip-permissions`, equivalent to `--permission-mode bypassPermissions` [[16]](#ref-claude-code-cli-reference). OAP can use that kind of mode only when the outer machine boundary is the safety mechanism.

### No sudo password versus no boundary

The phrase "without sudo password" can mean two different things:

- the agent has no way to elevate and is constrained by the user account;
- the agent can run passwordless `sudo` for selected commands or broad administrative actions.

OAP should make this explicit. A good execution VM may allow passwordless access to local test setup commands, package installation, Docker for disposable services, browser dependencies, or database fixture creation. A bad execution VM gives broad root power near production data or valuable personal files.

The correct question is not "does the agent have sudo?" The correct questions are:

- What can the agent destroy?
- What secrets can it read?
- What networks can it reach?
- What persistent systems can it mutate?
- Can every change be reverted?
- Can every external effect be audited?
- Can the VM be rebuilt if it is damaged?
- Is the agent asking the human to do work it should be able to do safely inside the VM?

### Runtime checklist

Before high-autonomy execution, verify:

- The repository is under version control.
- The agent starts from a clean working tree or reports existing changes.
- Production secrets are absent.
- Test secrets are clearly fake or disposable.
- Databases are test databases.
- External APIs are mocked unless explicitly required.
- Network access is deliberate.
- Package installation policy is clear.
- Docker or service permissions are understood.
- VM rebuild steps are documented.
- The remote repository and PRs contain durable project truth.
- The agent cannot push directly to protected branches.
- The final output must be a branch and PR, not an untracked local mutation.

### Runtime anti-patterns

Avoid:

- running a high-autonomy agent on a developer laptop full of unrelated secrets;
- allowing access to production databases;
- giving an agent cloud credentials with broad permissions;
- letting the agent change CI secrets;
- letting the agent merge its own PR;
- forcing the agent to ask the human for routine dependency installation;
- accepting "tests passed" without command output or CI confirmation;
- running high autonomy in a folder that is not version-controlled.

High autonomy is not unsafe because it is high autonomy. It is unsafe when the surrounding system assumes the agent will behave like a careful human, or when the runtime contains assets that should never have been inside the blast radius. In a well-designed OAP runtime, the agent can be powerful because the environment is disposable and the durable state is elsewhere.

## II.2 Baseline Agent VM Setup

Operational preflight is the work done before the execution agent receives a coding task. It answers one question: can the agent run with enough power to be useful without being able to damage the human's workstation, host home directory, or long-lived credentials?

This is not a hostile-malware containment problem. OAP does not assume that coding agents are malicious. It assumes that autonomous command execution can be wrong, over-broad, confused by repository instructions, or pushed into unsafe paths by dependency scripts. The reasonable target is:

- the agent can install tools and run tests inside its own environment;
- the agent cannot read or overwrite the human's normal home directory;
- the agent cannot reach long-lived SSH, cloud, browser, password-manager, or production credentials;
- the agent can be reset cheaply;
- durable work lives in Git, not in the disposable machine.

For terminal coding agents, this matters most when using full-access or permission-bypass modes. Codex documents `--dangerously-bypass-approvals-and-sandbox`, also aliased as `--yolo`, as running commands without approvals or sandboxing and says it should be used only inside an externally hardened environment [[17]](#ref-codex-cli-reference). Claude Code documents `--dangerously-skip-permissions` as skipping permission prompts and equivalent to `--permission-mode bypassPermissions` [[16]](#ref-claude-code-cli-reference). The OAP answer is to put the hard boundary outside the CLI agent: the guest machine, distro, sandbox, or VM is the safety boundary.

### Linux guest baseline

Use this pattern inside a disposable Ubuntu VM, imported WSL2 distro, Lima VM, Multipass VM, Hyper-V Linux VM, or similar guest:

```bash
sudo adduser agent
sudo usermod -aG sudo agent
sudo visudo -f /etc/sudoers.d/90-agent-nopasswd
```

Add:

```txt
agent ALL=(ALL) NOPASSWD:ALL
```

Then verify:

```bash
sudo chmod 0440 /etc/sudoers.d/90-agent-nopasswd
sudo visudo -c
su - agent
sudo -n true && echo "passwordless sudo works"
```

Keep agent state guest-local:

```bash
mkdir -p "$HOME/.codex-agent"
export CODEX_HOME="$HOME/.codex-agent"
mkdir -p "$HOME/.claude-agent"
export CLAUDE_CONFIG_DIR="$HOME/.claude-agent"
```

For a high-autonomy Codex CLI run inside this guest:

```bash
cd ~/work/project
codex --yolo
```

The equivalent long Codex CLI form is:

```bash
codex --dangerously-bypass-approvals-and-sandbox
```

For the same execution role with Claude Code CLI:

```bash
cd ~/work/project
claude --dangerously-skip-permissions
```

The equivalent Claude Code CLI setting form is:

```bash
claude --permission-mode bypassPermissions
```

The repository should be cloned into the guest filesystem or into a narrow project mount. Do not mount the host home directory writable. Do not mount host SSH keys, cloud credential directories, browser profiles, password-manager files, Docker socket, or production `.env` files. A guest-local `~/.ssh/authorized_keys` file for inbound access is fine; host private keys and production SSH credentials are not.

### SSH access to the guest

For SSH-in workflows, install OpenSSH inside the guest and connect from the host:

```bash
sudo apt update
sudo apt install -y openssh-server
sudo systemctl enable --now ssh || sudo service ssh start
mkdir -p ~/.ssh
chmod 700 ~/.ssh
```

Then add the host public key to `~/.ssh/authorized_keys` inside the guest. Prefer SSH key login over passwords. For a local VM, bind forwarded ports to localhost when possible:

```text
host localhost:2222 -> guest port 22
```

The SSH boundary is a convenience boundary, not the security boundary. The security boundary is still the guest isolation, mounted filesystem policy, and absence of host secrets. In an SSH-in VM or sandbox, `~/.ssh` will normally exist. Its existence is not a preflight failure; copied host identities, production private keys, agent forwarding into the guest, or broad credential mounts are the failure.

### Snapshot and reset

The preflight is incomplete until reset is cheap:

```text
before run:
  snapshot/export/checkpoint the guest

after broken run:
  destroy or revert the guest

after useful run:
  preserve only Git commits, PRs, logs, and documented setup changes
```

If the environment takes hours to reconstruct, humans will be tempted to preserve it as an irreplaceable workstation. OAP environments should instead be managed as replaceable runtime units: valuable when working, rebuildable when damaged.

## II.3 Platform Recipes

The following recipes are starting points, not compliance requirements. Choose the weakest setup that protects host data and still lets the agent do real work. The default recommendation is a per-project Linux VM or WSL2 distro for Linux-oriented work, and a persistent Windows VM only when native Windows toolchains are required.

<ExpandingSideImg
  src="../assets/fig-07-preflight-platforms.svg"
  alt="Operational preflight platform choices."
  caption="Operational preflight platform choices."
/>

### Windows option A: WSL2 Ubuntu per project

WSL2 is a convenient Windows-hosted Linux environment. Microsoft documents `wsl --install` as the default installation path and notes that new installs use WSL2 by default [[18]](#ref-microsoft-wsl-install). For coding-agent work:

```powershell
wsl --install -d Ubuntu
wsl -l -v
wsl --set-version Ubuntu 2
```

Inside Ubuntu:

```bash
sudo apt update
sudo apt upgrade -y
sudo apt install -y build-essential git curl wget unzip zip ca-certificates openssh-server
```

Store Linux projects in the Linux filesystem, not under `/mnt/c`, because Microsoft recommends keeping Linux-command-line projects in the WSL filesystem for performance [[19]](#ref-microsoft-wsl-filesystems):

```bash
mkdir -p ~/work
cd ~/work
git clone <repo-url>
```

For a hardened agent distro, reduce accidental host coupling in `/etc/wsl.conf`:

```ini
[automount]
enabled=false

[interop]
enabled=false
appendWindowsPath=false

[user]
default=agent
```

WSL settings are split between per-distribution `/etc/wsl.conf` and user-level `.wslconfig`; Microsoft documents that changes apply after the distribution fully stops and restarts [[20]](#ref-microsoft-wsl-config).

To SSH into WSL2 from Windows, run `sshd` in the distro and connect to the distro address or to a forwarded port. On current Windows 11, mirrored networking can make WSL reachable more naturally from the local network, but Microsoft documents firewall considerations for inbound access [[21]](#ref-microsoft-wsl-networking). For a simple local-only setup, prefer:

```powershell
ssh -p 2222 agent localhost
```

with an explicit Windows port proxy or VM tool forwarding rule if localhost forwarding is not automatic in the target Windows/WSL version.

### Windows option B: Hyper-V Linux VM

Use a real Linux VM when WSL2 filesystem and networking behavior is too coupled to the host, or when you want snapshots/checkpoints with a clearer boundary:

```text
Windows host
+-- Hyper-V Ubuntu VM
    +-- repo cloned inside VM
    +-- OpenSSH enabled
    +-- agent user with passwordless sudo
    +-- no host profile shares
    +-- checkpoint before each major run
```

Connect over SSH, use a VM checkpoint before each agent session, and keep the repository remote as the durable truth.

### Windows option C: Windows Sandbox for ephemeral native work

Windows Sandbox is useful for disposable native-Windows smoke tests or one-off agent runs. It supports `.wsb` configuration with networking, mapped folders, and a logon command; mapped folders are available before the logon command runs [[22]](#ref-microsoft-windows-sandbox-config). It is deliberately ephemeral. When the sandbox closes, installed tools, users, OpenSSH host keys, repository clones, and Build Tools installations are gone.

Example `AgentSandbox.wsb`:

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

Inside `bootstrap.ps1`, OpenSSH Server can be installed and started with the Windows optional capability commands documented by Microsoft [[23]](#ref-microsoft-openssh-windows):

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

On Windows 11 24H2 and later, the Windows Sandbox CLI can list sandboxes and report a sandbox IP [[24]](#ref-microsoft-windows-sandbox-cli):

```powershell
wsb list
wsb ip --id <sandbox-id>
```

Visual Studio Build Tools can also be installed non-interactively. Microsoft documents quiet command-line installation parameters such as `--quiet`, `--wait`, and `--norestart`, and publishes Build Tools workload/component IDs [[25]](#ref-microsoft-vs-install); [[26]](#ref-microsoft-vs-buildtools):

```powershell
$vsArgs = @(
  "--quiet", "--wait", "--norestart", "--nocache",
  "--installPath", "C:\BuildTools",
  "--add", "Microsoft.VisualStudio.Workload.VCTools",
  "--includeRecommended"
)
Start-Process C:\agent-in\vs_BuildTools.exe -Wait -ArgumentList $vsArgs
```

This is technically workable, but slow if repeated often. Use it when ephemerality is the point.

### Windows option D: persistent Windows VM with OpenSSH

Use a persistent Windows VM when the project needs repeated native Windows work: MSVC, Windows SDKs, COM, PowerShell-only automation, Windows service behavior, or Visual Studio Build Tools caches. Configure it like a real agent VM:

```text
Windows host or Linux hypervisor
+-- Windows guest VM
    +-- OpenSSH Server enabled
    +-- dedicated local agent account
    +-- Visual Studio Build Tools installed once
    +-- checkpoint before high-autonomy work
    +-- no host home/profile share
    +-- repository cloned inside the VM
```

This VM is persistent, so treat it as a managed development machine. Patch it, snapshot it, rotate credentials, and periodically rebuild it. Also note the licensing boundary: a persistent Windows guest normally requires appropriate Windows licensing separate from the host or from Windows Sandbox entitlement. Microsoft licensing guidance distinguishes Windows desktop virtualization and VDA access rights from ordinary local installation rights [[27]](#ref-microsoft-windows-licensing). This manual does not give legal advice; verify the licensing model before standardizing a persistent Windows VM.

### Linux option A: KVM/libvirt VM

On a Linux workstation, a KVM/libvirt VM is the cleanest default. Ubuntu documents Virtual Machine Manager as a GUI for managing local and remote VMs using tools such as `virt-install`, `virt-clone`, and `virt-viewer` [[28]](#ref-ubuntu-virt-manager). A practical setup is:

```bash
sudo apt update
sudo apt install -y qemu-kvm libvirt-daemon-system virt-manager openssh-client
```

Create an Ubuntu VM, enable OpenSSH inside it, and connect from the host. For host-only development, NAT plus SSH is usually enough. For LAN access, use bridged networking or explicit port forwarding. libvirt documents the common "virtual network" and "shared physical device" models, and its network XML format is the authoritative reference for network definitions [[29]](#ref-libvirt-networking); [[30]](#ref-libvirt-network-xml).

### Linux option B: Multipass or LXD VM

For a faster CLI-native Ubuntu VM, Multipass is reasonable. Canonical describes Multipass as a tool for quickly generating cloud-style Ubuntu VMs on Linux, macOS, and Windows [[31]](#ref-canonical-multipass):

```bash
sudo snap install multipass
multipass launch 24.04 --name agent --cpus 6 --memory 12G --disk 80G
multipass shell agent
```

Then configure the guest user, SSH, and passwordless sudo. LXD virtual machines are another option when an organization already uses LXD; Ubuntu documents LXD as managing both system containers and virtual machines [[32]](#ref-ubuntu-lxd).

### Linux option C: restricted container for trusted work

Containers are convenient for trusted repositories, but they are a weaker boundary than a VM for unrestricted agents. Avoid:

```text
--privileged
-v /:/host
-v ~/.ssh:/home/agent/.ssh
-v /var/run/docker.sock:/var/run/docker.sock
--net=host
```

A container can be useful for narrow CI-like tasks, but a full `--yolo` coding agent with package installation and arbitrary command execution belongs in a VM unless the repository and dependency scripts are already trusted.

### Linux option D: OverlayFS plus chroot as reset mechanism

OverlayFS can provide a fast filesystem reset layer:

```bash
sudo mkdir -p /srv/agent/base /srv/agent/upper /srv/agent/work /srv/agent/merged

sudo mount -t overlay overlay \
  -o lowerdir=/srv/agent/base,upperdir=/srv/agent/upper,workdir=/srv/agent/work \
  /srv/agent/merged

sudo chroot /srv/agent/merged /bin/bash
```

The Linux kernel documentation describes the lower, upper, work, and merged directories used by OverlayFS [[33]](#ref-linux-overlayfs). This is useful as a reset mechanism, not as a strong security boundary for a privileged autonomous agent. `systemd-nspawn` is stronger than bare chroot and useful for lightweight machine containers, but it still does not replace a VM for untrusted full-access work [[34]](#ref-systemd-nspawn).

### macOS option A: Lima Ubuntu VM

On macOS, use a Linux VM rather than giving the agent access to the macOS host. Lima is a good command-line-native default. Its documentation shows that host home directories are mounted read-only by default and can be made writable or disabled explicitly [[35]](#ref-lima-usage). For OAP, prefer a narrow writable share or no host mount.

Example `agent.yaml`:

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

Start and enter:

```bash
brew install lima
limactl start ./agent.yaml --name agent
limactl shell agent
```

Lima documents several host-filesystem mount methods, including reverse-sshfs, 9p, and virtiofs depending on version and VM backend [[36]](#ref-lima-mounts). Keep those mounts narrow.

### macOS option B: Multipass or UTM

Multipass is also available on macOS and gives a simple Ubuntu VM:

```bash
brew install --cask multipass
multipass launch 24.04 --name agent --cpus 6 --memory 12G --disk 80G
multipass shell agent
```

Use UTM, VMware Fusion, or Parallels when the organization already standardizes on those tools. The OAP principle is unchanged: do not give the agent broad write access to the macOS home directory or long-lived host credentials.

## II.4 Preflight Checklist

Before launching an unrestricted agent mode, the operator should be able to check every item below:

```text
[ ] Agent runs inside disposable VM/distro/sandbox, not normal host account
[ ] Agent user is dedicated
[ ] Passwordless sudo/admin exists only inside the guest
[ ] Repository is inside guest or narrow writable mount
[ ] Host home directory is not mounted writable
[ ] No host/prod SSH private keys are mounted or copied into guest
[ ] No host/prod cloud, kube, or Docker credentials are in guest
[ ] No password-store files, browser profile, or production .env in guest
[ ] Guest-local ~/.ssh is expected for SSH-in guests
[ ] Guest-local ~/.ssh has VM/sandbox access material only
[ ] CODEX_HOME is guest-local
[ ] Network policy is understood
[ ] Snapshot/export/checkpoint exists
[ ] Git working tree starts clean or known dirty
[ ] Logs are enabled
[ ] Credentials, if any, are short-lived and least-privilege
[ ] Agent cannot merge its own PR
[ ] Recovery path has been tested once
```

The preflight can be short because OAP does not require perfect isolation. It requires a boundary that makes the expected failure survivable. A reasonable summary is:

> The agent may be powerful inside the guest, but the guest must not contain anything the human cannot afford to lose or rotate.

<Question
  id="oap-preflight-boundary"
  question="What is the main reason OAP prefers a hardened, rebuildable guest runtime for a high-autonomy execution agent?"
  options={["Because the guest becomes the authoritative source of project truth", "* Because the agent can act with useful autonomy inside an environment that is disposable and separated from host secrets", "Because passwordless sudo is never needed inside the guest", "Because a VM guarantees the agent cannot make mistakes"]}
  attempts={2}
>
The guest boundary is not about assuming perfect safety. It is about containing risk while allowing the agent to perform real setup, testing, and implementation work without dragging the human into routine operations.
</Question>
