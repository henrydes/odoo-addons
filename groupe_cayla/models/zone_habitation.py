import logging

from odoo import models, fields

_logger = logging.getLogger(__name__)


class ZoneHabitation(models.Model):
    _name = 'groupe_cayla.zone_habitation'
    _description = 'Zone Habitation'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'libelle'

    libelle = fields.Char(required=True)
