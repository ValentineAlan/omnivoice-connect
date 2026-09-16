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

## Published build and owner-assisted HAOS check

On 16 September 2026, the [versioned GitHub Actions build](https://github.com/ValentineAlan/omnivoice-connect/actions/runs/34976901422)
passed tests and published `ghcr.io/valentinealan/omnivoice-connect:0.1.0`.
Anonymous registry access confirmed linux/amd64 and linux/arm64 images with index
digest `sha256:fd4466486d87576a198369f7ecd97526923e43d0a59a4161568c139403aad046`.
CI also checked fresh writable storage, runtime UID 568 and generated Compose syntax.

The companion was installed through the custom repository in a real HAOS app store.
Ingress loaded successfully, the existing external Wyoming service was detected,
and a fixed-phrase speech sample was generated: 5.25 seconds of audio, first audio
at 0.244 seconds. The browser player entered playback. This is server-test timing,
not end-to-end Assist latency or a subjective audio-quality assessment.

The saved address and port survived a companion restart. With the companion
stopped, a separate Wyoming client still obtained valid non-silent speech from
the external server (5.27 seconds; first audio 0.219 seconds). This checks server
independence; it does not substitute for a spoken Assist-device test. The companion
was started again after the check.

## Remaining release gates

* Actual arm64 HAOS installation: not yet tested (image build succeeded).
* End-to-end spoken Assist-device response in this onboarding trial: not verified.
* Upgrade/rollback between companion releases: not yet tested; this is the first release.
* Independent clean installations: 0 of 3–5 target participants.
* Broad community launch: held until independent installation feedback is reviewed.

The external server's existing 1.1.0 evidence is in its own VALIDATION.md.
It must not be presented as independent validation of this new companion.
