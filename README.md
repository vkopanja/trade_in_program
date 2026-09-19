# Trade-in Program

An Odoo 16 module for running a device trade-in program. Visitors pick their
device and its condition on a public website page, see the estimated payout
straight away, and send a trade-in request. Support staff then approve or
reject each request in the backoffice.

- **Public request form** at `/trade-in` with a live estimate that updates
  without reloading the page
- **Price list** of devices, each with a base trade-in value, and condition
  grades whose payout percentage marketing can change themselves
- **Review workflow**: requests start as *New*, and staff approve them or
  reject them with a required reason
- **Yearly reference numbers** such as `TI/2026/00017`
- **User and Manager roles**: support processes requests, marketing maintains
  the price list

## Requirements

- Odoo 16.0 (Community is enough)
- Python 3.10 or 3.11
- PostgreSQL 14 or newer
- The `website` module, which is installed automatically as a dependency

No other modules, OCA addons or frontend libraries are used.

## Installation

The repository root *is* the module, so clone it into a directory named
`trade_in_program`. Odoo uses the directory name as the module name, and the
frontend asset path depends on it.

```bash
cd /path/to/custom-addons
git clone <repo-url> trade_in_program

python odoo-bin -c /path/to/odoo.conf -d <database> \
     --addons-path=/path/to/odoo/addons,/path/to/custom-addons \
     -i trade_in_program
```

You can also install it from the UI: enable developer mode, open
**Apps → Update Apps List**, search for *Trade-in Program* and click
**Activate**.

To upgrade after pulling changes:

```bash
python odoo-bin -c /path/to/odoo.conf -d <database> -u trade_in_program
```

### The setup I used

- Odoo 16.0 from the official git repository (`16.0` branch)
- Python 3.11.0 in a pyenv virtualenv
- PostgreSQL 16.8 in Docker

`odoo.conf`:

```ini
[options]
addons_path = /Users/vkopanja/work/odoo/addons,/Users/vkopanja/work/odoo-addons
db_host = localhost
db_port = 5432
db_user = odoo
db_password = <password>
http_port = 8069
```

The exact command, run from the Odoo source directory:

```bash
python odoo-bin -c /Users/vkopanja/work/odoo.conf -d tradeindb -i trade_in_program --dev=xml,reload
```

`--dev=xml` reloads QWeb templates and views from disk. Python changes still
need a restart unless the `watchdog` package is installed.

## Quick start

1. Log in as the administrator. The installation adds the admin to the
   *Trade-In / Manager* group.
2. Open `http://localhost:8069/trade-in`. Choose a device and a condition, and
   the estimate appears (`€315.00` for an *iPhone 14* in *Good* condition, which
   pays 70% of 450). Enter a name and email, then click **Get Offer**.
3. The page shows a confirmation with the reference number, for example
   `TI/2026/00004`.
4. Go to **Trade-In → Trade-In Requests**. The list opens on the *New* filter.
   Open the request and click **Approve**, or **Reject** to enter a reason.

### Demo data

On a database with demo data, the module adds:

- Six devices, plus an archived *iPhone 8* that the website form hides
- Two contacts, Jane Cooper and Tom Novak
- Three requests, one in each state: *New*, *Approved*, and *Rejected* with a
  reason
- *Marc Demo* (login `demo`, password `demo`) as a *Trade-In / User*, to see the
  support view without the Configuration menu

The four conditions are regular data, not demo data, so every database gets
them.

The `/trade-in` page is not added to the website menu automatically. To link
it, go to **Website → Site → Menus**.

## Configuration

### Devices

Go to **Trade-In → Configuration → Devices** (managers only).

| Field               | Meaning |
|---------------------|---------|
| Device Name         | Name shown to customers, e.g. *Samsung Galaxy S21* |
| Base Trade-In Value | Payout for a device in *Like New* condition (100%) |
| Active              | Archived devices disappear from the website form and can no longer be quoted or submitted. With no active devices, the page says that trade-ins are not accepted at the moment. |

