# 2. Prepare WSL2 Ubuntu

This quickstart treats WSL2 Ubuntu as the execution environment. It is not perfect isolation, and it is not a security product. It is a practical first boundary: the agent works in Linux, the repository lives in the Linux filesystem, and host secrets are not copied into the guest.

<Sidenote>
WSL2 is not presented here as an ideal security solution, but as a pragmatic first boundary for rapid adoption. The main point is that the agent is not working directly inside the user's ordinary Windows environment.
</Sidenote>

Install WSL2 Ubuntu from PowerShell:

```powershell
wsl --install -d Ubuntu
wsl -l -v
wsl --set-version Ubuntu 2
```

Open Ubuntu and install a baseline toolchain:

```bash
sudo apt update
sudo apt upgrade -y
sudo apt install -y build-essential git curl wget unzip zip ca-certificates openssh-client
```

Create a Linux-side work directory:

```bash
mkdir -p ~/work
cd ~/work
git clone <repo-url>
cd <repo-name>
```

Keep the repository under `~/work`, not under `/mnt/c/...`. WSL2 can access the Windows filesystem, but for coding-agent work the Linux filesystem is cleaner and faster. The agent should not receive broad write access to the host user's Windows profile.

<Sidenote>
This is one of the most important practical choices in the guide. Simply keeping the repository in the Linux filesystem removes a surprising amount of hidden friction and accidental host access.
</Sidenote>

If you want to reduce accidental Windows coupling, edit `/etc/wsl.conf`:

```ini
[automount]
enabled=false

[interop]
enabled=false
appendWindowsPath=false
```

Then restart WSL from PowerShell:

```powershell
wsl --shutdown
```

This is optional for a first experiment. It is useful when you want a cleaner boundary and fewer accidental host dependencies.

## Install the agent CLIs

Install and authenticate Codex CLI according to the current OpenAI Codex documentation. The command this quickstart uses for high-autonomy execution is:

```bash
codex --yolo
```

For the same execution role with Claude Code CLI, install and authenticate Claude Code according to the current Anthropic documentation. The equivalent high-autonomy command is:

```bash
claude --dangerously-skip-permissions
```

Claude Code also documents the equivalent setting form:

```bash
claude --permission-mode bypassPermissions
```

Keep each CLI's local state inside WSL2. Add these lines to `~/.bashrc` before logging in to the tools if you want the state paths to be stable:

```bash
mkdir -p "$HOME/.codex-agent" "$HOME/.claude-agent"
export CODEX_HOME="$HOME/.codex-agent"
export CLAUDE_CONFIG_DIR="$HOME/.claude-agent"
```

Then reload your shell:

```bash
source ~/.bashrc
```

In this quickstart, whenever a work order says "run the execution agent," use either:

```bash
codex --yolo
```

or:

```bash
claude --dangerously-skip-permissions
```

Do not run either command in your normal Windows home directory. Run it inside the WSL2 project directory you prepared for agent work.

## Keep secrets out

For a first run, use the simplest rule:

```text
The WSL2 agent environment must not contain anything you cannot afford to lose or rotate.
```

That means:

- do not copy host production SSH private keys into WSL2;
- do not copy cloud credentials into WSL2;
- do not copy Kubernetes configs into WSL2;
- do not put production `.env` files in the repository;
- do not mount or expose browser profiles or password-manager files;
- do not give the agent credentials that can mutate production systems.

A guest-local `~/.ssh` directory is normal. It may be needed for Git over SSH. Its existence is not a failure. The failure is copying host or production private keys into it. Prefer a separate key for this WSL2 environment, or use HTTPS/token-based Git credentials with limited scope.

<Sidenote>
The important distinction is not whether a key exists, but where it came from and what it unlocks. A separate WSL2-scoped key reduces the blast radius if the environment or agent goes wrong.
</Sidenote>

## Optional passwordless sudo

OAP works best when the execution agent can install ordinary local development tools inside the execution environment. In WSL2, you may decide to allow passwordless sudo for the WSL user:

```bash
sudo visudo -f /etc/sudoers.d/90-agent-nopasswd
```

Add:

```txt
%sudo ALL=(ALL) NOPASSWD:ALL
```

Then verify:

```bash
sudo chmod 0440 /etc/sudoers.d/90-agent-nopasswd
sudo visudo -c
sudo -n true && echo "passwordless sudo works"
```

This is powerful. It is acceptable only because the agent is inside the chosen WSL2 execution environment and the repository is the durable truth. It is not acceptable if WSL2 contains host secrets, production credentials, or irreplaceable data.

<Sidenote>
`NOPASSWD` is not a general recommendation for every Linux system. In this guide it is acceptable only in combination with a bounded, disposable environment and a strict ban on production secrets.
</Sidenote>
