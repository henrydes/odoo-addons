import logging
from datetime import date

from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class Client(models.Model):
    _name = 'groupe_cayla.client'
    _description = 'Un prospect ou un client'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _inherits = {'res.partner': 'res_partner_id'}
    res_partner_id = fields.Many2one(comodel_name="res.partner", ondelete="restrict", required=True)

    etat = fields.Selection([
        ('nouveau', 'Nouveau prospect à contacter'),
        ('annule_telephone', 'Annulé par téléphone'),
        ('annule_client', 'Annulé par le client'),
        ('vt_a_planifier', 'VT à planifier'),
        ('vt_planifiee', 'VT planifiée'),
        ('vt_a_saisir', 'VT à mettre à jour'),
        ('annule_par_vt', 'Annulé par VT'),
        ('vt_incomplete', 'VT incomplète'),
        ('devis_a_editer', 'Devis à éditer'),
        ('attente_commande', 'Devis en attente de commande'),
        ('chantier_a_planifier', 'Chantier à planifier'),
        ('chantier_planifie', 'Chantier planifié'),
        ('annule_par_client', 'Annulé par client'),
        ('chantier_a_saisir', 'Chantier à saisir'),
        ('annule_par_applicateur', 'Annulé par applicateur'),
        ('facture_client_a_editer', 'Facture client à éditer'),
        ('dossier_incomplet', 'Dossier contrôlé incomplet'),
        ('dossier_a_deposer', 'Dossier à déposer'),
        ('dossier_depose', 'Dossier déposé PNCE'),
        ('dossier_valide', 'Clôturé / Facture délégataire à éditer'),
        ('dossier_refuse', 'Dossier déposé PNCE / Refusé')
    ], default='nouveau', compute='_compute_etat_client', store=True
    )

    prospect_qualifie = fields.Selection([
        ('oui', 'OUI'),
        ('non', 'NON')
    ], default=None, string='Prospect qualifié')

    @api.depends('devis_id', 'chantier_id', 'vt_id', 'planif_chantier_id', 'planif_vt_id', 'cee_id',
                 'prospect_qualifie', 'planif_vt_id.date_time_planif', 'planif_chantier_id.date_time_planif',
                 'vt_id.documents_complets', 'vt_id.dossier_complet', 'vt_id.vt_validee', 'vt_id.date_de_realisation',
                 'devis_id.date_envoi', 'devis_id.date_refus', 'devis_id.date_acceptation',
                 'chantier_id.chantier_realise',
                 'cee_id.refus', 'cee_id.date_validation', 'cee_id.date_depot', 'cee_id.dossier_valide',
                 'cee_id.date_controle')
    def _compute_etat_client(self):
        for c in self:
            cee = c.cee_id
            if cee:
                if cee.refus:
                    c.etat = 'dossier_refuse'
                    return
                if cee.date_validation:
                    c.etat = 'dossier_valide'
                    return
                if cee.date_depot:
                    c.etat = 'dossier_depose'
                    return
                if cee.dossier_valide:
                    c.etat = 'dossier_a_deposer'
                    return
                if not cee.dossier_valide and cee.date_controle:
                    c.etat = 'dossier_incomplet'
                    return
            chantier = c.chantier_id
            if chantier:
                if chantier.chantier_realise:
                    c.etat = 'facture_client_a_editer'
                    return
                else:
                    c.etat = 'annule_par_applicateur'
                    return
            planif_chantier = c.planif_chantier_id
            if planif_chantier:
                if planif_chantier.date_time_planif:
                    if planif_chantier.date_time_planif.date() > date.today():
                        c.etat = 'chantier_planifie'
                        return
                    else:
                        c.etat = 'chantier_a_saisir'
                        return
            devis = c.devis_id
            if devis:
                if devis.date_refus:
                    c.etat = 'annule_par_client'
                    return
                if devis.date_acceptation:
                    c.etat = 'chantier_a_planifier'
                    return
                if devis.date_envoi:
                    c.etat = 'attente_commande'
                    return
            vt = c.vt_id
            if vt and vt.date_de_realisation:
                if vt.documents_complets and vt.vt_validee and vt.dossier_complet:
                    c.etat = 'devis_a_editer'
                    return
                if not vt.documents_complets:
                    c.etat = 'vt_incomplete'
                    return
                if not vt.vt_validee:
                    c.etat = 'annule_par_vt'
                    return
            planif_vt = c.planif_vt_id
            if planif_vt:
                if planif_vt.date_time_planif:
                    if planif_vt.date_time_planif.date() > date.today():
                        c.etat = 'vt_planifiee'
                        return
                    else:
                        c.etat = 'vt_a_saisir'
                        return

            if c.prospect_qualifie is not None:
                if c.prospect_qualifie == 'oui':
                    c.etat = 'vt_a_planifier'
                    return
                if c.prospect_qualifie == 'non':
                    c.etat = 'annule_telephone'
                    return
            c.etat = 'nouveau'
            _logger.info('NOUVEAU CLIENT')

    solde_client = fields.Float(compute='_compute_solde_client', store=True)

    @api.depends('cee_id', 'devis_id', 'cee_id.somme_reversion', 'devis_id.montant_ttc', 'devis_id.acompte')
    def _compute_solde_client(self):
        for record in self:
            montant_ttc_devis = 0
            somme_reversions_cee = 0
            acompte = 0
            if record.devis_id:
                montant_ttc_devis = record.devis_id.montant_ttc
                if record.devis_id.acompte:
                    acompte = record.devis_id.acompte
            if record.cee_id:
                somme_reversions_cee = record.cee_id.somme_reversion

            record.solde_client = montant_ttc_devis - somme_reversions_cee - acompte
            _logger.info(record.solde_client)

    # 1 Source apporteur
    date_entree = fields.Date()
    utilisateur_id = fields.Many2one('res.users')
    source_client = fields.Char()

    # 2 Maitrise d'oeuvre
    maitre_oeuvre = fields.Char()
    installateur = fields.Char()
    contrat = fields.Char()

    # 3 Planif VT
    planif_vt_id = fields.Many2one(
        'groupe_cayla.planif_vt',
        required=False,
        ondelete='set null'
    )
    date_appel_planif_vt = fields.Date(compute='_compute_planif_vt',
                                       string="Date appel", store=False)
    date_time_planif_planif_vt = fields.Datetime(compute='_compute_planif_vt',
                                                 string="VT planifiée", store=False)
    utilisateur_planif_vt = fields.Many2one('res.users', compute='_compute_planif_vt',
                                            string="Utilisateur", store=False)
    technicien_planif_vt = fields.Many2one('res.users', compute='_compute_planif_vt',
                                           string="Technicien", store=False)

    @api.depends('planif_vt_id')
    def _compute_planif_vt(self):
        for record in self:
            if record.planif_vt_id is None:
                record.date_appel_planif_vt = None
                record.date_time_planif_planif_vt = None
                record.utilisateur_planif_vt = None
                record.technicien_planif_vt = None
            else:
                record.date_appel_planif_vt = record.planif_vt_id.date_appel
                record.date_time_planif_planif_vt = record.planif_vt_id.date_time_planif
                record.utilisateur_planif_vt = record.planif_vt_id.utilisateur_id
                record.technicien_planif_vt = record.planif_vt_id.technicien_id

    # 4 Saisie VT
    vt_id = fields.Many2one(
        'groupe_cayla.vt',
        delegate=False,
        required=False,
        ondelete='set null'
    )
    date_de_realisation_vt = fields.Date(compute='_compute_vt',
                                         string="Date de réalisation", store=False)
    vt_validee_vt = fields.Boolean(compute='_compute_vt',
                                   string="VT validée", store=False)
    documents_complets_vt = fields.Boolean(compute='_compute_vt',
                                           string="Documents complets", store=False)

    utilisateur_vt = fields.Many2one('res.users', compute='_compute_vt',
                                     string="Utilisateur", store=False)
    technicien_vt = fields.Many2one('res.users', compute='_compute_vt',
                                    string="Technicien", store=False)

    @api.depends('vt_id')
    def _compute_vt(self):
        for record in self:
            if record.vt_id is None:
                record.utilisateur_vt = None
                record.vt_validee_vt = None
                record.documents_complets_vt = None
                record.technicien_vt = None
                record.date_de_realisation_vt = None
            else:
                record.utilisateur_vt = record.vt_id.utilisateur_id
                record.vt_validee_vt = record.vt_id.vt_validee
                record.documents_complets_vt = record.vt_id.documents_complets
                record.technicien_vt = record.vt_id.technicien_id
                record.date_de_realisation_vt = record.vt_id.date_de_realisation

    # 5.1 Edition devis
    devis_id = fields.Many2one(
        'groupe_cayla.devis',
        delegate=False,
        required=False,
        ondelete='set null'
    )
    date_edition_devis = fields.Date(compute='_compute_devis',
                                     string="Edition", store=False)
    date_envoi_devis = fields.Date(compute='_compute_devis',
                                   string="Envoyé le", store=False)
    date_acceptation_devis = fields.Date(compute='_compute_devis',
                                         string="Accepté le", store=False)
    date_refus_devis = fields.Date(compute='_compute_devis',
                                   string="Refusé le", store=False)
    utilisateur_devis = fields.Many2one('res.users', compute='_compute_devis',
                                        string="Utilisateur", store=False)
    numero_devis = fields.Char(compute='_compute_devis',
                               string="N° Devis", store=False)
    montant_ttc_devis = fields.Float(compute='_compute_devis',
                                     string="Montant TTC", store=False)
    etat_devis = fields.Char(compute='_compute_devis',
                             string="Etat devis", store=False)

    @api.depends('devis_id', 'cee_id')
    def _compute_devis(self):
        for record in self:
            if record.devis_id is None:
                record.etat_devis = None
                record.numero_devis = None
                record.montant_ttc_devis = None
                record.date_edition_devis = None
                record.date_envoi_devis = None
                record.date_acceptation_devis = None
                record.date_refus_devis = None
                record.utilisateur_devis = None

            else:
                record.numero_devis = record.devis_id.numero
                record.montant_ttc_devis = record.devis_id.montant_ttc
                record.date_edition_devis = record.devis_id.date_edition
                record.date_envoi_devis = record.devis_id.date_envoi
                record.date_acceptation_devis = record.devis_id.date_acceptation
                record.date_refus_devis = record.devis_id.date_refus
                record.utilisateur_devis = record.devis_id.user_id
                record.etat_devis = record.devis_id.etat

    # 5.2 Saisie CEE, 6.2 CEE AH,  8.1 contrôle CEE
    cee_id = fields.Many2one(
        'groupe_cayla.cee',
        delegate=False,
        required=False,
        ondelete='set null'
    )

    type_client_cee = fields.Many2one('groupe_cayla.type_client', compute='_compute_cee',
                                      string="Type client", store=False)
    convention_cee = fields.Many2one('groupe_cayla.convention', compute='_compute_cee',
                                     string="Délégataire", store=False)
    fiche_1_cee = fields.Many2one('groupe_cayla.fiche', compute='_compute_cee',
                                  string="Type d'opération", store=False)
    fiche_2_cee = fields.Many2one('groupe_cayla.fiche', compute='_compute_cee',
                                  string=" ", store=False)
    somme_reversion_cee = fields.Float(compute='_compute_cee', string='Montant');
    somme_primes_cee = fields.Float(compute='_compute_cee', string='Montant HT');

    date_edition_contribution_cee = fields.Date(compute='_compute_cee', string='Edition', store=False)
    utilisateur_edition_contribution_cee = fields.Many2one('res.users', compute='_compute_cee', string='Utilisateur',
                                                           store=False)

    date_edition_ah_cee = fields.Date(compute='_compute_cee', string='Edition', store=False)
    utilisateur_edition_ah_cee = fields.Many2one('res.users', compute='_compute_cee', string='Utilisateur', store=False)

    date_reception_controle_cee = fields.Date(compute='_compute_cee', string='Réception', store=False)
    utilisateur_controle_cee = fields.Many2one('res.users', compute='_compute_cee', string='Utilisateur', store=False)
    date_controle_cee = fields.Date(compute='_compute_cee', string='Contrôle', store=False)
    dossier_valide_controle = fields.Boolean(string='Validé', compute='_compute_cee', store=False)
    date_depot_cee = fields.Date(compute='_compute_cee', string='Dépôt', store=False)
    date_validation_cee = fields.Date(compute='_compute_cee', string='Date de valid.', store=False)

    @api.depends('cee_id')
    def _compute_cee(self):
        for record in self:
            if record.cee_id is None:
                record.type_client_cee = None
                record.convention_cee = None
                record.fiche_1_cee = None
                record.fiche_2_cee = None
                record.somme_primes_cee = None
                record.somme_reversion_cee = None
                record.date_edition_contribution_cee = None
                record.utilisateur_edition_contribution_cee = None
                record.date_edition_ah_cee = None
                record.utilisateur_edition_ah_cee = None
                record.date_reception_controle_cee = None
                record.utilisateur_controle_cee = None
                record.date_controle_cee = None
                record.dossier_valide_controle = None
                record.date_depot_cee = None
                record.date_validation_cee = None

            else:
                record.type_client_cee = record.cee_id.type_client_id
                record.convention_cee = record.cee_id.convention_id
                record.fiche_1_cee = record.cee_id.fiche_1_id
                record.fiche_2_cee = record.cee_id.fiche_2_id
                record.somme_primes_cee = record.cee_id.somme_primes
                record.somme_reversion_cee = record.cee_id.somme_reversion
                record.date_edition_contribution_cee = record.cee_id.contribution_date_edition
                record.utilisateur_edition_contribution_cee = record.cee_id.contribution_user_id
                record.date_edition_ah_cee = record.cee_id.ah_date_edition
                record.utilisateur_edition_ah_cee = record.cee_id.ah_user_id
                record.date_reception_controle_cee = record.cee_id.date_reception
                record.utilisateur_controle_cee = record.cee_id.controle_user_id
                record.date_controle_cee = record.cee_id.date_controle
                record.dossier_valide_controle = record.cee_id.dossier_valide
                record.date_depot_cee = record.cee_id.date_depot
                record.date_validation_cee = record.cee_id.date_validation

    # 6 Planif Chantier
    planif_chantier_id = fields.Many2one(
        'groupe_cayla.planif_chantier',
        delegate=False,
        required=False,
        ondelete='set null'
    )
    date_appel_planif_chantier = fields.Date(compute='_compute_planif_chantier',
                                             string="Date appel", store=False)
    date_time_planif_planif_chantier = fields.Datetime(compute='_compute_planif_chantier',
                                                       string="Chantier planifié", store=False)
    utilisateur_id_planif_chantier = fields.Many2one('res.users', compute='_compute_planif_chantier',
                                                     string="Utilisateur", store=False)
    equipier_1_id_planif_chantier = fields.Many2one('res.users', compute='_compute_planif_chantier',
                                                    string="Equipe", store=False)
    equipier_2_id_planif_chantier = fields.Many2one('res.users', compute='_compute_planif_chantier',
                                                    string=" ", store=False)
    entreprise_planif_chantier = fields.Char(compute='_compute_planif_chantier',
                                             string="Entreprise", store=False)
    entite_edition_devis_id_planif_chantier = fields.Many2one('groupe_cayla.entite_edition_devis',
                                                              compute='_compute_planif_chantier',
                                                              string="Entité devis", store=False)
    entreprise_planif_chantier = fields.Char(compute='_compute_planif_chantier',
                                             string="Entreprise", store=False)

    @api.depends('planif_chantier_id')
    def _compute_planif_chantier(self):
        for record in self:
            if record.planif_chantier_id is None:
                record.entreprise_planif_chantier = None
                record.date_appel_planif_chantier = None
                record.date_time_planif_planif_chantier = None
                record.utilisateur_id_planif_chantier = None
                record.equipier_1_id_planif_chantier = None
                record.equipier_2_id_planif_chantier = None
                record.entreprise_planif_chantier = None
                record.entite_edition_devis_id_planif_chantier = None
            else:
                record.entreprise_planif_chantier = record.planif_chantier_id.entreprise
                record.date_appel_planif_chantier = record.planif_chantier_id.date_appel
                record.date_time_planif_planif_chantier = record.planif_chantier_id.date_time_planif
                record.utilisateur_id_planif_chantier = record.planif_chantier_id.utilisateur_id
                record.equipier_1_id_planif_chantier = record.planif_chantier_id.equipier_1_id
                record.equipier_2_id_planif_chantier = record.planif_chantier_id.equipier_2_id
                record.entreprise_planif_chantier = record.planif_chantier_id.entreprise
                record.entite_edition_devis_id_planif_chantier = record.planif_chantier_id.entite_devis_id

    # 4 Saisie Chantier
    chantier_id = fields.Many2one(
        'groupe_cayla.chantier',
        delegate=False,
        required=False,
        ondelete='set null'
    )
    date_de_realisation_chantier = fields.Date(compute='_compute_chantier',
                                               string="Date de réalisation", store=False)
    equipier_1_id_chantier = fields.Many2one('res.users', compute='_compute_chantier',
                                             string="Equipe", store=False)
    equipier_2_id_chantier = fields.Many2one('res.users', compute='_compute_chantier',
                                             string=" ", store=False)
    produit_chantier = fields.Char(compute='_compute_chantier',
                                   string='Type Produit', store=False)
    marque_produit_chantier = fields.Char(compute='_compute_chantier',
                                          string='Marque', store=False)
    nb_sac_chantier = fields.Integer(compute='_compute_chantier',
                                     string='Nb sac', store=False)
    temps_passe_chantier = fields.Integer(compute='_compute_chantier',
                                          string='Temps passé', store=False)
    chantier_realise_chantier = fields.Boolean(compute='_compute_chantier',
                                               string='Chantier réalisé', store=False)

    @api.depends('chantier_id')
    def _compute_chantier(self):
        for record in self:
            if record.chantier_id is None:
                record.date_de_realisation_chantier = None
                record.equipier_1_id_chantier = None
                record.equipier_2_id_chantier = None
                record.produit_chantier = None
                record.marque_produit_chantier = None
                record.nb_sac_chantier = None
                record.temps_passe_chantier = None
                record.chantier_realise_chantier = None
            else:
                record.date_de_realisation_chantier = record.chantier_id.date_de_realisation
                record.equipier_1_id_chantier = record.chantier_id.equipier_1_id
                record.equipier_2_id_chantier = record.chantier_id.equipier_2_id
                if len(record.chantier_id.lignes_chantier) > 0:
                    record.produit_chantier = record.chantier_id.lignes_chantier[0].produit_id.libelle
                if len(record.chantier_id.lignes_chantier) > 1:
                    record.produit_chantier += ', ...'
                if len(record.chantier_id.lignes_chantier) > 0:
                    record.marque_produit_chantier = record.chantier_id.lignes_chantier[0].marque_produit_id.libelle
                if len(record.chantier_id.lignes_chantier) > 1:
                    record.marque_produit_chantier += ', ...'
                for ligne in record.chantier_id.lignes_chantier:
                    record.nb_sac_chantier += ligne.nb_sacs
                for ligne in record.chantier_id.lignes_chantier:
                    record.temps_passe_chantier += ligne.temps_passe
                record.chantier_realise_chantier = record.chantier_id.chantier_realise

    @api.model
    def default_get(self, fields_list):
        res = models.Model.default_get(self, fields_list)
        france = self.env['res.country'].search([('name', '=', 'France')], limit=1)
        res['country_id'] = france.id
        return res

    def onchange_etat(self):
        if self.prospect_qualifie == 'oui':
            self.etat = 'vt_a_planifier'
        else:
            self.etat = 'annule_telephone'

    @api.model
    def create(self, values):
        # if 'prospect_qualifie' in values :
        #    values['etat'] = 'vt_a_planifier' if values['prospect_qualifie'] == 'oui' else 'annule_telephone'
        rec = super(Client, self).create(values)
        return rec

    @api.multi
    def write(self, vals):
        # if 'prospect_qualifie' in vals and self.etat in('nouveau', 'annule_telephone', 'vt_a_planifier'):
        #    vals['etat'] = 'vt_a_planifier' if vals['prospect_qualifie'] == 'oui' else 'annule_telephone'

        super().write(vals)
        return True
