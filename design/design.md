# Getron: Tetron Installation and Version Management

## 1. Purpose

Getron is the installation and lifecycle manager for Tetron.

Its purpose is to make installing, upgrading, downgrading, repairing and diagnosing a Tetron installation reliable and predictable. Getron should behave more like `rustup` or Lean 4's `lake` than a collection of shell commands for copying binaries and starting services.

The fundamental design goal is:

> **No ordinary installation or upgrade failure should leave the machine in an ambiguous or unusable state, and the user should always be told what happened and what to do next.**

Getron manages Tetron. It does not provide Tetron's networking functionality itself.

The two programs therefore have distinct responsibilities:

```text
getron
    Installation and lifecycle management

tetron
    The actual Tetron daemon and operational CLI
```

---

# 2. Bootstrap

Getron itself is installed by a minimal bootstrap script:

```bash
curl -fsSL https://getron.dev/install.sh | sh
```

This script has exactly one responsibility:

> Install Getron.

It must **not** install Tetron, configure a Tetron node, start a Tetron service or perform any other node-management operation.

After the bootstrap completes, the user has:

```bash
getron
```

available on their `PATH`.

The user then explicitly initiates Tetron installation:

```bash
getron install
```

This separation is intentional.

```text
install.sh
    │
    └── installs Getron

getron install
    │
    └── installs and configures Tetron
```

The bootstrap script should remain deliberately simple. All substantive installation logic belongs in Getron.

---

# 3. User Experience

The complete initial experience should be:

```bash
curl -fsSL https://getron.dev/install.sh | sh
getron install
```

There should be no requirement for the user to:

* choose an installation directory
* copy a binary into `/usr/local/bin`
* select an architecture-specific Tetron filename
* manually install a service file
* manually enable a service
* manually start the daemon
* manually verify that the daemon started
* determine which Tetron version is appropriate
* manually download dependencies or addons

In particular, this should **not** be part of the documented installation procedure:

```bash
sudo install getron /usr/local/bin/getron
```

Getron's bootstrap process owns installation of Getron itself.

---

# 4. Responsibilities of Getron

Getron is responsible for:

* discovering the host platform
* selecting compatible Tetron releases
* downloading Tetron
* verifying downloaded artifacts
* installing Tetron versions
* maintaining multiple installed versions
* selecting the active Tetron version
* installing and managing the Tetron system service
* starting and stopping Tetron
* performing health checks
* upgrading Tetron
* downgrading Tetron
* rolling back failed upgrades
* performing configuration migrations
* checking compatibility between Tetron and addons
* installing and managing addons
* diagnosing broken installations
* repairing installations
* removing unused versions
* producing useful diagnostic information

Tetron itself remains responsible for:

* the daemon
* the network
* the TUN interface
* the Tetron IPC API
* operational commands such as `status`, `join`, `create`, etc.

---

# 5. Core Commands

The initial command vocabulary should be small and predictable.

## Installation

```bash
getron install
```

Install Tetron if it is not already installed.

```bash
getron install 1.3.0
```

Install a specific version.

## Updates

```bash
getron update
```

Check for and install a newer compatible version.

```bash
getron update --check
```

Check for updates without changing the installation.

## Version management

```bash
getron versions
```

List installed Tetron versions.

```bash
getron use 1.3.0
```

Switch the active Tetron version.

```bash
getron rollback
```

Return to the previous known-good version.

## Diagnostics

```bash
getron doctor
```

Diagnose the installation and provide actionable recommendations.

```bash
getron repair
```

Repair a damaged installation where possible.

## Cleanup

```bash
getron gc
```

Remove unused versions and installation artifacts.

```bash
getron uninstall 1.2.0
```

Remove one particular installed version.

---

# 6. Versioned Installation

Getron must never treat the currently installed Tetron executable as a mutable file.

Instead, each Tetron version is installed into its own immutable directory.

A possible Linux layout is:

```text
/usr/local/lib/tetron/
    versions/
        1.2.0/
            tetron
            manifest.toml

        1.3.0/
            tetron
            manifest.toml

    active -> versions/1.3.0
```

The exact filesystem location is an implementation detail and should be selected by Getron.

The important property is that:

