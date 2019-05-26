from datetime import date

from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class Devis(models.Model):
    _name = 'groupe_cayla.devis'
    _description = 'Un devis'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    etat = fields.Selection([
        ('nouveau', "Facture non éditée : devis modifiable"),
        ('valide', 'Facture client éditée. Devis non modifiable')
    ], default='nouveau'
    )
    _sql_constraints = [
        ('client_id', 'unique (client_id)', 'Ce client a déjà un devis')
    ]
    client_id = fields.Many2one('groupe_cayla.client', required=True, ondelete='cascade')
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
    acompte = fields.Float(default=0)

    # champs en lecture seuls
    montant_ht = fields.Float(compute='_compute_montant_ht_montant_remise', store=True)
    montant_tva = fields.Float(compute='_compute_montant_tva_montant_ttc', store=True)
    montant_ttc = fields.Float(compute='_compute_montant_tva_montant_ttc', store=True)
    montant_remise = fields.Float(compute='_compute_montant_ht_montant_remise', store=True)
    montant_eco_cheque = fields.Float(compute='_compute_montant_eco_cheque', store=True)
    superficie = fields.Integer(compute='_compute_superficie', store=True)
    mention_legale = fields.Char(compute='_compute_mention_legale', store=True)
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

    @api.depends('date_edition', 'client_id', 'client_id.cee_id', 'client_id.cee_id.convention_id',
                 'client_id.cee_id.convention_id.mention_legale_convention_ids',
                 'client_id.cee_id.convention_id.mention_legale_convention_ids.mention',
                 'client_id.cee_id.convention_id.mention_legale_convention_ids.date_debut',
                 'client_id.cee_id.convention_id.mention_legale_convention_ids.date_fin')
    def _compute_mention_legale(self):
        for d in self:
            mention = '**********'
            if d.date_edition and d.client_id and d.client_id.cee_id and d.client_id.cee_id.convention_id and d.client_id.cee_id.convention_id.mention_legale_convention_ids:
                mentions = d.client_id.cee_id.convention_id.mention_legale_convention_ids
                mentions_valables = [m for m in mentions if
                                     m.date_debut <= d.date_edition and (
                                                 not m.date_fin or m.date_fin >= d.date_edition)]
                _logger.info(mentions_valables)
                if mentions_valables and len(mentions_valables) == 1:
                    mention = mentions_valables[0].mention
                # empecher en amont la création de plusieurs mentions légales valables à la même date
            d.mention_legale = mention

    @api.depends('numero', 'montant_ht', 'objet', 'lignes_devis', 'lignes_devis.prix_total')
    def _compute_fields_combination(self):
        for d in self:
            d.combination = 'Devis numéro ' + d.numero + ' ' + str(d.montant_ht) + '€ HT (' + d.objet.libelle + ')'

    @api.depends('type_eco_cheque')
    def _compute_montant_eco_cheque(self):
        for d in self:
            d.montant_eco_cheque = 1500 if d.type_eco_cheque else 0

    @api.depends('lignes_devis')
    def _compute_superficie(self):
        for d in self:
            for ligne in d.lignes_devis:
                d.superficie += ligne.quantite

    @api.depends('lignes_supplement_devis', 'lignes_devis', 'remise', 'lignes_devis.prix_unitaire',
                 'lignes_devis.prix_total')
    def _compute_montant_ht_montant_remise(self):
        for d in self:
            d.montant_ht = 0
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
        rec = super(Devis, self).create(values)

        client = self.env['groupe_cayla.client'].search([('id', '=', values['client_id'])], limit=1)

        client.devis_id = rec
        return rec

    @api.multi
    def write(self, vals):
        super().write(vals)

        return True

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
    def invalider_devis(self):
        self.date_envoi = None
        self.etat = 'nouveau'
