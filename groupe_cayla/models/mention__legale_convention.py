from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class MentionLegaleConvention(models.Model):
    _name = 'groupe_cayla.mention_legale_convention'
    _description = 'Mention légale convention'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    convention_ids = fields.Many2many('groupe_cayla.convention', required=True, string='Conventions', relation='groupe_cayla_convention_m2m_mention_legal_rel')

    mention = fields.Char('Mention')
    date_debut = fields.Date('Début validité', required=True)
    date_fin = fields.Date('Fin validité')

    _rec_name = 'combination'
    combination = fields.Char(string='Combination', compute='_compute_fields_combination')

    @api.depends('mention', 'date_debut', 'date_fin')
    def _compute_fields_combination(self):
        for d in self:
            if d.date_fin:
                d.combination = 'Mention "' + d.mention + '" valable du ' + str(d.date_debut) + ' au ' + str(d.date_fin)
            else:
                d.combination = 'Mention "' + d.mention + '" valable à partir du ' + str(d.date_debut)
