from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = "res.partner"

    related_patient_id = fields.Many2one("hms.patient", string="Related Patient")

    @api.constrains("email")
    def _check_email_not_in_patient(self):
        for rec in self:
            if rec.email:
                patient = self.env["hms.patient"].search(
                    [("email", "=ilike", rec.email)], limit=1
                )
                if patient:
                    raise ValidationError(
                        _(
                            "The email '%s' already exists for patient '%s'. "
                            "Cannot link a customer with an email used by a patient.",
                            rec.email,
                            patient.full_name,
                        )
                    )

    @api.constrains("vat")
    def _check_vat_required(self):
        for rec in self:
            if not rec.vat:
                raise ValidationError(_("Tax ID is mandatory for customers."))

    def unlink(self):
        for rec in self:
            if rec.related_patient_id:
                raise ValidationError(
                    _(
                        "Cannot delete customer '%s' because it is linked to patient '%s'.",
                        rec.display_name,
                        rec.related_patient_id.full_name,
                    )
                )
        return super(ResPartner, self).unlink()
