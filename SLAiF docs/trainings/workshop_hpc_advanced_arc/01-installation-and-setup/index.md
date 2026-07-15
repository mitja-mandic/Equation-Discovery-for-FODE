# Installation And Setup

## Prerequisites

Before submitting jobs through ARC, make sure you have:

- a valid SLING User Interface account;
- an X.509 digital certificate from a trusted certificate authority;
- membership in a Virtual Organization, such as `gen.vo.sling.si`;
- a terminal with SSH access;
- a working ARC client installation.

ARC uses the certificate and VO membership to authenticate you across distributed resources. This is separate from ordinary SSH authentication.

## Installing The ARC Client

Official operating-system repositories may lag behind current NorduGrid ARC releases. When possible, use the NorduGrid packages.

### Ubuntu Or Debian

```bash
wget -q -O - https://download.nordugrid.org/DEB-GPG-KEY-nordugrid-6.asc | sudo apt-key add -
echo "deb http://download.nordugrid.org/repos-6/ubuntu/ jammy main" | sudo tee /etc/apt/sources.list.d/nordugrid.list

sudo apt-get update
sudo apt-get install nordugrid-arc-client nordugrid-arc-plugins-needed
```

### CentOS, Rocky, Or Similar

```bash
sudo yum install epel-release
sudo yum install nordugrid-arc-client nordugrid-arc-plugins-needed
```

### macOS

On macOS, Homebrew is usually the simplest option:

```bash
brew tap nordugrid/arc
brew install nordugrid-arc
```

macOS users should also create the ARC configuration directory manually:

```bash
mkdir -p ~/.arc
```

If the Homebrew package is not suitable for your system, ARC can also be compiled from source. One macOS-oriented build reference is available at:

```text
https://github.com/pavleb/arc/tree/mac_build
```

## Certificate Setup

ARC expects certificate material in PEM format. If your certificate arrives as a `.p12` file, convert it into:

- `usercert.pem`: the public certificate;
- `userkey.pem`: the private key.

Protect the private key:

```bash
chmod 400 userkey.pem
```

Place these files where ARC can find them, typically under `~/.arc`.

## Creating And Inspecting A Proxy

A proxy is a short-lived credential derived from your certificate. You normally create it before submitting jobs:

```bash
arcproxy -s gen.vo.sling.si
```

ARC will ask for the private-key passphrase and then report the generated proxy. Inspect it with:

```bash
arcproxy -I
```

The important fields are the identity, remaining validity time, proxy path, and proxy type. If authentication later fails unexpectedly, checking the proxy lifetime is one of the first debugging steps.

## ARC Computing Element Configuration

ARC clients use Computing Element definitions to know where jobs can be submitted. A typical configuration contains entries like these:

```ini
[computing/nsc]
url=https://nsc.ijs.si:443/arex
infointerface=org.ogf.glue.emies.resourceinfo
submissioninterface=org.ogf.glue.emies.activitycreation
default=yes

[computing/situla]
url=https://situla.fis.unm.si:443/arex
infointerface=org.ogf.glue.emies.resourceinfo
submissioninterface=org.ogf.glue.emies.activitycreation
default=yes

[computing/arnes]
url=https://hpc.arnes.si:443/arex
infointerface=org.ogf.glue.emies.resourceinfo
submissioninterface=org.ogf.glue.emies.activitycreation
default=yes
```

Use meaningful aliases such as `nsc`, `situla`, and `arnes`, because they make submission commands and automation scripts much easier to read.
