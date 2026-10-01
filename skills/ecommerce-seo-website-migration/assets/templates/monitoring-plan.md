# Monitoring plan: <site>

| Period | Checks | Cadence | Owner |
| --- | --- | --- | --- |
| Cutover | Production smoke checks: availability, priority redirects, indexing controls, canonicals, sitemaps, tracking | Once, immediately | <name> |
| Early stabilisation | Redirect failures, errors, indexing and canonical changes on priority groups | <e.g. daily; set to inventory size and risk> | <name> |
| Processing | Clicks, impressions, CTR, position, visits, orders, revenue by mapped page group and segment | <e.g. weekly> | <name> |
| Long term | Redirect retention (generally at least a year), new 404s, link hygiene | <e.g. monthly> | <name> |

## Segments
Page type, locale, country, device, branded and non-branded queries, as far as the data allows.

## Comparison method
Mapped page groups (each old URL with its new URL), equal-length periods, the same filters and definitions as the
baseline. Overlapping exports are not double-counted.

## Alerts
| Page group | Metric | Normal variation in the baseline | Alert when | Who is told |
| --- | --- | --- | --- | --- |
| <group> | <metric> | <range> | <threshold set from that variation and the group's importance> | <name> |

Thresholds are configuration choices tied to this baseline, not universal rules.
