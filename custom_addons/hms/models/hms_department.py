from odoo import fields, models


class HmsDepartment(models.Model):
    _name = 'hms.department'
    _description = "Department"

    name = fields.Char(required=True)
    capacity = fields.Integer()
    is_opened = fields.Boolean(default=True)
    patient_ids = fields.Many2many('hms.patient', string="Patients")
