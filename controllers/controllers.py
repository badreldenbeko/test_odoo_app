# -*- coding: utf-8 -*-
# from odoo import http


# class Inquiry(http.Controller):
#     @http.route('/inquiry/inquiry', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/inquiry/inquiry/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('inquiry.listing', {
#             'root': '/inquiry/inquiry',
#             'objects': http.request.env['inquiry.inquiry'].search([]),
#         })

#     @http.route('/inquiry/inquiry/objects/<model("inquiry.inquiry"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('inquiry.object', {
#             'object': obj
#         })

