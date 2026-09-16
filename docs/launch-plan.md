# Discovery and onboarding launch

## Current audience

Home Assistant voice enthusiasts who already own a supported NVIDIA server.
Lead with a real audio demonstration and state the separate-server requirement
before the install button. Do not advertise universal GPU support, official store
inclusion, guaranteed five-minute setup or measured latency for untested hardware.

## Entry points

The external server README offers **Set up OmniVoice**, **Connect an existing
server**, an audible synthetic voice example, measured RTX 3090 results and hardware
requirements. The companion repository provides an **Add app repository** button.
Users then discover OmniVoice Connect within their own app store.

## Trial before broad launch

Publish a tester invitation in Home Assistant Community's Share your Projects
category, pointing to the tester guide and first-install issue form. Seek 3–5
volunteers. Track voluntary reports in GitHub issues; currently no independent
participants have completed this trial. Do not announce broad compatibility until
reports support it. The owner-assisted test is separate evidence.

The [public trial tracker](https://github.com/ValentineAlan/omnivoice-connect/issues/1)
is open for reports. The forum invitation is prepared in `community-invitation.md`;
record its published link here once the forum account is ready.

## Broader distribution after trial

Maintain that community topic as the canonical announcement. Adapt the explanation
for TrueNAS users (external app deployment) and other Docker users (generic Compose).
Use a short demonstration showing the app check, browser sample and an actual
Assist request. Include versions, hardware and cold/warm timing context.

After independent success, send a concise demo and setup link to suitable Home
Assistant voice creators. Record the chosen recipient before outreach. Do not bulk
message or imply endorsement. Do not depend on acceptance by a curated app collection.

## What to measure

Voluntary reports: requirement understood before install, time excluding downloads,
successful sample, successful Assist response, independence from companion,
restart persistence, upgrade and rollback where actually tested. Review recurring
support questions before expanding promotion. No user tracking is required.