### Conditions

Go to **Trade-In → Configuration → Conditions** (managers only). The list is
edited in place: change a name or payout directly in the row, and drag the
handle to change the order in which conditions appear on the website.

The payout is shown and entered as a percentage and must be between 0% and
100%. The module installs these defaults:

| Condition | Payout |
|-----------|-------:|
| Like New  | 100%   |
| Good      | 70%    |
| Damaged   | 40%    |
| Broken    | 10%    |

The defaults are loaded with `noupdate="1"`, so your edits survive module
upgrades.

## How offers are calculated

```
offer value = device base trade-in value × condition payout
```

The calculation lives in one method, `trade_in_program.trade_in._calculate_offer`.
Both the website estimate and the stored offer on each request use it. The
browser only ever sends a device ID and a condition ID, never a price.

When a request is created, the device's base value and the condition's payout
are copied onto it, and the offer is computed from those copies. Later changes
to the price list do not change requests that already exist.

## Review workflow

```
New ──Approve──▶ Approved
 │
 └──Reject (reason required)──▶ Rejected
```

- **Approve** and **Reject** are in the form header and in the list rows. Both
  only work on *New* requests. The buttons are hidden once a request is
  decided, and the server refuses the action even if a stale page sends it.
- **Reject** opens a dialog that asks for a reason. The status and the reason
  are saved together, so cancelling the dialog leaves the request unchanged.
- A constraint on the model also requires a reason on every *Rejected*
  request, whichever way it is written.
- Once a request is decided, its customer and device fields become read-only.

## Customers and contacts

The website form looks up an existing contact by email (case-insensitive) and
creates one when none matches. Each request stores the name and email exactly
as the customer entered them, plus a link to that contact.

When staff create a request in the backoffice, the name and email are filled
in from the chosen contact and can be edited.

Contact forms have a **Trade-Ins** smart button with the number of requests
linked to that contact. It opens all of them, whatever their state, and only
Trade-In users and managers see it.

## Reference numbers

References come from the `trade_in_program.trade_in` sequence, with the prefix
`TI/<year>/` and 5-digit padding. The counter restarts every year. You can
change the sequence under **Settings → Technical → Sequences & Identifiers →
Sequences** (developer mode). It is loaded
with `noupdate="1"`, so your changes survive upgrades.

## Access rights

| Group                  | Requests                           | Devices and conditions | Menus |
|------------------------|------------------------------------|------------------------|-------|
| Trade-In / User        | Read, create, edit, approve, reject | Read only              | Trade-In Requests |
| Trade-In / Manager     | Everything, including delete       | Everything             | Also Configuration |
| Other internal users, portal and public users | No access | No access  | None |

Assign roles under **Settings → Users & Companies → Users → Access Rights**,
in the *Trade-In* dropdown of the *Other* section.

Website visitors never get access to the models. The public routes use
`sudo()` only for specific steps, after validating the input: listing active
devices and conditions, computing a quote, finding or creating the contact,
and creating the request.

## HTTP routes

| Route              | Type | Method | Auth   | Purpose |
|--------------------|------|--------|--------|---------|
| `/trade-in`        | http | GET    | public | Renders the form. `?submitted=<token>` shows the confirmation with the reference of the request created from that form. |
| `/trade-in/submit` | http | POST   | public | Validates the input. On errors it shows the form again with messages and the entered values. On success it creates the request and redirects to `/trade-in?submitted=<token>`. CSRF-protected. |
| `/trade-in/quote`  | json | POST   | public | Returns the estimated offer for a device and condition. |

Example quote request:

```bash
curl -s http://localhost:8069/trade-in/quote \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc": "2.0", "method": "call", "params": {"device_id": 1, "condition_id": 2}}'
```

```json
{"jsonrpc": "2.0", "id": null, "result": {"ok": true, "value": 315.0}}
```

