from datetime import date

from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class Devis(models.Model):
    _name = 'groupe_cayla.devis'
    _description = 'Un devis'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _sql_constraints = [
        ('client_id', 'unique (client_id)', 'Ce client a déjà un devis')
    ]
    client_id = fields.Many2one(
        'groupe_cayla.client',
        delegate=False,
        required=True,
    )
    user_id = fields.Many2one(
        'res.users',
        delegate=False,
        required=True,
    )

    numero = fields.Char(required=True)
    date_edition = fields.Date(default=date.today())
    date_acceptation = fields.Date()
    date_envoi = fields.Date()
    date_refus = fields.Date()
    montant = fields.Float()

    entite_edition_id = fields.Many2one(
        'groupe_cayla.entite_edition_devis', required=True
    )

    motif_refus = fields.Text()

    type_octeha = fields.Boolean(string="Oc'teha", default=False)
    type_anah = fields.Boolean(string='ANAH', default=False)
    type_eco_cheque = fields.Boolean(string='Eco-chéque', default=False)
    type_cee = fields.Boolean(string='CEE', default=False)
    type_profesionnel = fields.Boolean(string='Profesionnel', default=False)
    remise = fields.Float(string='Remise (%)')

    objet = fields.Many2one('groupe_cayla.objet_devis', required=False)
    objet_autres = fields.Char()
    autre_1 = fields.Many2one('groupe_cayla.travaux_devis', string='Autre')
    autre_2 = fields.Many2one('groupe_cayla.travaux_devis', string='Autre')
    autre_3 = fields.Many2one('groupe_cayla.travaux_devis', string='Autre')
    choix_tva = fields.Many2one('groupe_cayla.taux_tva', string='Choix TVA')

    quantite_1 = fields.Integer(default=None)
    quantite_2 = fields.Integer(default=None)
    quantite_3 = fields.Integer(default=None)
    prix_unitaire_1 = fields.Float(default=None)
    prix_unitaire_2 = fields.Float(default=None)
    prix_unitaire_3 = fields.Float(default=None)
    tarif_1 = fields.Float(default=None)
    tarif_2 = fields.Float(default=None)
    tarif_3 = fields.Float(default=None)

    _rec_name = 'combination'
    combination = fields.Char(string='Combination', compute='_compute_fields_combination')

    @api.onchange('autre_1')
    def onchange_autre_1(self):
        self.prix_unitaire_1 = self.autre_1.prix_unitaire

    @api.onchange('prix_unitaire_1', 'quantite_1')
    def onchange_prix_unitaire_1(self):
        self.tarif_1 = self.prix_unitaire_1 * self.quantite_1

    @api.onchange('prix_unitaire_2', 'quantite_2')
    def onchange_prix_unitaire_2(self):
        self.tarif_2 = self.prix_unitaire_2 * self.quantite_2

    @api.onchange('prix_unitaire_3', 'quantite_3')
    def onchange_prix_unitaire_3(self):
        self.tarif_3 = self.prix_unitaire_3 * self.quantite_3

    @api.depends('numero')
    def _compute_fields_combination(self):
        for d in self:
            d.combination = 'Devis numéro ' + d.numero

    @api.model
    def create(self, values):
        rec = super(Devis, self).create(values)
        client = self.env['groupe_cayla.client'].search([('id', '=', values['client_id'])], limit=1)
        client.etat = 'attente_commande'
        client.devis_id = rec
        return rec

    @api.multi
    def write(self, vals):
        client = self.client_id
        super().write(vals)
        devis = self.env['groupe_cayla.devis'].search([('id', '=', self.id)], limit=1)
        if devis.date_acceptation:
            client.etat = 'chantier_a_planifier'
        elif devis.date_refus:
            client.etat = 'annule_par_client'
        return True

    @api.onchange('date_refus')
    def onchange_date_refus(self):
        if self.date_refus:
            self.date_acceptation = None

    @api.onchange('date_acceptation')
    def onchange_date_acceptation(self):
        if self.date_acceptation:
            self.date_refus = None
