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

    # pas de couplage entre la ligne et les many2one
    modele_libelle = fields.Char(string='Libellé')
    marque_libelle = fields.Char(string='Marque')
    produit_libelle = fields.Char(string='Produit')
    sujet_libelle = fields.Char(string='Sujet')
    acermi = fields.Char()
    epaisseur = fields.Integer(string='Epaisseur (mm)')
    resistance_thermique = fields.Char(string='Res.Ther.')
    detail = fields.Char()

    prix_unitaire = fields.Float(required=True, compute='_compute_prix_unitaire', store=True)
    quantite = fields.Integer(required=True)
    prix_total = fields.Float(required=True, compute='_compute_prix_total', store=True)
    prime_cee = fields.Boolean(default=False)

    @api.onchange('modele_produit_id')
    def onchange_modele(self):
        if self.modele_produit_id:
            self.acermi = self.modele_produit_id.acermi
            self.epaisseur = self.modele_produit_id.epaisseur
            self.resistance_thermique = self.modele_produit_id.resistance_thermique
            self.modele_libelle = self.modele_produit_id.libelle
            self.marque_libelle = self.marque_produit_id.libelle
            self.produit_libelle = self.produit_id.libelle
            self.sujet_libelle = self.sujet_devis_id.libelle
        else:
            self.acermi = None
            self.epaisseur = None
            self.resistance_thermique = None
            self.modele_libelle = None
            self.marque_libelle = None
            self.produit_libelle = None
            self.sujet_libelle = None

    @api.depends('quantite', 'prix_unitaire')
    def _compute_prix_total(self):
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

    @api.depends('devis_id', 'sujet_devis_id', 'ligne_sujet_devis_id', 'prime_cee',
                 'devis_id.type_professionnel','devis_id.client_id.cee_id', 'devis_id.client_id.cee_id.type_client_id.donne_droit_tarif_solidarite_energetique')
    def _compute_prix_unitaire(self):
        for r in self:
            r.prix_unitaire = self.get_prix_unitaire(r.devis_id, r.sujet_devis_id, r.ligne_sujet_devis_id, r.prime_cee)


    def get_prix_unitaire(self, devis_id, sujet_devis_id, ligne_sujet_devis_id, prime_cee):
        prix_unitaire = None
        if sujet_devis_id:
            if sujet_devis_id.tarif_tout_compris:
                if devis_id.type_professionnel:
                    prix_unitaire = sujet_devis_id.tarif_pro
                elif devis_id.client_id.cee_id and devis_id.client_id.cee_id.type_client_id.donne_droit_tarif_solidarite_energetique == True and prime_cee == True:
                    prix_unitaire = sujet_devis_id.tarif_solidarite_energetique
                else:
                    prix_unitaire = sujet_devis_id.tarif_particulier
            else:
                if devis_id.type_professionnel:
                    prix_unitaire = ligne_sujet_devis_id.tarif_pro
                elif devis_id.client_id.cee_id and devis_id.client_id.cee_id.type_client_id.donne_droit_tarif_solidarite_energetique == True and prime_cee == True:
                    prix_unitaire = ligne_sujet_devis_id.tarif_solidarite_energetique
                else:
                    prix_unitaire = ligne_sujet_devis_id.tarif_particulier
        return prix_unitaire

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

