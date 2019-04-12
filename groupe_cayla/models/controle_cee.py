from datetime import date

from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class ControleCEE(models.Model):
    _name = 'groupe_cayla.controle_cee'
    _description = 'Controle CEE'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _sql_constraints = [
        ('cee_id', 'unique (cee_id)', 'Ce dossier CEE a déjà une fiche contrôle')
    ]

    cee_id = fields.Many2one('groupe_cayla.cee',required=True,ondelete='cascade')
    user_id = fields.Many2one('res.users',required=True,string='Utilisateur')
    date_reception = fields.Date()
    date_controle = fields.Date(default=date.today())
    fiche_vt = fields.Boolean(default=False, string='Fiche de VT')
    devis = fields.Boolean(default=False, string='Devis')
    ah = fields.Boolean(default=False, string='AH')
    fiche_chantier = fields.Boolean(default=False, string='Fiche de CH')
    dossier_valide = fields.Boolean(default=False, string='DOSS. VALIDE')

    _rec_name = 'combination'
    combination = fields.Char(string='Combination', compute='_compute_fields_combination')

    @api.depends('user_id', 'date_reception')
    def _compute_fields_combination(self):
        for d in self:
            d.combination = 'Contrôlé '+ ('VALIDE' if d.dossier_valide else 'INCOMPLET')+ ' par '+d.user_id.name+' le '+str(d.date_controle)

    @api.model
    def create(self, values):
        rec = super(ControleCEE, self).create(values)
        cee = self.env['groupe_cayla.cee'].search([('id', '=', values['cee_id'])], limit=1)

        if values['dossier_valide'] is True:
            cee.client_id.etat = 'dossier_a_deposer'
        else:
            cee.client_id.etat = 'dossier_incomplet'
        return rec

    @api.multi
    def write(self, values):
        client = self.cee_id.client_id
        result = super().write(values)
        controle_cee = self.env['groupe_cayla.controle_cee'].search([('id', '=', self.id)], limit=1)
        if controle_cee.dossier_valide:
            client.etat = 'dossier_a_deposer'
        else:
            client.etat = 'dossier_incomplet'
        return result