> **Installing or upgrading one version never overwrites another installed version.**

The active version can therefore be changed atomically.

This also avoids problems caused by replacing a running executable in place.

---

# 7. Persistent Configuration

Tetron configuration and state must remain independent of the executable version.

Conceptually:

```text
Tetron binaries
    /.../tetron/versions/

Tetron configuration
    /etc/tetron/

Tetron runtime state
    /var/lib/tetron/
```

An upgrade from:

```text
1.2.0 → 1.3.0
```

must not implicitly replace or discard the user's node configuration.

Configuration migrations, if required, must be explicit and transactional.

The existing Tetron configuration system already uses atomic replacement for configuration files and should retain that property.

---

# 8. Version Manifest

Every installed Tetron version should have a manifest.

Example:

```toml
version = "1.3.0"
git_sha = "abc123..."
target = "x86_64-unknown-linux-gnu"

artifact = "tetron-linux-x86_64"
sha256 = "..."

protocol_version = 7
config_schema_min = 3
config_schema_max = 5

installed_at = "2026-08-04T19:23:14Z"
```

The manifest allows Getron to answer questions about an installed version without relying on mutable external state.

It should record at least:

* semantic version
* target platform
* release artifact
* cryptographic hash
* source revision where available
* protocol compatibility
* configuration compatibility
* installation timestamp

---

# 9. Atomic Installation

Installation must be treated as a transaction.

A simplified installation sequence is:

```text
discover platform
       ↓
select version
       ↓
download artifact
       ↓
verify artifact
       ↓
create version directory
       ↓
install executable
       ↓
validate executable
       ↓
validate compatibility
       ↓
prepare service
       ↓
activate version
       ↓
start service
       ↓
wait for daemon
       ↓
health check
       ↓
commit
```

At no point should a failed download, corrupt binary, incompatible version or failed daemon startup destroy the previously working installation.

---

# 10. Upgrade Transaction

An upgrade should follow the same transactional model.

For example:

```bash
sudo getron update
```

Expected behavior:

```text
Checking for updates...
  current: 1.2.3
  latest:  1.3.0

Downloading Tetron 1.3.0...
  download complete

Verifying release...
  checksum: OK
  signature: OK

Installing Tetron 1.3.0...
  executable: OK
  compatibility: OK

Activating Tetron 1.3.0...
  service stopped
  version switched
  service started

Waiting for daemon...
  IPC: OK
  daemon: OK

Update complete.

  previous: 1.2.3
  current:  1.3.0

Previous version retained for rollback.
```

---

# 11. Automatic Rollback

If activation succeeds but the new daemon does not become healthy, Getron must automatically restore the previous version.

For example:

```text
Tetron update failed.

  requested version: 1.3.0
  previous version:  1.2.3

The new daemon failed its health check.

Restoring 1.2.3...
  service stopped
  previous version activated
  service started
  health check: OK

Rollback complete.

Tetron is still running version 1.2.3.

Diagnostic log:
  /var/log/tetron/install/2026-08-04T192314Z.log
```

The user should never be left with:

```text
Tetron might be broken.
Try reinstalling.
```

Instead, Getron should make the machine safe first and explain the failure second.

---

# 12. Explicit Version Selection

Multiple versions should be allowed to coexist.

For example:

```text
Installed Tetron versions

  1.3.0   active
  1.2.3   rollback
  1.1.9
```

The user can switch versions with:

```bash
sudo getron use 1.2.3
```

The same transactional activation and health-check process applies to manual version changes as to upgrades.

A failed `getron use` must therefore also automatically restore the previous working version.

---

# 13. Rollback

Rollback should be a first-class operation.

```bash
sudo getron rollback
```

should mean:

> Restore the most recent known-good Tetron installation.

It should not require the user to remember which version was previously installed.

Getron should maintain enough installation metadata to identify the previous known-good version.

At least one previous version should normally be retained after an upgrade.

---

# 14. Compatibility

Tetron consists of more than one executable. In particular, the Web UI and other addons communicate with the Tetron daemon over the same IPC interface.

The existing architecture already treats the Web UI as an optional separate binary communicating with the daemon through the shared IPC socket.

Therefore Getron must understand compatibility between:

```text
Tetron core
    │
    ├── Web UI
    ├── systray
    └── future addons
```

A Tetron release should declare relevant compatibility information, such as:

```toml
[compatibility]
ipc_protocol = 7
config_schema_min = 3
config_schema_max = 5
```

An incompatible addon should not silently be allowed to remain active.

Instead:

```text
Cannot activate Tetron 2.0.0.

The installed tetron-webui is incompatible.

  Web UI: 1.4.0
  required IPC protocol: 7
  supported IPC protocol: 6

Suggested action:

    getron addon update webui
```

The user should always receive a concrete next step.

---

# 15. Addons

Addons should eventually be managed by Getron rather than having unrelated installation mechanisms.

For example:

```bash
getron addon list
getron addon install webui
getron addon install systray
getron addon update
getron addon remove webui
```

The existing Web UI can continue to provide an Add-ons interface, but the underlying installation mechanism should be the same Getron-managed system.

Each addon should have its own manifest containing:

* name
* version
* target platform
* artifact
* checksum/signature
* Tetron compatibility
* IPC compatibility
* installation state

---

# 16. Service Management

Getron owns installation and lifecycle management of the Tetron system service.

The daemon itself should remain independent of the service manager. The current Tetron design already has this useful property: the daemon can run in the foreground without requiring systemd, while the service-management convenience commands are platform-specific.

Getron should detect the host's service environment rather than blindly assuming systemd.

For Linux:

```text
systemd
OpenRC
runit
s6
other / unsupported
```

For macOS:

```text
launchd
```

If a service manager is unsupported, Getron should explain the situation and provide the appropriate fallback rather than producing an opaque `systemctl: command not found` error.

The current Tetron implementation already uses `/run/systemd/system` as the canonical systemd detection mechanism. That behavior should be preserved.

---

# 17. Service Installation Must Be Observable

Privileged operations should never happen silently.

For example:

```text
Installing Tetron system service
  service: tetron.service
  location: /etc/systemd/system/tetron.service

Enabling service...
Starting service...

Waiting for daemon...
```

The current implementation has already adopted this principle by explicitly reporting the service name and path being written.

Getron should make this standard throughout the installation process.

---

# 18. Doctor

`getron doctor` is a major part of the design rather than an afterthought.

It should inspect the entire installation:

```text
Getron diagnostic

Platform
  OS:             Linux
  Architecture:   x86_64
  Init system:    systemd

Getron
  version:        1.0.0
  executable:     OK
  PATH:           OK

Tetron
  active:         1.3.0
  executable:     OK
  manifest:       OK
  checksum:       OK

Service
  unit:           tetron.service
  installed:      yes
  enabled:        yes
  active:         yes

Daemon
  version:        1.3.0
  IPC:            OK
  TUN:            OK

Configuration
  configuration:  OK
  permissions:    OK

Addons
  webui:          1.3.0
  compatibility:  OK

Result: HEALTHY
```

When something is wrong, the diagnostic must explain both the problem and the remedy.

---

# 19. Repair

`getron repair` should make targeted repairs rather than blindly reinstalling everything.

For example:

```text
Checking installation...

  Getron executable       OK
  Tetron executable       OK
  Version manifest        OK
  Active version          BROKEN
  Service unit            OK
  Configuration           OK

Repairing active version...

  active → 1.3.0          OK

Restarting service...

  daemon health            OK

Repair complete.
```

Repair operations should themselves be transactional whenever possible.

---

# 20. Garbage Collection

Old versions should not accumulate indefinitely.

After several upgrades:

```text
versions/
    1.1.9
    1.2.0
    1.2.3
    1.3.0
    1.4.0
```

Getron can eventually remove versions that are no longer needed:

```bash
getron gc
```

The active version must never be removed.

The most recent known-good rollback version should normally be retained automatically.

---

# 21. Error Handling

Every externally observable failure should belong to a known class.

Examples:

```text
network unavailable
DNS failure
TLS failure
HTTP failure
release unavailable
unsupported platform
unsupported architecture
checksum failure
signature failure
corrupt executable
insufficient permissions
service manager unavailable
service installation failure
service startup failure
daemon crash
daemon health-check failure
configuration migration failure
incompatible protocol
incompatible addon
disk full
read-only filesystem
existing installation inconsistent
```