On a new database with demo data, device 1 is the *iPhone 14* (450) and
condition 2 is *Good* (70%).

The result is `{"ok": false}` when the device or condition does not exist, or
when the device is archived.

## Data model

| Model                            | Purpose |
|----------------------------------|---------|
| `trade_in_program.device`        | Devices that can be traded in, each with a base value. Can be archived. |
| `trade_in_program.condition`     | Condition grades, their payout (stored as a fraction, 0.7 = 70%) and display order |
| `trade_in_program.trade_in`      | Trade-in requests: reference, customer name and email, contact, device, condition, copied base value and payout, stored `offer_value`, `state`, rejection reason and the submission token |
| `trade_in_program.reject.wizard` | Temporary dialog that collects a rejection reason |

## Design decisions

- **Copy the price onto the request.** The PDF asks for the value "as
  calculated at submission time". Copying the base value and payout, then
  computing the offer from the copies, keeps old requests stable when
  marketing changes prices, while every offer is still produced by the same
  method.
- **Store the payout as a fraction, show it as a percentage.** The calculation
  stays a plain multiplication, Odoo's `percentage` widget handles display and
  entry, and a database `CHECK` keeps it between 0% and 100%.
- **Keep the customer's own details on the request.** The request stores the
  name and email as typed, next to the contact link. If an email matches an
  existing contact, the typed name is not lost, and staff can see when the
  submitted details differ from the contact.
- **A plain `state` selection.** `new` / `approved` / `rejected` in a
  module-level constant, following Odoo's convention for workflow fields. The
  same values appear as plain strings in the views, so an Enum would only have
  covered the Python side.
- **A wizard for rejections.** Writing the status and the reason in one step
  means a rejected request can never be saved without a reason, and a model
  constraint covers any other way of writing the status.
- **An `ir.sequence` for references.** It restarts every year through a date
  range and staff can adjust it without code. I kept the default
  implementation, which can leave gaps, instead of the gap-free one, which
  locks the sequence row on every submission of a public form.
- **Two roles instead of one.** The PDF requires a manager group. A separate
  user group means someone who processes requests cannot change the prices
  that decide the payout, and employees outside the program cannot see
  customers' details.
- **Validate on the server, show errors in the page.** Name (required, at most
  100 characters), email format, an active device and an existing condition
  are checked on the server. On errors the form is rendered again with the
  messages and entered values. On success the browser is redirected, so a
  refresh never resubmits. The browser also checks required fields, the email
  format and the name length, but only for convenience.
- **Two routes for the form.** `GET /trade-in` shows the form and
  `POST /trade-in/submit` handles it. After a validation error the address
  bar therefore shows `/trade-in/submit`; I preferred that to one route that
  handles both methods.
- **Double-submit protection on both sides.** The submit button is disabled
  while sending. Each rendered form also carries a one-time token that is
  stored on the request under a unique constraint. Sending the same form
  again redirects to the request that already exists. If two copies arrive at
  the same moment, the second fails on the constraint inside a savepoint and
  is redirected to the same result. The confirmation page looks the reference
  up by that token instead of repeating a value from the URL.
- **Archived devices are filtered by the ORM.** Devices are looked up with
  `search()`, which skips archived records, and the quote and submit routes
  share the same helper, so they cannot disagree.
- **Frontend code in the asset bundle.** The live estimate and button handling
  are a `publicWidget`, and the page's few styles are a small SCSS file. Both
  are registered in `web.assets_frontend`, with no script or style in the
  template. The styles are scoped under `.o_trade_in` and use Bootstrap
  variables, so they follow the website theme and cannot affect other pages.
- **An empty state instead of an empty form.** When no device is active, or no
  condition exists, the page shows a short message instead of a form that
  cannot be submitted.

## Known limitations

- **Duplicate submits that arrive at the same moment log an error.** The
  duplicate is blocked and the customer sees the normal confirmation, but
  Odoo logs one `duplicate key … submission_token_unique` error line per
  blocked copy.
