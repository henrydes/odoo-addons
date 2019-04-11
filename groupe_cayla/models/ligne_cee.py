from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class LigneCEE(models.Model):
    _name = 'groupe_cayla.ligne_cee'
    _description = 'Une ligne cee'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    cee_id = fields.Many2one('groupe_cayla.cee')

    ligne_devis_id = fields.Many2one('groupe_cayla.ligne_devis', ondelete='cascade')

    sujet_ligne_devis = fields.Char(compute='_compute_ligne_devis_data', store=False)
    quantite_ligne_devis = fields.Integer(compute='_compute_ligne_devis_data', store=False)

    montant_prime_unitaire = fields.Float(required=True)
    montant_prime_total = fields.Float()

    @api.depends('ligne_devis_id')
    def _compute_ligne_devis_data(self):
        for l in self:
            if l.ligne_devis_id:
                l.sujet_ligne_devis = l.ligne_devis_id.sujet_devis_id.libelle
                l.quantite_ligne_devis = l.ligne_devis_id.quantite
            else:
                l.sujet_ligne_devis = None
                l.quantite_ligne_devis = None

    @api.onchange('montant_prime_unitaire')
    def onchange_primeunitaire(self):
        for l in self:
            l.montant_prime_total = l.montant_prime_unitaire * l.quantite_ligne_devis
