from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class LigneCEE(models.Model):
    _name = 'groupe_cayla.ligne_cee'
    _description = 'Une ligne cee'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    cee_id = fields.Many2one('groupe_cayla.cee', ondelete='cascade')

    ligne_devis_id = fields.Many2one('groupe_cayla.ligne_devis', ondelete='cascade')

    sujet_ligne_devis = fields.Char(compute='_compute_ligne', store=False)
    quantite_ligne_devis = fields.Integer(compute='_compute_ligne', store=False)

    montant_prime_unitaire = fields.Float(required=True, compute='_compute_ligne', store=True)
    montant_prime_total = fields.Float( compute='_compute_ligne', store=True)
    montant_reversion=fields.Float( compute='_compute_ligne', store=True)

    _rec_name = 'combination'
    combination = fields.Char(string='Combination', compute='_compute_fields_combination')

    @api.depends('sujet_ligne_devis')
    def _compute_fields_combination(self):
        for d in self:
            d.combination = d.sujet_ligne_devis

    @api.depends('ligne_devis_id', 'ligne_devis_id.quantite', 'ligne_devis_id.sujet_devis_id','ligne_devis_id.prime_cee',
                 'cee_id', 'cee_id.convention_id', 'cee_id.zone_habitation_id', 'cee_id.type_client_id', 'cee_id.type_chauffage_id')
    def _compute_ligne(self):
        for l in self:
            if l.ligne_devis_id:
                l.sujet_ligne_devis = l.ligne_devis_id.sujet_devis_id.libelle
                l.quantite_ligne_devis = l.ligne_devis_id.quantite
            else:
                l.sujet_ligne_devis = None
                l.quantite_ligne_devis = None

            l.montant_prime_unitaire = 0
            l.montant_reversion = 0
            if l.ligne_devis_id and l.ligne_devis_id.prime_cee:
                sujet = l.ligne_devis_id.sujet_devis_id
                if l.cee_id.type_chauffage_id:
                    source_energie_chauffage = l.cee_id.type_chauffage_id.source_energie_chauffage_id
                    if sujet:
                        primes = self.env['groupe_cayla.tarif_prime_cee'].search([
                            ('sujet_devis_id', '=', sujet.id),
                            ('convention_id', '=', l.cee_id.convention_id.id),
                            ('zone_habitation_id', '=', l.cee_id.zone_habitation_id.id),
                            ('type_client_id', '=', l.cee_id.type_client_id.id),
                        ])
                        if primes:
                            if len(primes) == 1:
                                l.montant_prime_unitaire = primes[0].prix_unitaire
                            elif len(primes) == 2:
                                prime = primes[0] if primes[
                                                         0].source_energie_chauffage_id.id == source_energie_chauffage.id else \
                                    primes[1]
                                l.montant_prime_unitaire = prime.prix_unitaire

            if l.montant_prime_unitaire:
                l.montant_prime_total = l.montant_prime_unitaire * l.ligne_devis_id.quantite
            else:
                l.montant_prime_total = None
            _logger.info(l)
            _logger.info(l.ligne_devis_id)
            _logger.info(l.cee_id.type_client_id)
            _logger.info(l.cee_id.type_client_id.taux_reversion)
            if l.cee_id.type_client_id.mode_calcul_reversion == 'multiplication':
                l.montant_reversion = l.ligne_devis_id.prix_total * l.cee_id.type_client_id.taux_reversion - 1
            else:
                l.montant_reversion = l.montant_prime_total / l.cee_id.type_client_id.taux_reversion



