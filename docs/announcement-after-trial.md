# Draft — publish after independent installation results

OmniVoice for Home Assistant runs local TTS on your NVIDIA Docker server and
connects to Assist over Wyoming. OmniVoice Connect adds a Home Assistant app that
helps you set up the server, check its connection and hear a sample.

Start with the [voice demo and hardware requirements](https://github.com/ValentineAlan/wyoming-omnivoice),
then [add the companion app repository](https://github.com/ValentineAlan/omnivoice-connect).
Already running the server? You can connect it directly through Wyoming.

Before publishing this draft, add a link to the completed independent trial
results, current known limitations and a real end-to-end Assist demonstration.
Do not replace those with assumptions or the unit-test result.

For a TrueNAS post: explain Install via YAML, dataset permissions and GPU selection;
state that catalog inclusion is separate. For generic Docker communities: link to
the generated Compose path and NVIDIA Container Toolkit requirements.

Creator outreach after the trial: introduce the project briefly, link the demo and
reproducible setup, state the separate-GPU requirement, and offer the published test
results. Choose relevant recipients individually rather than sending bulk outreach.
