from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class TauxReversion(models.Model):
    _name = 'groupe_cayla.taux_reversion'
    _description = 'taux reversion'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    _sql_constraints = [
        ('taux_unique', 'unique (u)', 'Un taux existe déjà')
    ]

    u = fields.Integer(default=1, required=True)
    taux = fields.Float(required=True, string='Taux utilisé pour le calcul de la reversion de la prime CEE (par exemple: 1.055)', default=1.055)
    taux_as_char = fields.Char(compute='_compute_taux_as_char', store=False, string='Taux')

    _rec_name = 'taux'


    @api.depends('taux')
    def _compute_taux_as_char(self):
        for t in self:
            if t.taux:
                t.taux_as_char = str(t.taux)