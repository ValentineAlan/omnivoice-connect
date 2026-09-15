# Get speaking

1. Add this app repository using the README button, then install OmniVoice Connect.
2. Start the app and select **Open web UI**. No app options or exposed ports are required.
3. If you need a server, choose Linux Docker or TrueNAS in the setup guide. Generate
   the configuration and run it on your external GPU host. The app does not log in
   to that host or install the server for you.
4. Enter that host's LAN address and published Wyoming port (usually 10200).
5. Check the connection, generate a sample, and press play. The fixed sample is English.
6. Open Wyoming setup. Enter the same external host and port. In Settings → Voice
   assistants, select OmniVoice as the text-to-speech provider and test a spoken response.
7. Mark the confirmation after hearing Assist. This is your confirmation, not an
   automated Home Assistant configuration check.

The app is optional after setup. Stopping it must not stop Assist from using the
external server. Its saved address is kept in `/data/connect.json`; no credentials
are required. The newest generated sample is kept in memory and access expires
after ten minutes or when another check starts; restarting clears it completely.
Diagnostics deliberately exclude server addresses, voice names, audio and logs.

## Requirements

The companion supports Home Assistant OS on amd64 and aarch64. It uses Ingress and
accepts requests only from the Supervisor Ingress proxy. The external server needs
the hardware described in the [server requirements](https://github.com/ValentineAlan/wyoming-omnivoice#requirements-and-versions).
Only RFC1918 IPv4 and unique-local IPv6 server addresses are accepted. Supervisor
internal, loopback, link-local and public addresses are rejected. Use a LAN IP if
hostname resolution fails. A server on another VLAN needs firewall access from
both this app and Home Assistant; neither automatic scanning nor mDNS is required.

## Troubleshooting

* **Cannot connect:** check the Docker port mapping, LAN IP, firewall and container status.
* **No TTS voice:** you may have entered a Whisper/STT port rather than OmniVoice's port.
* **Timeout:** model downloads and cold starts can take time; check server logs before retrying.
* **Sample works, Assist does not:** verify the integration host/port and selected assistant's TTS provider.
* **App will not start:** inspect the app log; its `/data` volume must be writable by UID 568.
* **Browser plays no sound:** use the player's play button and check browser/device volume.
* **502 on Open web UI:** wait for startup and inspect the app log. Do not expose port 8099 publicly.

Update the companion through the Home Assistant app store. It does not update your
external container. Follow the server's release guide for that separate update.
