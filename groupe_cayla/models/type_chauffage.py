import logging

from odoo import models, fields

_logger = logging.getLogger(__name__)


class TypeChauffage(models.Model):
    _name = 'groupe_cayla.type_chauffage'
    _description = 'Type chauffage'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'libelle'

    libelle = fields.Char(required=True)
    source_energie_chauffage_id = fields.Many2one('groupe_cayla.source_energie_chauffage', required=True)
