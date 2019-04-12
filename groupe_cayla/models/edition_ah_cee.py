from datetime import date

from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class EditionAhCEE(models.Model):
    _name = 'groupe_cayla.edition_ah_cee'
    _description = 'Fiche ah CEE'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _sql_constraints = [
        ('cee_id', 'unique (cee_id)', 'Ce dossier CEE a déjà une fiche AH')
    ]

    cee_id = fields.Many2one('groupe_cayla.cee',required=True,ondelete='cascade')
    user_id = fields.Many2one('res.users',required=True,string='Utilisateur')
    date_edition = fields.Date(default=date.today())

    _rec_name = 'combination'
    combination = fields.Char(string='Combination', compute='_compute_fields_combination')

    @api.depends('user_id', 'date_edition')
    def _compute_fields_combination(self):
        for d in self:
            d.combination = 'Editée par '+d.user_id.name+' le '+str(d.date_edition)
