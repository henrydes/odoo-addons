from datetime import date

from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class CEE(models.Model):
    _name = 'groupe_cayla.cee'
    _description = 'Un dossier CEE'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _sql_constraints = [
        ('client_id', 'unique (client_id)', 'Ce client a déjà un dossier CEE')
    ]

    client_id = fields.Many2one(
        'groupe_cayla.client',
        required=True,
        ondelete='cascade'
    )
    user_id = fields.Many2one(
        'res.users',
        delegate=False,
        required=True,
    )

    lignes_cee = fields.One2many('groupe_cayla.ligne_cee', 'cee_id', string='Lignes')


    devis_id = fields.Many2one('groupe_cayla.devis', store=False, compute='_compute_devis')
    type_client_id = fields.Many2one('groupe_cayla.type_client', required=True)
    zone_habitation_id = fields.Many2one('groupe_cayla.zone_habitation', required=True)
    type_chauffage_id = fields.Many2one('groupe_cayla.type_chauffage', required=True)
    source_energie_chauffage = fields.Char(compute='_compute_source_energie_chauffage', store=False)

    convention_id = fields.Many2one('groupe_cayla.convention', required=True)
    fiche_1_id = fields.Many2one('groupe_cayla.fiche', required=True, string='Fiche')
    fiche_2_id = fields.Many2one('groupe_cayla.fiche', required=True, string='Fiche')

    objet_devis = fields.Char(compute='_compute_devis_data', store=False)

    ref_fiscale = fields.Char(required=True)
    foyer = fields.Integer(required=True)
    locataire = fields.Boolean(string='Locataire ?', required=True)

    @api.depends('type_chauffage_id')
    def _compute_source_energie_chauffage(self):
        for c in self:
            if c.type_chauffage_id:
                c.source_energie_chauffage = c.type_chauffage_id.source_energie_chauffage_id.libelle

    @api.depends('client_id')
    def _compute_devis(self):
        for c in self:
            if c.client_id:
                if c.client_id.devis_id:
                    c.devis_id = c.client_id.devis_id
                else:
                    c.devis_id = None

    @api.depends('devis_id')
    def _compute_devis_data(self):
        for c in self:
            if c.devis_id:
                c.objet_devis = c.devis_id.objet.libelle
            else:
                c.objet_devis = None

    @api.onchange('type_client_id', 'zone_habitation_id', 'convention_id', 'type_chauffage_id')
    def onchange_cee_data(self):
        if self.type_client_id and self.zone_habitation_id and self.convention_id and self.lignes_cee:
            for l in self.lignes_cee:
                if l.ligne_devis_id:
                    sujet = l.ligne_devis_id.sujet_devis_id
                    if l.cee_id.type_chauffage_id:
                        source_energie_chauffage = self.type_chauffage_id.source_energie_chauffage_id
                        if sujet:
                            primes = self.env['groupe_cayla.tarif_prime_cee'].search([
                                ('sujet_devis_id', '=', sujet.id),
                                ('convention_id', '=', self.convention_id.id),
                                ('zone_habitation_id', '=', self.zone_habitation_id.id),
                                ('type_client_id', '=', self.type_client_id.id),
                            ])
                            if primes:
                                if len(primes) == 1:
                                    l.montant_prime_unitaire = primes[0].prix_unitaire
                                elif len(primes) == 2:
                                    prime = primes[0] if primes[0].source_energie_chauffage_id.id == source_energie_chauffage.id else primes[1]
                                    l.montant_prime_unitaire = prime.prix_unitaire
                            else:
                                l.montant_prime_unitaire = None
                        else:
                            l.montant_prime_unitaire = None
                    else:
                        l.montant_prime_unitaire = None
                else:
                    l.montant_prime_unitaire = None


    @api.model
    def default_get(self, fields_list):
        res = models.Model.default_get(self, fields_list)
        if 'client_id' not in res:
            return res
        client = self.env['groupe_cayla.client'].search([('id', '=', res['client_id'])], limit=1)
        lignes_devis = client.devis_id.lignes_devis

        type_ligne_cee = self.env['groupe_cayla.ligne_cee']
        lignes_cee = []
        for ligne_devis in lignes_devis:
            lcee = type_ligne_cee.create({
                'ligne_devis_id': ligne_devis.id,
                'montant_prime_unitaire': 0,
                'montant_prime_total': 0
            })
            lignes_cee.append(lcee.id)
        res['lignes_cee'] = lignes_cee

        return res

