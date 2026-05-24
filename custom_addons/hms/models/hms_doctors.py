from odoo import fields, models


class HmsDoctors(models.Model):
    _name = 'hms.doctors'
    _description = "Doctor"

    first_name = fields.Char(required=True)
    last_name = fields.Char(required=True)
    image = fields.Image()
