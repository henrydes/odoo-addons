from datetime import date

from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class CEE(models.Model):
    _name = 'groupe_cayla.cee'
    _description = 'Un dossier CEE'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    client_id = fields.Many2one('groupe_cayla.client',required=True,ondelete='cascade')
    devis_id = fields.Many2one('groupe_cayla.devis',required=True,ondelete='cascade')
    user_id = fields.Many2one('res.users',required=True,string='Utilisateur')

    # controle
    saisie_controle = fields.Boolean(string='Saisir le contrôle', store=False, default=False)
    controle_user_id = fields.Many2one('res.users',required=False,string='Utilisateur')
    date_reception = fields.Date()
    date_controle = fields.Date()
    fiche_vt = fields.Boolean(default=False, string='Fiche de VT')
    devis = fields.Boolean(default=False, string='Devis')
    ah = fields.Boolean(default=False, string='AH')
    fiche_chantier = fields.Boolean(default=False, string='Fiche de CH')
    dossier_valide = fields.Boolean(default=False, string='DOSS. VALIDE')

    # edition contribution
    contribution_user_id = fields.Many2one('res.users', required=False, string='Utilisateur')
    contribution_date_edition = fields.Date(default=date.today())

    # edition ah
    ah_user_id = fields.Many2one('res.users', required=False, string='Utilisateur')
    ah_date_edition = fields.Date()

    # depot

    saisie_depot = fields.Boolean(string='Saisir le dépôt', store=False, default=False)
    date_depot = fields.Date()
    date_validation = fields.Date()
    refus = fields.Boolean(default=False)
    reference_cee = fields.Char(string='Ref CEE')

    lignes_cee = fields.One2many('groupe_cayla.ligne_cee', 'cee_id', string='Lignes')

    type_client_id = fields.Many2one('groupe_cayla.type_client', required=True)
    zone_habitation_id = fields.Many2one('groupe_cayla.zone_habitation', required=True)
    type_chauffage_id = fields.Many2one('groupe_cayla.type_chauffage', required=True)
    source_energie_chauffage = fields.Char(related='type_chauffage_id.source_energie_chauffage_id.libelle', store=False)

    convention_id = fields.Many2one('groupe_cayla.convention', required=True)
    fiche_1_id = fields.Many2one('groupe_cayla.fiche', required=True, string='Fiches')
    fiche_2_id = fields.Many2one('groupe_cayla.fiche', required=False, string=' ')

    objet_devis = fields.Char(related='devis_id.objet.libelle', store=False)

    ref_fiscale = fields.Char(required=True)
    foyer = fields.Integer(required=True)
    locataire = fields.Boolean(string='Locataire ?', required=True)

    _rec_name = 'combination'
    combination = fields.Char(string='Combination', compute='_compute_fields_combination')

    somme_reversion = fields.Float(string='Prime client', compute='_compute_sommes', store=True)
    somme_primes = fields.Float(string='Montant HT', compute='_compute_sommes', store=True)



    @api.depends('convention_id', 'type_client_id', 'devis_id')
    def _compute_fields_combination(self):
        for d in self:
            d.combination = d.convention_id.libelle + ' * ' + d.type_client_id.libelle+' devis n°'+d.devis_id.numero+' ('+str(d.devis_id.montant_ht)+'€ HT)'



    @api.depends('lignes_cee', 'lignes_cee.montant_reversion', 'lignes_cee.montant_prime_total')
    def _compute_sommes(self):
        for d in self:
            if d.lignes_cee:
                d.somme_primes = 0
                d.somme_reversion = 0
                for l in d.lignes_cee:
                    d.somme_primes += l.montant_prime_total
                    d.somme_reversion += l.montant_reversion

    @api.onchange('convention_id', 'type_client_id', 'zone_habitation_id', 'type_chauffage_id')
    def update_lignes(self):
        for d in self:
            if d.lignes_cee:
                for l in d.lignes_cee:
                    l._compute_ligne()

    @api.onchange('devis_id')
    def onchange_devis(self):
        for r in self:
            devis = r.devis_id
            if devis:
                lignes_devis = devis.lignes_devis

                type_ligne_cee = self.env['groupe_cayla.ligne_cee']
                lignes_cee = []
                for ligne_devis in lignes_devis:
                    lcee = type_ligne_cee.create({
                        'ligne_devis_id': ligne_devis.id,
                        'montant_prime_unitaire': 0,
                        'montant_prime_total': 0
                    })
                    lignes_cee.append(lcee.id)
                r.lignes_cee = lignes_cee



    @api.onchange('refus')
    def onchange_refus(self):
        for record in self:
            if record.refus:
                record.date_validation = None

    @api.onchange('date_validation')
    def onchange_date_validation(self):
        for record in self:
            if record.date_validation:
                record.refus = False

    @api.model
    def create(self, values):
        rec = super(CEE, self).create(values)
        devis = self.env['groupe_cayla.devis'].search([('id', '=', values['devis_id'])], limit=1)
        devis.cee_ic = rec
        type_client = self.env['groupe_cayla.type_client'].search([('id', '=', values['type_client_id'])], limit=1)
        self.modification_tarifs_lignes_devis(devis, type_client)
        return rec

    @api.multi
    def write(self, vals):
        client = self.client_id

        super().write(vals)
        self.modification_tarifs_lignes_devis(self.devis_id, self.type_client_id)
        return True

    def modification_tarifs_lignes_devis(self, devis_id, type_client_id):

        if devis_id and devis_id.lignes_devis:
            montant_ht = 0
            for record in devis_id.lignes_devis:
                record.prix_unitaire = 0
                record.prix_total = 0
                if record.sujet_devis_id:
                    if record.sujet_devis_id.tarif_tout_compris:
                        if record.devis_id.type_professionnel:
                            record.prix_unitaire = record.sujet_devis_id.tarif_pro
                        elif type_client_id.donne_droit_tarif_solidarite_energetique == True and record.prime_cee == True:
                            record.prix_unitaire = record.sujet_devis_id.tarif_solidarite_energetique
                        else:
                            record.prix_unitaire = record.sujet_devis_id.tarif_particulier
                    else:
                        if record.devis_id.type_professionnel:
                            record.prix_unitaire = record.ligne_sujet_devis_id.tarif_pro
                        elif type_client_id.donne_droit_tarif_solidarite_energetique == True and record.prime_cee == True:
                            record.prix_unitaire = record.ligne_sujet_devis_id.tarif_solidarite_energetique
                        else:
                            record.prix_unitaire = record.ligne_sujet_devis_id.tarif_particulier
                record.prix_total = record.prix_unitaire * record.quantite
            if devis_id.lignes_supplement_devis:
                for ligne_supplement in devis_id.lignes_supplement_devis:
                    montant_ht += ligne_supplement.tarif
            for ligne in devis_id.lignes_devis:
                montant_ht += ligne.prix_total
            # client.devis_id.montant_ht = montant_ht
            if False or devis_id.remise:
                devis_id.montant_remise = devis_id.montant_ht * devis_id.remise / 100
                devis_id.montant_ht = devis_id.montant_ht - devis_id.montant_remise
            # client.devis_id.montant_tva = client.devis_id.montant_ht * client.devis_id.choix_tva.taux / 100
            # client.devis_id.montant_ttc = client.devis_id.montant_ht + client.devis_id.montant_tva
            # client.montant_ttc_devis = client.devis_id.montant_ttc
