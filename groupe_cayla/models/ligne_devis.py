from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class LigneDevis(models.Model):
    _name = 'groupe_cayla.ligne_devis'
    _description = 'Une ligne devis'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    devis_id = fields.Many2one('groupe_cayla.devis', ondelete='cascade')

    sujet_devis_id = fields.Many2one('groupe_cayla.sujet_devis', required=True, string='Sujet')
    ligne_sujet_devis_id = fields.Many2one('groupe_cayla.ligne_sujet_devis', required=True, string='Produit')
    produit_id = fields.Many2one('groupe_cayla.produit', required=False, string='Produit 2')
    marque_produit_id = fields.Many2one('groupe_cayla.marque_produit', required=True, string='Marque')
    modele_produit_id = fields.Many2one('groupe_cayla.modele_produit', required=True, string='Modèle')

    acermi = fields.Char(compute='_compute_acermi', store=False)
    epaisseur = fields.Integer(compute='_compute_epaisseur', string='Epaisseur (mm)', store=False)
    resistance_thermique = fields.Char(compute='_compute_resistance_thermique', string='Res.Ther.', store=False)
    detail = fields.Char()

    prix_unitaire = fields.Float(required=True)
    quantite = fields.Integer(required=True)
    prix_total = fields.Float(required=True)
    prime_cee = fields.Boolean(default=False)

    @api.depends('modele_produit_id')
    def _compute_acermi(self):
        for d in self:
            if d.modele_produit_id:
                d.acermi = d.modele_produit_id.acermi
                d.epaisseur = d.modele_produit_id.epaisseur
                d.resistance_thermique = d.modele_produit_id.resistance_thermique
            else:
                d.acermi = None
                d.epaisseur = None
                d.resistance_thermique = None

    @api.onchange('quantite', 'prix_unitaire')
    def on_change_quantite(self):
        for record in self:
            record.prix_total = record.quantite * record.prix_unitaire

    @api.onchange('sujet_devis_id')
    def on_change_sujet_devis_id(self):
        for record in self:
            if record.sujet_devis_id:
                record.detail = record.sujet_devis_id.detail
                record.ligne_sujet_devis_id = None
                record.marque_produit_id = None
                record.modele_produit_id = None
                if record.sujet_devis_id.tarif_tout_compris:
                    # si tarif tout compris, le tarif est porté par le SUJET, sinon par le PRODUIT
                    # TODO tarif eco : si service energie client type P.GP (particulier grand précaire) et devis Prime CEE
                    # à implémenter après avoir fait le service energie
                    if record.devis_id.type_professionnel:
                        record.prix_unitaire = record.sujet_devis_id.tarif_pro
                    else:
                        record.prix_unitaire = record.sujet_devis_id.tarif_particulier
                else:
                    record.prix_unitaire = None

    @api.onchange('ligne_sujet_devis_id')
    def on_change_ligne_sujet_devis_id(self):
        for record in self:
            if record.ligne_sujet_devis_id:
                record.produit_id = record.ligne_sujet_devis_id.produit_id
                record.marque_produit_id = None
                record.modele_produit_id = None
                marques = self.env['groupe_cayla.marque_produit'].search(
                    [('produits_id', 'in', record.ligne_sujet_devis_id.produit_id.id)])
                if marques and len(marques) == 1:
                    record.marque_produit_id = marques[0]
                if not record.sujet_devis_id.tarif_tout_compris:
                    _logger.info('tarif au detail')
                    # si tarif tout compris, le tarif est porté par le SUJET, sinon par le PRODUIT
                    # TODO tarif eco : si service energie client type P.GP (particulier grand précaire) et devis Prime CEE
                    # à implémenter après avoir fait le service energie
                    if record.devis_id.type_professionnel:
                        record.prix_unitaire = record.ligne_sujet_devis_id.tarif_pro
                    else:
                        record.prix_unitaire = record.ligne_sujet_devis_id.tarif_particulier

    @api.onchange('marque_produit_id')
    def on_change_marque_produit_id(self):
        for record in self:
            if record.marque_produit_id:
                record.modele_produit_id = None
                modeles = self.env['groupe_cayla.modele_produit'].search(
                    [
                        ('sujets_devis_id', 'in', record.sujet_devis_id.id),
                        ('produits_id', 'in', record.produit_id.id),
                        ('marque_produit_id', '=', record.marque_produit_id.id)
                    ]
                )
                if modeles and len(modeles) == 1:
                    record.modele_produit_id = modeles[0]

    @api.model
    def create(self, values):
        values['prix_total'] = values['quantite'] * values['prix_unitaire']
        rec = super(LigneDevis, self).create(values)
        return rec

    @api.multi
    def write(self, values):
        quantite = values['quantite'] if 'quantite' in values else self.quantite
        prix_unitaire = values['prix_unitaire'] if 'prix_unitaire' in values else self.prix_unitaire
        values['prix_total'] = quantite * prix_unitaire
        super().write(values)
        return True
