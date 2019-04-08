from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class LigneChantier(models.Model):
    _name = 'groupe_cayla.ligne_chantier'
    _description = 'Une ligne chantier'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    chantier_id = fields.Many2one('groupe_cayla.chantier')

    type_produit = fields.Char()
    marque_produit = fields.Char()
    nb_sacs = fields.Integer()
    temps_passe = fields.Integer(string='Temps passé en heures, nombre entier')

