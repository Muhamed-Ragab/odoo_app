from odoo import _, fields, models
from odoo.exceptions import AccessError


class PatientLog(models.Model):
  _name = 'hms.patient.log'
  _description = "Patient Log"
  _order = "date DESC"

  created_by = fields.Many2one(
    'res.users', string="Created By", default=lambda self: self.env.user, readonly=True)
  date = fields.Datetime(default=fields.Datetime.now, readonly=True)
  description = fields.Text(readonly=True)
  patient_id = fields.Many2one(
    'hms.patient', string="Patient", required=True, ondelete='cascade', readonly=True)

  def write(self, vals):
    raise AccessError(_("Patient logs cannot be modified once created."))

  def unlink(self):
    raise AccessError(_("Patient logs cannot be deleted once created."))
