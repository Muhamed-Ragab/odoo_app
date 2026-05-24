from datetime import date

from odoo import _, api, fields, models, tools
from odoo.exceptions import ValidationError


class HmsPatient(models.Model):
  _name = "hms.patient"
  _description = "Patient"
  _order = "create_date DESC"

  first_name = fields.Char(required=True)
  last_name = fields.Char(required=True)
  full_name = fields.Char(compute="_compute_full_name", string="Full Name")
  birthdate = fields.Date()
  history = fields.Html()
  cr_ratio = fields.Float(string="CR Ratio")
  blood_type = fields.Selection(
      [
          ("A+", "A+"),
          ("A-", "A-"),
          ("B+", "B+"),
          ("B-", "B-"),
          ("AB+", "AB+"),
          ("AB-", "AB-"),
          ("O+", "O+"),
          ("O-", "O-"),
      ],
      string="Blood Type",
  )
  pcr = fields.Boolean(string="PCR")
  image = fields.Image()
  address = fields.Text()
  email = fields.Char(string="Email")
  age = fields.Integer(compute="_compute_age", store=True)

  _unique_email = models.Constraint(
      "UNIQUE(email)",
      "The email address must be unique across all patients.",
  )

  department_ids = fields.Many2many("hms.department", string="Departments")
  doctor_ids = fields.Many2many("hms.doctors", string="Doctors")
  log_ids = fields.One2many("hms.patient.log", "patient_id", string="Logs")
  state = fields.Selection(
      [
          ("undetermined", "Undetermined"),
          ("good", "Good"),
          ("fair", "Fair"),
          ("serious", "Serious"),
      ],
      default="undetermined",
      string="State",
  )

  @api.depends("first_name", "last_name")
  def _compute_full_name(self):
    for rec in self:
      if rec.first_name and rec.last_name:
        rec.full_name = f"{rec.first_name} {rec.last_name}"
      elif rec.first_name:
        rec.full_name = rec.first_name
      elif rec.last_name:
        rec.full_name = rec.last_name
      else:
        rec.full_name = ""

  @api.depends("birthdate")
  def _compute_age(self):
    today = date.today()
    for rec in self:
      if rec.birthdate:
        rec.age = (
            today.year
            - rec.birthdate.year
            - (
                (today.month, today.day)
                < (rec.birthdate.month, rec.birthdate.day)
            )
        )
      else:
        rec.age = 0

  @api.constrains("pcr", "cr_ratio")
  def _check_pcr_cr_ratio(self):
    for rec in self:
      if rec.pcr and not rec.cr_ratio:
        raise ValidationError(_("CR Ratio is required when PCR is checked."))

  @api.constrains("email")
  def _check_email_validity(self):
    for rec in self:
      if rec.email:
        if not tools.email_normalize_all(rec.email):
          raise ValidationError(_("The email '%s' is not valid.", rec.email))

  @api.onchange("birthdate")
  def _onchange_birthdate_pcr(self):
    if self.birthdate:
      today = date.today()
      age = (
          today.year
          - self.birthdate.year
          - (
              (today.month, today.day)
              < (self.birthdate.month, self.birthdate.day)
          )
      )
      if age < 30:
        self.pcr = True
        return {
            "warning": {
                "title": _("PCR Auto-Checked"),
                "message": _(
                    "PCR has been automatically checked because the patient is under 30 years old."
                ),
            }
        }

  @api.model_create_multi
  def create(self, vals_list):
    patients = super(HmsPatient, self).create(vals_list)
    for patient in patients:
      self.env["hms.patient.log"].sudo().create(
          {
              "created_by": self.env.user.id,
              "date": fields.Datetime.now(),
              "description": _("Patient created"),
              "patient_id": patient.id,
          }
      )
    return patients

  def write(self, vals):
    res = super(HmsPatient, self).write(vals)
    if "state" in vals:
      for rec in self:
        self.env["hms.patient.log"].sudo().create(
            {
                "created_by": self.env.user.id,
                "date": fields.Datetime.now(),
                "description": _(
                    "State changed to %s",
                    dict(rec._fields["state"].selection).get(rec.state),
                ),
                "patient_id": rec.id,
            }
        )
    return res
