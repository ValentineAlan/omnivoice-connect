# First-install trial: 3–5 independent testers wanted

OmniVoice Connect 0.1.0 is available for experimental testing. It helps Home
Assistant users configure an external OmniVoice server, check it, generate a speech
sample and finish Wyoming/Assist setup. The model stays on a separate supported
NVIDIA Docker host.

We are looking for 3–5 volunteers who have not worked on this project. Docker and
TrueNAS installations are both welcome; failed attempts are useful reports too.

1. Read the [requirements and installation guide](https://github.com/ValentineAlan/omnivoice-connect).
2. Follow the [first-install checklist](https://github.com/ValentineAlan/omnivoice-connect/blob/main/docs/tester-guide.md).
3. Submit a separate [first-install report](https://github.com/ValentineAlan/omnivoice-connect/issues/new?template=first-install.yaml).

Please omit private addresses, credentials, personal recordings and full server
logs. The companion's diagnostic download excludes these fields.

## Evidence so far

Published amd64/arm64 builds passed automated checks. One owner-assisted HAOS
installation passed Ingress, external speech generation, saved-settings restart
and external-server independence checks. See the [validation record](https://github.com/ValentineAlan/omnivoice-connect/blob/main/VALIDATION.md)
for the exact scope and remaining gaps. This does not count as independent testing.

Independent completed reports at trial opening: **0**. Reports will be linked here
as they arrive. Broad promotion follows review of the trial results; no completion
date or untested compatibility is promised.

## Review checklist

- [ ] Review 3–5 independent installation reports, including unsuccessful attempts.
- [ ] Confirm spoken Assist responses and that stopping the companion leaves Assist working.
- [ ] Review restart persistence and any available upgrade/rollback evidence.
- [ ] Fix recurring installation problems and update the walkthrough.
- [ ] Record remaining platform gaps before broader promotion.
