# -*- coding: utf-8 -*-
from odoo import http

class GroupeCayla(http.Controller):
    @http.route('/groupe_cayla/groupe_cayla/', auth='public')
    def index(self, **kw):
        return "Hello, world"

    @http.route('/groupe_cayla/groupe_cayla/objects/', auth='public')
    def list(self, **kw):
        return http.request.render('groupe_cayla.listing', {
            'root': '/groupe_cayla/groupe_cayla',
            'objects': http.request.env['groupe_cayla.groupe_cayla'].search([]),
        })

    @http.route('/groupe_cayla/groupe_cayla/objects/<model("groupe_cayla.groupe_cayla"):obj>/', auth='public')
    def object(self, obj, **kw):
        return http.request.render('groupe_cayla.object', {
            'object': obj
        })