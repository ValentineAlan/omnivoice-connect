# First-install trial

We need 3–5 volunteers who have not helped build the project. Prefer at least one
Linux Docker host and one TrueNAS host, and both amd64 and aarch64 Home Assistant
hosts where possible. Use a compatible GPU; report untested models as test results,
not as established support.

## Before starting

Read the server requirements before installing. Confirm that you understand which
machine runs Home Assistant and which runs the model. Use a fresh data directory
or named volume; keep your current voice service available for rollback. Do not
replace an existing working installation just to participate.

Start a timer. Follow only the README and app instructions; note where you need
personal assistance. Separate download/model-loading time from configuration time.

## Tasks

1. Find the hardware requirement and choose the correct deployment path.
2. Add the repository and install/start OmniVoice Connect.
3. Generate a configuration and deploy the external server with fresh storage.
4. Check the connection; generate and listen to the fixed sample.
5. Configure Wyoming and your Assist TTS provider. Get a spoken response from Assist.
6. Stop the companion and verify that Assist still speaks.
7. Restart the companion: its server address should remain saved.
8. Restart the external server: voices and model cache should remain intact.
9. Repeat a connection check with a deliberately incorrect port; the error should
   help you recover without reporting success.
10. When a newer tested release exists, follow the upgrade/rollback guide. Mark
    this step **not tested** until there is a real version change to test.

## Report voluntarily

Use the **First-install feedback** issue form. Include GPU model, NVIDIA driver,
host platform, HAOS architecture, release versions, download time, setup time,
where you became stuck, whether Assist spoke, and restart/upgrade outcomes.
Do not include private addresses, voice recordings, credentials or unreviewed logs.
Diagnostics from the companion are optional. No automatic telemetry is collected.

## Decision after the trial

Aim for at least three completed independent setups with no unresolved install
blockers. Record failures too. Fix recurring confusion, update instructions, and
repeat affected steps before broad promotion. Never invent participants or results.
