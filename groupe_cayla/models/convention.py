import logging

from odoo import models, fields

_logger = logging.getLogger(__name__)


class Convention(models.Model):
    _name = 'groupe_cayla.convention'
    _description = 'Convention'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'libelle'

    libelle = fields.Char(required=True)
    delegataire_id = fields.Many2one('groupe_cayla.delegataire')
    mention_legale_convention_ids = fields.Many2many('groupe_cayla.mention_legale_convention', required=False, string='Mention légale', relation='groupe_cayla_convention_m2m_mention_legal_rel')