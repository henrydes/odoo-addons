# -*- coding: utf-8 -*-

from odoo import models, fields, api

class groupe_cayla(models.Model):
    _name = 'groupe_cayla.groupe_cayla'

    name = fields.Char()
    value = fields.Integer()
    value2 = fields.Float(compute="_value_pc", store=True)
    description = fields.Text()

    @api.depends('value')
    def _value_pc(self):
        self.value2 = float(self.value) / 100