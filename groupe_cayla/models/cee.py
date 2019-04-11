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

    _rec_name = 'combination'
    combination = fields.Char(string='Combination', compute='_compute_fields_combination')

    @api.depends('convention_id', 'type_client_id')
    def _compute_fields_combination(self):
        for d in self:
            d.combination = d.convention_id.libelle + ' * ' + d.type_client_id.libelle

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
                                    prime = primes[0] if primes[
                                                             0].source_energie_chauffage_id.id == source_energie_chauffage.id else \
                                        primes[1]
                                    l.montant_prime_unitaire = prime.prix_unitaire
                            else:
                                l.montant_prime_unitaire = None
                        else:
                            l.montant_prime_unitaire = None
                    else:
                        l.montant_prime_unitaire = None
                else:
                    l.montant_prime_unitaire = None
                if l.montant_prime_unitaire:
                    l.montant_prime_total = l.montant_prime_unitaire * l.ligne_devis_id.quantite
                else:
                    l.montant_prime_total = None

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

    @api.model
    def create(self, values):
        rec = super(CEE, self).create(values)
        client = self.env['groupe_cayla.client'].search([('id', '=', values['client_id'])], limit=1)
        self.modification_tarifs_lignes_devis(client)
        return rec

    @api.multi
    def write(self, vals):
        client = self.client_id
        super().write(vals)
        self.modification_tarifs_lignes_devis(client)
        return True

    def modification_tarifs_lignes_devis(self, client):
        if client.devis_id and client.devis_id.etat != 'valide' and client.devis_id.lignes_devis:
            montant_ht = 0
            for record in client.devis_id.lignes_devis:
                record.prix_unitaire = 0
                record.prix_total = 0
                if record.sujet_devis_id:
                    if record.sujet_devis_id.tarif_tout_compris:
                        if record.devis_id.type_professionnel:
                            record.prix_unitaire = record.sujet_devis_id.tarif_pro
                        elif record.devis_id.client_id.cee_id and record.devis_id.client_id.cee_id.type_client_id.donne_droit_tarif_solidarite_energetique == True and record.prime_cee == True:
                            record.prix_unitaire = record.sujet_devis_id.tarif_solidarite_energetique
                        else:
                            record.prix_unitaire = record.sujet_devis_id.tarif_particulier
                    else:
                        if record.devis_id.type_professionnel:
                            record.prix_unitaire = record.ligne_sujet_devis_id.tarif_pro
                        elif record.devis_id.client_id.cee_id and record.devis_id.client_id.cee_id.type_client_id.donne_droit_tarif_solidarite_energetique == True and record.prime_cee == True:
                            record.prix_unitaire = record.ligne_sujet_devis_id.tarif_solidarite_energetique
                        else:
                            record.prix_unitaire = record.ligne_sujet_devis_id.tarif_particulier
                record.prix_total = record.prix_unitaire * record.quantite
            if client.devis_id.lignes_supplement_devis:
                for ligne_supplement in client.devis_id.lignes_supplement_devis:
                    montant_ht += ligne_supplement.tarif
            for ligne in client.devis_id.lignes_devis:
                montant_ht += ligne.prix_total
            client.devis_id.montant_ht = montant_ht
            if client.devis_id.remise:
                client.devis_id.montant_remise = client.devis_id.montant_ht * client.devis_id.remise / 100
                client.devis_id.montant_ht = client.devis_id.montant_ht - client.devis_id.montant_remise
            client.devis_id.montant_tva = client.devis_id.montant_ht * client.devis_id.choix_tva.taux / 100
            client.devis_id.montant_ttc = client.devis_id.montant_ht + client.devis_id.montant_tva
            client.montant_ttc_devis = client.devis_id.montant_ttc

