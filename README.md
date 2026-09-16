# OmniVoice Connect for Home Assistant

Set up your external OmniVoice voice server, check it and hear a sample from a
small Home Assistant app. Your NVIDIA server does the speech generation; Home
Assistant connects directly over Wyoming.

**Experimental 0.1.0 — seeking first-install testers.** The companion is new;
the external server has its own tested release and hardware requirements.

[![Add app repository](https://my.home-assistant.io/badges/supervisor_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2FValentineAlan%2Fomnivoice-connect)

After adding the repository, install **OmniVoice Connect** from your app store,
start it, and open its web UI. Adding this repository makes the app visible in
your store; it is not an official or default-store app.

Already have a working server? Skip the companion and
[open Wyoming setup](https://my.home-assistant.io/redirect/config_flow_start/?domain=wyoming).

## What it does

* Generates a version-pinned Docker/TrueNAS configuration for an external NVIDIA host.
* Checks the Wyoming service and advertised TTS voices.
* Generates a fixed test phrase and plays it in your browser.
* Guides you to select OmniVoice in Assist, with separate connection, speech and
  user-confirmed Assist status.
* Saves the server address locally and exports diagnostics without private addresses,
  voice names, recordings, credentials or logs. No telemetry.

See the [walkthrough](connect/DOCS.md), [external server](https://github.com/ValentineAlan/wyoming-omnivoice)
and [independent test checklist](docs/tester-guide.md).

**First-install testers wanted:** join the [3–5 person trial](https://github.com/ValentineAlan/omnivoice-connect/issues/1).
Successful and unsuccessful attempts both help improve the setup guide.

## Development and boundaries

Python 3.12 standard library only. Run `python -m unittest discover -s tests -v`.
For a loopback-only preview: `python connect/server.py --dev --data ./data`.
The production entry point only accepts the Home Assistant Ingress proxy.
The companion has no Supervisor API, HA API, Docker socket, host network or GPU privileges.
It cannot verify Assist configuration automatically or deploy onto an external host.

GHCR image `ghcr.io/valentinealan/omnivoice-connect:0.1.0` targets amd64/aarch64.
The workflow tests the client and UI server before building. See
[validation status](VALIDATION.md) for what has actually been exercised.

Apache-2.0; see LICENSE and NOTICE.
