# Trade-in Program

An Odoo 16 module for running a device trade-in program. Customers request a
trade-in offer from a public website form and see an estimated value right
away. Staff then review each request in the back office and approve or reject
it.

- **Public request form** at `/trade-in` that shows a live quote as the customer
  picks a device and condition
- **Price list** of devices, each with a base trade-in value, plus condition
  multipliers (Like New, Good, Damaged, Broken)
- **Review workflow**: requests start as *New*. Staff approve them, or reject
  them with a required reason.
- **Yearly reference numbers** such as `TI/2026/00001`
- Customers are matched to existing contacts by email, and a new contact is
  created when none matches

## Requirements

- Odoo 16.0
- The `website` module, which is installed automatically as a dependency

## Installation

The repository root *is* the module, so clone it into a directory named
`trade_in_program`. Odoo uses the directory name as the module name, and the
frontend asset path depends on it.

```bash
cd /path/to/custom-addons
git clone <repo-url> trade_in_program

odoo -c /etc/odoo/odoo.conf -d <database> \
     --addons-path=/path/to/odoo/addons,/path/to/custom-addons \
     -i trade_in_program
```

You can also install it from the UI. Enable developer mode, open **Apps →
Update Apps List**, search for *Trade-in Program* and click **Activate**.

To upgrade after pulling changes:

```bash
odoo -c /etc/odoo/odoo.conf -d <database> -u trade_in_program
```

## Quick start

1. Go to **Trade-In → Devices**, click **New** and add a device, for example
   *iPhone 12* with a base trade-in value of `400`. The module ships no demo
   data, so the form stays empty until you add at least one device.
2. Open `http://localhost:8069/trade-in`. Choose the device and a condition,
   and the estimated value appears (`280.00` for *Good*). Enter a name and
   email, then click **Get Offer**.
3. The page shows a confirmation with the reference number, for example
   `TI/2026/00001`.
4. Go to **Trade-In → Trade-Ins**, find the request and click ✓ to approve it or
   ✕ to reject it.

The `/trade-in` page is not added to the website menu automatically. To link it,
go to **Website → Site → Menus**.

## Configuration

### Devices

Go to **Trade-In → Devices**.

| Field                | Meaning                                                   |
|----------------------|-----------------------------------------------------------|
| Device Name          | Name shown to customers, e.g. *Samsung Galaxy S21*        |
| Base Trade-In Value  | Offer for a device in *Like New* condition (multiplier 1.0) |
| Active               | Archived devices disappear from the form and return no quote |

### Conditions

Go to **Trade-In → Conditions**. The module installs these defaults:

| Condition | Multiplier |
|-----------|-----------:|
| Like New  | 1.0        |
| Good      | 0.7        |
| Damaged   | 0.4        |
| Broken    | 0.1        |

The defaults are loaded with `noupdate="1"`, so your edits survive module
upgrades.

## How offers are calculated

```
offer value = device base trade-in value × condition multiplier
```

When a request is created, the device's base value and the condition's
multiplier are copied onto it. Later changes to the price list do not change
offers that already exist. Values are plain numbers with no currency attached.

## Review workflow

```
New ──Approve──▶ Accepted
 │
 └──Reject (reason required)──▶ Rejected
```

- **Approve** (✓ in the list view) sets the status to *Accepted* and clears any
  rejection reason.
- **Reject** (✕) opens a dialog that asks for a reason. Only *New* requests can
  be rejected.
- A constraint requires a rejection reason on every *Rejected* request.

## Reference numbers

References come from the `trade_in_program.trade_in` sequence, with the prefix
`TI/<year>/` and 5-digit padding. The counter restarts every year.

> If you change the prefix, also update `REFERENCE_RE` in
> `controllers/controllers.py`. That pattern checks the reference before the
> confirmation page displays it, so a changed prefix makes the confirmation
> message disappear.

## HTTP routes

| Route                 | Type | Method | Auth   | Purpose |
|-----------------------|------|--------|--------|---------|
| `/trade-in`           | http | GET    | public | Renders the request form. `?submitted=<reference>` shows the confirmation and `?error=email` / `?error=invalid` shows an error. |
| `/trade-in/submit`    | http | POST   | public | Validates the input, finds or creates the contact, creates the trade-in and redirects back to `/trade-in`. CSRF-protected. |
| `/trade-in/quote`     | json | POST   | public | Returns the estimated offer for a device and condition. |

Example quote request:

```bash
curl -s http://localhost:8069/trade-in/quote \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc": "2.0", "method": "call", "params": {"device_id": 1, "condition_id": 2}}'
```

```json
{"jsonrpc": "2.0", "id": null, "result": {"ok": true, "value": 280.0}}
```

The result is `{"ok": false}` when the device or condition does not exist, or
when the device is archived.

## Data model

| Model                            | Purpose |
|----------------------------------|---------|
| `trade_in_program.device`        | Devices that can be traded in, each with a base value |
| `trade_in_program.condition`     | Condition names and their multipliers |
| `trade_in_program.trade_in`      | Trade-in requests: customer, device, condition, stored base value and multiplier, computed `offer_value`, `reference`, `status`, `rejection_reason` |
| `trade_in_program.reject.wizard` | Transient dialog that collects a rejection reason |

## Access rights

All internal users (`base.group_user`) can read, create, edit and delete
devices, conditions and trade-in requests. The module has no separate manager
group yet. Website visitors never access the models directly. The public
controllers read and write through `sudo()`.

## Module layout

```
trade_in_program/
├── __manifest__.py
├── controllers/controllers.py        # /trade-in, /trade-in/submit, /trade-in/quote
├── data/ir_sequence_data.xml         # TI/<year>/ reference sequence
├── demo/demo.xml                     # placeholder, no demo records
├── models/
│   ├── condition.py
│   ├── device.py
│   └── trade_in.py                   # Status enum, offer computation, actions
├── security/ir.model.access.csv
├── static/src/js/trade_in_form.js    # live quote widget for the public form
├── views/
│   ├── condition_views.xml           # also seeds the default conditions
│   ├── device_views.xml
│   ├── trade_in_customer_templates.xml
│   ├── trade_in_menus.xml
│   └── trade_in_views.xml
└── wizard/
    ├── trade_in_reject_wizard.py
    └── trade_in_reject_wizard_views.xml
```

## License

LGPL-3. Author: Vedran Kopanja.
