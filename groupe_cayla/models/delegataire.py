import logging

from odoo import models, fields

_logger = logging.getLogger(__name__)


class Delegataire(models.Model):
    _name = 'groupe_cayla.delegataire'
    _description = 'Délégataire'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'nom'

    nom = fields.Char(required=True)
    adresse_facturation = fields.Text(required=True)
