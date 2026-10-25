# Home lab security

Security engineering from my self-hosted home lab: detection rules, test methods and write-ups. Nothing here
contains hostnames, IP addresses, credentials or personal data from the lab.

## Lab at a glance
- **Zero Trust access:** self-hosted services are published through Cloudflare Tunnel and Cloudflare Access with Authentik passkey SSO, with no inbound port forwarding for the web apps. The origin re-validates the Access JWT (signature, issuer, audience, identity, lifetime) before serving anything.
- **SIEM:** a Wazuh manager on an isolated network segment, with agents on Windows and Linux hosts. The host firewall only allows agent traffic toward the manager.
- **Hardening:** DNSSEC, DMARC (reject), SPF, CAA and HSTS on the public domains. Every change ships with pre-checks, a backup and a scripted rollback.

## Contents

### [`wazuh/`](wazuh/): identity detection rules for Authentik
Custom Wazuh rules that turn Authentik sign-in and admin events into alerts:

| Rule | Level | Detects |
|---|---|---|
| 100701 | 5 | Failed sign-in |
| 100702 | 10 | 8+ failed sign-ins in 5 minutes (brute force / password spraying, MITRE ATT&CK T1110) |
| 100703 | 3 | Successful sign-in |
| 100704 | 8 | New passkey or MFA device enrolled |
| 100705 | 10 | Flow, policy, provider, token or application configuration changed |
| 100706 | 8 | User changed, password set, impersonation started |

- [`authentik_identity_rules.xml`](wazuh/authentik_identity_rules.xml): the rules. Install them to `/var/ossec/etc/rules/`, run `wazuh-analysisd -t`, then restart the manager.
- [`test-results.md`](wazuh/test-results.md): how the rules were validated, against 21,000+ real log lines and with wazuh-logtest. Includes the two draft bugs that testing caught.
- [`make_test_event.py`](wazuh/make_test_event.py): builds synthetic Authentik events for `wazuh-logtest`.

The rules assume Authentik's container logs are collected with `<log_format>json</log_format>` (Docker json-file driver). The burst rule counts failures from any source, which suits a lab with a handful of users; a larger deployment would add `<same_field>` on the client address to make it per source.

### Honeypot: Google Cloud
I deployed a honeypot/honeynet on Google Cloud Platform to observe real attacker behaviour against an internet-facing host.

- **Result:** **3,000+ attack attempts within the first hour.**
- **What they were:** mostly **SSH brute-force** and **credential-stuffing** attempts, automated tooling cycling through common usernames and leaked passwords.
- **Takeaway:** an internet-facing host with SSH open is attacked continuously, at a rate no human could follow. It is the reason the lab above exposes no SSH or admin ports at all, uses passkeys instead of passwords, and alerts on bursts of failed sign-ins (rule 100702).

## License
MIT. Use the rules as a starting point for your own Authentik monitoring.
