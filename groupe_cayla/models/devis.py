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
    etat = fields.Selection([
        ('nouveau', "En cours d'édition, non envoyé. Devis modifiable."),
        ('valide', 'Devis envoyé. Non modifiable')
    ], default='nouveau'
    )

    client_id = fields.Many2one(
        'groupe_cayla.client',
        delegate=False,
        required=True,
        ondelete='cascade'
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

    # champs en lecture seuls
    montant_ht = fields.Float(compute='_compute_montant_ht_montant_remise', store=True)
    montant_tva = fields.Float(compute='_compute_montant_tva_montant_ttc', store=True)
    montant_ttc = fields.Float(compute='_compute_montant_tva_montant_ttc', store=True)
    montant_remise = fields.Float(compute='_compute_montant_ht_montant_remise', store=True)
    montant_eco_cheque = fields.Float(compute='_compute_montant_eco_cheque', store=True)
    superficie = fields.Integer(compute='_compute_superficie', store=True)
    # fin champs en lecture seuls

    entite_edition_id = fields.Many2one(
        'groupe_cayla.entite_edition_devis', required=True
    )

    motif_refus = fields.Text()

    type_octeha = fields.Boolean(string="Oc'teha", default=False)
    type_anah = fields.Boolean(string='ANAH', default=False)
    type_eco_cheque = fields.Boolean(string='Eco-chéque', default=False)
    type_cee = fields.Boolean(string='CEE', default=False)
    type_professionnel = fields.Boolean(string='Professionnel', default=False)
    remise = fields.Float(string='Remise (%)')

    objet = fields.Many2one('groupe_cayla.objet_devis', required=True)
    objet_autres = fields.Char()
    choix_tva = fields.Many2one('groupe_cayla.taux_tva', string='Choix TVA', required=True)

    lignes_supplement_devis = fields.One2many('groupe_cayla.ligne_supplement_devis', 'devis_id', string='Supplement')
    lignes_devis = fields.One2many('groupe_cayla.ligne_devis', 'devis_id', string='Lignes')

    _rec_name = 'combination'
    combination = fields.Char(string='Combination', compute='_compute_fields_combination')


    @api.depends('numero')
    def _compute_fields_combination(self):
        for d in self:
            d.combination = 'Devis numéro ' + d.numero



    @api.depends('type_eco_cheque')
    def _compute_montant_eco_cheque(self):
        for d in self:
            d.montant_eco_cheque = 1500 if d.type_eco_cheque else 0

    @api.depends('lignes_supplement_devis', 'lignes_devis')
    def _compute_superficie(self):
        for d in self:
            for ligne_supplement in d.lignes_supplement_devis:
                d.superficie += ligne_supplement.quantite
            for ligne in d.lignes_devis:
                d.superficie += ligne.quantite

    @api.depends('lignes_supplement_devis', 'lignes_devis', 'remise')
    def _compute_montant_ht_montant_remise(self):
        for d in self:
            for ligne_supplement in d.lignes_supplement_devis:
                d.montant_ht += ligne_supplement.tarif
            for ligne in d.lignes_devis:
                d.montant_ht += ligne.prix_total
            if d.remise:
                d.montant_remise = d.montant_ht * d.remise / 100
                d.montant_ht = d.montant_ht - d.montant_remise

    @api.depends('montant_ht', 'choix_tva')
    def _compute_montant_tva_montant_ttc(self):
        for d in self:
            d.montant_tva = d.montant_ht * d.choix_tva.taux / 100
            d.montant_ttc = d.montant_ht + d.montant_tva

    @api.model
    def create(self, values):
        if 'date_envoi' in values and values['date_envoi']:
            values['etat'] = 'valide'
        rec = super(Devis, self).create(values)

        client = self.env['groupe_cayla.client'].search([('id', '=', values['client_id'])], limit=1)
        client.etat = 'attente_commande'
        client.devis_id = rec
        return rec

    @api.multi
    def write(self, vals):
        client = self.client_id
        if 'date_envoi' in vals and vals['date_envoi']:
            vals['etat'] = 'valide'
        super().write(vals)
        devis = self.env['groupe_cayla.devis'].search([('id', '=', self.id)], limit=1)
        if devis.date_acceptation:
            client.etat = 'chantier_a_planifier'
        elif devis.date_refus:
            client.etat = 'annule_par_client'
        return True

    @api.onchange('type_professionnel')
    def onchange_type_professionnel(self):
        # si tarif tout compris, le tarif est porté par le SUJET, sinon par le PRODUIT
        # tarif eco : si service energie client type P.GP (particulier grand précaire) et ligne devis Prime CEE
        # à implémenter après avoir fait le service energie
        for ligne in self.lignes_devis:
            if ligne.sujet_devis_id.tarif_tout_compris:
                if self.type_professionnel:
                    ligne.prix_unitaire = ligne.sujet_devis_id.tarif_pro
                elif self.client_id.cee_id and self.client_id.cee_id.type_client_id.donne_droit_tarif_solidarite_energetique == True and ligne.prime_cee == True:
                    ligne.prix_unitaire = ligne.sujet_devis_id.tarif_solidarite_energetique
                else:
                    ligne.prix_unitaire = ligne.sujet_devis_id.tarif_particulier
            else:
                if self.type_professionnel:
                    ligne.prix_unitaire = ligne.ligne_sujet_devis_id.tarif_pro
                elif self.client_id.cee_id and self.client_id.cee_id.type_client_id.donne_droit_tarif_solidarite_energetique == True and ligne.prime_cee == True:
                    ligne.prix_unitaire = ligne.ligne_sujet_devis_id.tarif_solidarite_energetique
                else:
                    ligne.prix_unitaire = ligne.ligne_sujet_devis_id.tarif_particulier
            ligne.prix_total = ligne.prix_unitaire * ligne.quantite

    @api.onchange('date_refus')
    def onchange_date_refus(self):
        if self.date_refus:
            self.date_acceptation = None

    @api.onchange('date_acceptation')
    def onchange_date_acceptation(self):
        if self.date_acceptation:
            self.date_refus = None
            self.motif_refus = None

    @api.one
    def set_date_envoi_to_none(self):
        self.date_envoi = None
        self.etat = 'nouveau'


