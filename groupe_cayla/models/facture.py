from datetime import date

from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class Facture(models.Model):
    _name = 'groupe_cayla.facture'
    _description = 'Facture'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    client_id = fields.Many2one('groupe_cayla.client',required=True,ondelete='cascade')
    user_id = fields.Many2one('res.users',required=True,string='Utilisateur')

    acompte = fields.Float(related='client_id.devis_id.acompte', store=False)
    reglement_chantier = fields.Float(related='client_id.chantier_id.reglement', store=False)
    reglement_facture = fields.Float()
    numero = fields.Char()
    solde = fields.Float(related='client_id.solde_client', store=False)

    combination = fields.Char(string='Combination', compute='_compute_fields_combination')
    _rec_name = 'combination'

    @api.depends('numero')
    def _compute_fields_combination(self):
        for d in self:
            d.combination = 'Facture numéro ' + str(d.numero)

    @api.model
    def create(self, values):
        rec = super(Facture, self).create(values)
        devis = self.env['groupe_cayla.client'].search([('id', '=', values['client_id'])], limit=1).devis_id
        if devis:
            devis.etat = 'valide'
        return rec
