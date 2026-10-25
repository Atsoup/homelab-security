# Test results

## 1. Against real traffic
The rule patterns were run over **21,000+ real Authentik log lines** (the server and worker containers' log files) before
installation.

- Only the successful sign-in rule (100703) matched real events, which is the expected result for a quiet period with no attacks or configuration changes. **No false positives.**
- The first draft had two rules that could never fire:
  - **Device enrollment (100704)** matched CamelCase model names (`WebAuthnDevice`), but Authentik logs them in lowercase (`webauthndevice`).
  - **Configuration change (100705)** listed bare names (`policy`, `provider`), but real names are compound (`expressionpolicy`, `oauth2provider`). It now matches on a suffix.

  Testing against real lines is what caught both.

## 2. wazuh-logtest with synthetic events (`make_test_event.py`)

| Event (action / model) | Rule | Level | Expected |
|---|---|---|---|
| `login` / user | 100703 | 3 | successful sign-in, logged quietly |
| `login_failed` / user | 100701 | 5 | failed sign-in |
| `model_created` / webauthndevice | 100704 | 8 | new passkey enrolled |
| `model_updated` / webauthndevice | 100700 | 0 | routine "last used" update, no alert |
| `model_updated` / expressionpolicy | 100705 | 10 | policy changed |
| `model_created` / oauth2provider | 100705 | 10 | provider created |
| `model_updated` / user | 100700 | 0 | routine "last login" update, no alert |
| `password_set` / user | 100706 | 8 | password set |

The burst rule (100702: 8+ failed sign-ins within 5 minutes, MITRE T1110) is a frequency rule built on 100701. Its syntax passed `wazuh-analysisd -t`, but it was not replayed as a burst in wazuh-logtest. To test it, pipe the `login_failed` event in 8 times within one logtest session.

The installation was checked with `wazuh-analysisd -t` before the manager was restarted.
