# OmniVoice for Home Assistant — looking for first-install testers

I've packaged OmniVoice as a Wyoming TTS server for Home Assistant, with a new
experimental companion app called **OmniVoice Connect** to make setup easier.

The model runs on your separate NVIDIA Docker server. Home Assistant connects
directly over Wyoming; the companion helps generate a Docker/TrueNAS configuration,
check the server, hear a sample, and finish Assist setup. You can stop the companion
afterward without putting it in the speech path.

**Hardware matters:** the current GPU server image needs a supported Turing-or-newer
NVIDIA GPU and CUDA 13-compatible R580-or-newer driver. The existing runtime was
tested on RTX 3090. The companion itself supports amd64/aarch64 and needs no GPU.

- [Hear the example and see server requirements](https://github.com/ValentineAlan/wyoming-omnivoice)
- [Install OmniVoice Connect](https://github.com/ValentineAlan/omnivoice-connect)
- [First-install checklist](https://github.com/ValentineAlan/omnivoice-connect/blob/main/docs/tester-guide.md)
- [Send feedback](https://github.com/ValentineAlan/omnivoice-connect/issues/new?template=first-install.yaml)

I'm looking for **3–5 people who haven't worked on the project** to try a clean
installation and report where the instructions are confusing. Linux Docker and
TrueNAS setups are both welcome. Failed attempts are useful feedback too.

This is an independent community project, and the companion is experimental.
Adding its repository makes it appear in your app store; it isn't included in the
default store. No telemetry is collected. Please don't post private addresses,
credentials or personal voice recordings in feedback.
