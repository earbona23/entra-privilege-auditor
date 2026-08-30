# Entra Privilege Auditor

**Find the over-privileged and abandoned app identities in a Microsoft Entra ID tenant —
ranked by how much damage each one could do.**

![CI](https://github.com/earbona23/entra-privilege-auditor/actions/workflows/ci.yml/badge.svg)
![License: MIT](https://img.shields.io/badge/license-MIT-blue)
![Read-only](https://img.shields.io/badge/tenant%20access-read--only-brightgreen)

Read-only, always — it never changes anything in your tenant, and a test enforces that.

---

## The problem

Almost every Microsoft 365 tenant of any age carries the same silent risk: app registrations
and service principals holding Graph permissions nobody remembers granting. A legacy
integration with tenant-wide `Mail.ReadWrite`. An automation app that can assign directory
roles. A vendor connector with `Directory.ReadWrite.All`, set up once and never revisited.
Credentials issued years ago and never rotated. Apps with no owner and no sign-in in a year.

None of it shows up in a daily alert. None of it is anyone's job to review. And each one is
a standing path to compromising the whole tenant. **This tool gives you the consolidated,
risk-ranked view that the portal doesn't.**

## See it in 10 seconds — no tenant required

```bash
git clone https://github.com/earbona23/entra-privilege-auditor
cd entra-privilege-auditor
python -m auditor.cli                    # demo mode: a synthetic tenant, no credentials
```

Everything is labelled **`DEMO DATA`** — an invented tenant, so you can evaluate the tool
before connecting anything. Then try the HTML board you'd hand to management:

```bash
python -m auditor.cli --formato html --salida report.html
python -m auditor.cli --formato json --salida today.json
python -m auditor.cli --diff yesterday.json     # report only what changed since last run
```

![HTML report in demo mode](docs/screenshot.png)

Each app shows its exposure score, the abandonment signals against it, and — for every
permission — *why* it carries the risk level it does.

## What makes it more than a permission dump

**Risk is a judgment, so it lives in data you can edit.** The risk level of each Graph
permission is not hard-coded — it sits in [`data/permission_risk.yaml`](data/permission_risk.yaml),
with the *reason* attached, because what counts as "critical" depends on the organization.
A permission the catalog doesn't know is scored **`unknown` (weight 15)**, never ignored:
what nobody reviewed is uncertain, not harmless.

**The score measures capability, not count.** Fifteen low-impact scopes are less dangerous
than one `RoleManagement.ReadWrite.Directory`, and the score reflects that:

```
base = Σ weight(application permission) + 0.5 · Σ weight(delegated permission)
```

Application permissions weigh double delegated ones on purpose — they act with no user
present and usually span the whole tenant. Abandonment signals (no owner, expired or
never-rotated credential, stale sign-in) then apply compounding multipliers, because
over-privilege is worse when it's also unwatched.

**The tenant score is a sum, not an average** — twenty medium-risk apps are a bigger problem
than one, and an average would hide exactly the sprawl you're hunting.

## Connecting a real tenant

```bash
pip install -r requirements.txt
cp config.example.yaml config.yaml
export EPA_CLIENT_SECRET=...             # the secret never goes in the repo
python -m auditor.cli --live --formato html --salida report.html
```

**Permissions — all read-only:** `Application.Read.All`, `Directory.Read.All`,
`AuditLog.Read.All`. The Graph client exposes only `get()`/`get_all()`; there is no write
path, and `tests/test_readonly_guarantee.py` fails if a Graph write verb appears anywhere.
A missing permission empties one signal rather than failing the whole run.

## Limitations

- **Permission risk is a starting point, not an absolute.** Review the catalog against your
  environment; the reasoning is published next to each level so you can.
- **Abandonment signals depend on Graph reports and licensing.** Where a signal isn't
  available, the tool stays silent rather than assume disuse.
- **It finds over-privilege, not misuse.** An app *can* read all mail; whether it *does* is a
  separate question that needs sign-in and audit-log analysis on top.
- **`--live` is unit-tested with mocked Graph responses.** Validate against your own tenant
  before operational use.

## Contributing

New risk-catalog entries and collectors are welcome — keep collectors read-only and add a
mocked test. Run `pytest -q` and `ruff check .` before a PR.

## License

MIT — see [LICENSE](LICENSE).
