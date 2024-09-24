from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class CreateRfqWizard(models.TransientModel):
    _name = 'create.rfq.wizard'
    _description = 'Create RFQ Wizard'

    partner_id = fields.Many2one('res.partner')

    def create_new_rfq(self):
        line_id = self.env.context.get('line_id')
        line_type = self.env.context.get('line_type')
        por_id = self.env.context.get('por_id')
        por_object = self.env['purchase.order.request'].search([('id', '=', por_id)], limit=1)
        if line_type:
            if line_type == 'material':
                line_obj = self.env['por.material.line'].search([('id', '=', line_id)], limit=1)
                self._create_single_line_rfq(self.partner_id, por_object, line_obj)
            elif line_type == 'tools':
                line_obj = self.env['por.tools.supplies.line'].search([('id', '=', line_id)], limit=1)
                self._create_single_line_rfq(self.partner_id, por_object, line_obj)
            elif line_type == 'finished':
                line_obj = self.env['por.finish.line'].search([('id', '=', line_id)], limit=1)
                self._create_single_line_rfq(self.partner_id, por_object, line_obj)
            elif line_type == 'semi_finished':
                line_obj = self.env['por.semi.finish.line'].search([('id', '=', line_id)], limit=1)
                self._create_single_line_rfq(self.partner_id, por_object, line_obj)
        else:
            raise ValidationError(
                _(f'There is no line type to create RFQ'))

    def create_multi_rfq(self):
        por_id = self.env.context.get('por_id')
        por_object = self.env['purchase.order.request'].search([('id', '=', por_id)], limit=1)
        lines_objs = list()
        lines_lst = list()
        for line in por_object.por_material_ids:
            if line.selected:
                lines_lst.append(line)
                lines_objs.append((0, 0, {
                    'product_id': line.product_id.id,
                    'product_qty': line.product_qty,
                    'product_uom': line.product_uom_id.id
                }))

        for line in por_object.por_tools_supplies_ids:
            if line.selected:
                lines_lst.append(line)
                lines_objs.append((0, 0, {
                    'product_id': line.product_id.id,
                    'product_qty': line.product_qty,
                    'product_uom': line.product_uom_id.id
                }))

        for line in por_object.por_finish_ids:
            if line.selected:
                lines_lst.append(line)
                lines_objs.append((0, 0, {
                    'product_id': line.product_id.id,
                    'product_qty': line.product_qty,
                    'product_uom': line.product_uom_id.id
                }))

        for line in por_object.por_semi_finish_ids:
            if line.selected:
                lines_lst.append(line)
                lines_objs.append((0, 0, {
                    'product_id': line.product_id.id,
                    'product_qty': line.product_qty,
                    'product_uom': line.product_uom_id.id
                }))
        self._create_multi_line_rfq(self.partner_id, por_object, lines_objs, lines_lst)

    def _create_single_line_rfq(self, partner_id, por_object, line_obj):
        rfq_obj = self.env['purchase.order']
        rfq_vals = {
            'partner_id': partner_id.id,
            'inquiry_id': por_object.bqr_id.inquiry_id.id,
            'bqr_id': por_object.bqr_id.id,
            'por_id': por_object.id,
            'order_line': [(0, 0, {
                'product_id': line_obj.product_id.id,
                'product_qty': line_obj.product_qty,
                'product_uom': line_obj.product_uom_id.id
            })]
        }
        try:
            rfq_obj = rfq_obj.create(rfq_vals)
            line_obj.rfq_ids = [(4, rfq_obj.id)]

            utils = self.env['utils.utils']
            utils.send_group_notification(self.env.user, 'budgetary.quotation.request', rfq_obj.id, 'sales',
                                          'warning',
                                          'BOR Created',
                                          f'New RFQ {rfq_obj.name} Created')
        except Exception as e:
            print(e)

    def _create_multi_line_rfq(self, partner_id, por_object, lines_objs, lines_lst):
        rfq_obj = self.env['purchase.order']
        if not lines_objs:
            raise ValidationError(_(f'No selected lines to create RFQ'))
        rfq_vals = {
            'partner_id': partner_id.id,
            'inquiry_id': por_object.bqr_id.inquiry_id.id,
            'bqr_id': por_object.bqr_id.id,
            'por_id': por_object.id,
            'order_line': lines_objs,
        }
        try:
            rfq_obj = rfq_obj.create(rfq_vals)
            for line in lines_lst:
                line.rfq_ids = [(4, rfq_obj.id)]

            utils = self.env['utils.utils']
            utils.send_group_notification(self.env.user, 'budgetary.quotation.request', rfq_obj.id, 'sales',
                                          'BOR Created',
                                          f'New RFQ {rfq_obj.name} Created')

        except Exception as e:
            print(e)
