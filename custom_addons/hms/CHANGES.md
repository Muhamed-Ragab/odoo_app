# HMS Module — Changes Documentation

## Overview
Implementation of Hospitals Management System (HMS) enhancements: patient email, CRM customer linking, constraints, and view updates.

---

## 1. Patient Email Field (`models/hms_patient.py`)

### What changed
- **Import**: Added `tools` to imports (line 3)
- **New field**: `email = fields.Char(string="Email")` (line 34)
- **SQL constraint**: `UNIQUE(email)` ensures database-level uniqueness (lines 37-40)
- **Validation**: `@api.constrains("email")` method validates email format using `tools.email_normalize_all()` (lines 90-95)

### How it works
- When a patient is created or email is modified, the SQL constraint ensures no duplicate emails exist across patients
- The Python constraint normalizes the email — if the normalization returns an empty list, the email is invalid and a `ValidationError` is raised
- `tools.email_normalize_all` is Odoo's built-in email normalizer that strips whitespace, lowercases, and validates format

---

## 2. Customer-Patient Link (`models/res_partner.py`) — NEW FILE

This file inherits `res.partner` (the customer/contact model) and adds:

### `related_patient_id` field
```python
related_patient_id = fields.Many2one("hms.patient", string="Related Patient")
```
- Many2one relationship linking a customer to a patient
- Shown in the **Misc** group inside the **Sales & Purchase** tab (via view inheritance)

### Constraint: no duplicate email between patient and customer
```python
@api.constrains("email")
def _check_email_not_in_patient(self):
```
- When a customer's email is set/changed, it searches `hms.patient` for a matching email
- If found, raises `ValidationError` — prevents linking a customer with an email that already belongs to a patient

### Constraint: Tax ID is mandatory
```python
@api.constrains("vat")
def _check_vat_required(self):
```
- Enforces that Tax ID (`vat` field) must be provided for all customers
- Raises `ValidationError` if empty

### Delete protection
```python
def unlink(self):
```
- Overrides the base `unlink()` method
- Before deleting any customer, checks if it has a `related_patient_id`
- If linked to a patient, deletion is blocked with a `ValidationError`

---

## 3. View Updates

### Patient form view (`views/hms_patient_views.xml`)
- Added `email` field between `last_name` and `birthdate` in the first group column

### Patient tree view (`views/hms_patient_views.xml`)
- Added `email` field after `full_name` in the list

### Customer form view (`views/res_partner_views.xml`) — NEW FILE
- Inherits `base.view_partner_form`
- Inserts `related_patient_id` field **after** the `ref` field — which places it inside the **Misc** group within the **Sales & Purchase** tab

### Customer tree view (`views/res_partner_views.xml`)
- Inherits `base.view_partner_tree`
- Adds `website` field **after** the `email` column in the list view

---

## 4. Module Manifest (`__manifest__.py`)

### Dependencies
```python
"depends": ["base", "crm"],
```
- Added `crm` dependency because we're extending the CRM customer model (`res.partner`)
- `crm` is a core Odoo module that inherits `res.partner` with CRM-specific fields

### Data files
```python
"data": [
    ...
    "views/res_partner_views.xml",
],
```
- Added the new partner views file to the data list

---

## 5. Models Init (`models/__init__.py`)

Added import for the new file:
```python
from . import res_partner
```

---

## Summary of Requirements Coverage

| # | Requirement | Location |
|---|-------------|----------|
| 1 | Email field on patient (valid + unique) | `hms_patient.py` — field, SQL constraint, format validation |
| 2 | `related_patient_id` in Misc group | `res_partner.py` + `res_partner_views.xml` |
| 3 | Age auto-calculated from birthdate | Already existed (`hms_patient.py:68-81`) |
| 4 | Constraint: customer email ≠ patient email | `res_partner.py:10-25` |
| 5 | Prevent deletion of customer linked to patient | `res_partner.py:33-42` |
| 6 | Website in customer list view | `res_partner_views.xml:21-23` |
| 7 | Tax ID mandatory for customers | `res_partner.py:27-31` |
