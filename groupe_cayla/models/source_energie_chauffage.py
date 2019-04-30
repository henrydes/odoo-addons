import logging

from odoo import models, fields

_logger = logging.getLogger(__name__)


class SourceEnergieChauffage(models.Model):
    _name = 'groupe_cayla.source_energie_chauffage'
    _description = 'Source energie chauffage'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'libelle'

    libelle = fields.Char(required=True)
    types_chauffage_id = fields.One2many('groupe_cayla.type_chauffage', 'source_energie_chauffage_id')