- **Reference numbers can have gaps.** The standard sequence can skip numbers,
  and a blocked simultaneous duplicate also uses up a number.
- **First submissions of a new year.** Odoo creates each year's sequence range
  the first time a number is drawn. If several requests arrive at exactly
  that moment, all but one fail with an error. This is Odoo core behaviour and
  affects any yearly sequence.
- **Contacts are matched by email only.** Anyone can type an existing
  contact's email, and the request is linked to that contact. Nothing is
  exposed to the visitor, and the request keeps the typed name and email so
  staff can spot the mismatch, but emails are not verified.
- **Fixed currency.** The website shows estimates with a € sign, but values are
  stored as plain numbers, not as monetary amounts in the company currency.
- **No spam protection** such as reCAPTCHA on the public form.
- **One message for both dropdowns.** An invalid device or condition shows the
  same message under both fields.
- **Estimate errors are silent.** If the quote request fails, the estimate
  stays at `-` without a message.
- **Messages are not translatable.** User-facing strings in the controller are
  not wrapped for translation.
- **No *Archived* filter for devices.** Archived devices can only be found
  with a custom filter.

## What I would do with another day

- Automated tests: `TransactionCase` for the pricing and the review workflow,
  `HttpCase` for the page, validation and double submits
- A confirmation email to the customer through a `mail.template`
- Chatter and tracking on requests, so the history of each decision is visible
- A monetary field in the company currency instead of plain numbers
- reCAPTCHA on the public form, using the `google_recaptcha` module that
  `website` already installs
- Show quote errors in the page and ignore out-of-date quote responses
- Separate messages for the device and condition fields
- A device search view with an *Archived* filter
- Translatable messages and a `.po` file for a second language
- A portal page (`/my/trade-ins`) where customers follow their requests

## AI assistance

I used Claude (Anthropic) as an assistant throughout the project:

- **Written by the assistant and reviewed by me:** the request form header,
  statusbar and search view; the user and manager groups with their access
  rules and menus; the double-submit protection (token, savepoint and button
  handling); the percentage-based condition list, the `state` rename and the
  stored customer details; the demo data; the smart button on contacts; the
  stylesheet and empty-state message; and this README.
- **Written by me with the assistant's guidance and reviews:** the yearly
  reference sequence, the reject wizard, the switch to the website layout,
  and the server-side validation in the controller and template.
- **Also used for:** comparing the module against the assignment, explaining
  Odoo concepts, and debugging, for example the missing `website=True` on the
  submit route.

## Module layout

```
trade_in_program/
├── __manifest__.py
├── controllers/controllers.py        # /trade-in, /trade-in/submit, /trade-in/quote
├── data/ir_sequence_data.xml         # TI/<year>/ reference sequence
├── demo/demo.xml                     # devices, contacts, example requests, Marc Demo's role
├── models/
│   ├── condition.py                  # condition grades and payout
│   ├── device.py
│   ├── res_partner.py                # Trade-Ins count and smart button action on contacts
│   └── trade_in.py                   # requests: state, pricing, approve/reject
├── security/
│   ├── trade_in_security.xml         # Trade-In category, User and Manager groups
│   └── ir.model.access.csv
├── static/src/
│   ├── js/trade_in_form.js           # live estimate and submit button handling
│   └── scss/trade_in.scss            # estimate box and phone-width submit button
├── views/
│   ├── condition_views.xml           # also installs the default conditions
│   ├── device_views.xml
│   ├── res_partner_views.xml         # adds the smart button to the contact form
│   ├── trade_in_customer_templates.xml
│   ├── trade_in_menus.xml
│   └── trade_in_views.xml
└── wizard/
    ├── trade_in_reject_wizard.py
    └── trade_in_reject_wizard_views.xml
```

## License

LGPL-3. Author: Vedran Kopanja.