Errors should contain:

1. What Getron was trying to do.
2. What failed.
3. Why it failed, when known.
4. Whether the existing installation is safe.
5. What Getron did to recover.
6. What the user should do next.

For example:

```text
ERROR: unable to activate Tetron 1.4.0

The daemon exited during startup.

Getron restored Tetron 1.3.0 automatically.

Current state:
  Tetron 1.3.0 — running

No further action is required.

The failed installation was retained for diagnosis.

Run:

    getron doctor

for additional information.
```

This is preferable to exposing raw subprocess errors as the primary user interface.

---

# 22. Installation State Machine

The installer should have an explicit internal state machine.

Conceptually:

```text
UNINSTALLED
    │
    ▼
DISCOVERING
    │
    ▼
DOWNLOADING
    │
    ▼
VERIFYING
    │
    ▼
STAGING
    │
    ▼
VALIDATING
    │
    ▼
ACTIVATING
    │
    ▼
STARTING
    │
    ▼
HEALTH_CHECK
    │
    ├── success ──► INSTALLED
    │
    └── failure ──► ROLLBACK
                         │
                         ▼
                    PREVIOUS_GOOD
```

Every transition should have a defined failure behavior.

This makes it possible to reason about interrupted installations and to recover from partially completed operations.

---

# 23. Interrupted Operations

Getron must also handle interruption.

For example:

```bash
sudo getron update
```

is interrupted by:

```text
Ctrl-C
```

or:

```text
machine reboot
```

The next invocation should inspect the installation state and determine whether a transaction was left incomplete.

For example:

```text
An interrupted Getron transaction was detected.

  operation: update
  target:   1.4.0
  state:    staging

The active Tetron installation was not modified.

Cleaning up incomplete transaction...
  OK

Current Tetron:
  1.3.0 — healthy
```

This is one of the major reasons to maintain explicit transaction metadata rather than implementing installation as a sequence of shell commands.

---

# 24. Security

Getron downloads executable code and therefore must treat release verification as a security boundary.

At minimum, releases should have:

* cryptographic hashes
* HTTPS transport
* authenticated release metadata

Ideally, release artifacts should also be signed and Getron should verify the signature before activation.

The verification process must happen **before an executable is made active**.

A failed verification must leave the previous installation untouched.

---

# 25. Idempotence

Running the same command repeatedly should be safe.

For example:

```bash
getron install
```

when Tetron is already installed and healthy should not reinstall everything unnecessarily.

Instead:

```text
Tetron is already installed.

  version: 1.3.0
  service: running
  health:  OK

Nothing to do.
```

Likewise:

```bash
getron install 1.3.0
```

should recognize that version 1.3.0 is already installed.

This is important both for users and for automation.

---

# 26. Design Principle: Getron Owns the State

The most important architectural principle is:

> **Getron should know what state Tetron is supposed to be in and what state it is actually in.**

It should therefore maintain installation metadata describing:

```text
Getron version
installed Tetron versions
active Tetron version
previous known-good version
installed addons
compatibility information
installation transactions
```

Getron should be able to reconstruct the state of the installation rather than relying on assumptions about what happened during previous commands.

---

# 27. Final User Model

The resulting user experience should be extremely simple.

### First installation

```bash
curl -fsSL https://getron.dev/install.sh | sh
getron install
```

### Update

```bash
getron update
```

### See versions

```bash
getron versions
```

### Switch versions

```bash
getron use 1.3.0
```

### Roll back

```bash
getron rollback
```

### Diagnose

```bash
getron doctor
```

### Repair

```bash
getron repair
```

The complexity belongs inside Getron, not in the installation instructions.

---

# 28. Guiding Principle

Getron should make the following promise:

> **The user should never have to understand how Tetron is installed in order to install Tetron.**

They should not need to know:

* where binaries live
* which service manager is present
* how service files work
* how versions are selected
* how releases are downloaded
* how configuration migrations work
* how to recover from a failed upgrade

They should only need to know:

```bash
getron install
getron update
getron rollback
getron doctor
```

Everything else is implementation detail.

The bootstrap script gets Getron onto the machine.

**Getron then owns the rest.**
