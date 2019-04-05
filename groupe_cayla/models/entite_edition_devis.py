from datetime import date

from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class EntiteEditionDevis(models.Model):
    _name = 'groupe_cayla.entite_edition_devis'
    _description = 'Une entité édition devis'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    nom = fields.Char()
    _rec_name = 'nom'
