# Validation status

## Companion 0.1.0

18 automated checks passed locally on 15 September 2026. They cover Wyoming
discovery, separated JSON and partial reads, PCM output, bad service responses,
truncated/oversized data, sample limits, deadlines, LAN target validation,
Ingress-only access, request token checks, relative frontend assets, generated
configuration, saved settings, job expiry and the diagnostic field selection.
JavaScript syntax validation passed. The local browser interface rendered and
the installation controls were inspected.

The test audio in unit tests is synthetic PCM fixture data, not a GPU speech test.
These checks alone do not establish Home Assistant installation compatibility.

## Release gates

* GitHub Actions tests and amd64/aarch64 image publication: pending.
* Actual HAOS installation, Ingress, restart and external speech sample: pending.
* Independent clean installations: 0 of 3–5 target participants.
* Broad community launch: held until independent installation feedback is reviewed.

The external server's existing 1.1.0 evidence is in its own VALIDATION.md.
It must not be presented as independent validation of this new companion.
