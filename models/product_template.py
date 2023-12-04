# -*- coding: utf-8 -*-

from odoo import models, api, fields, _


class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    multi_uom_price_id = fields.One2many('product.multi.uom.price', 'product_id', string=_("UOM price"))

    @api.model
    def create(self, vals):
        if vals.get('uom_id', ''):
            uom_id = self.env['uom.uom'].sudo().browse(vals['uom_id'])
            uom_categ = uom_id.category_id

            all_uom = self.env['uom.uom'].sudo().search([('category_id', '=', uom_categ.id), ('active', '=', True), ('id', '!=', uom_id.id)])
            
            uom_obj = self.env['product.multi.uom.price'].sudo()

            list_price = vals.get('list_price')

            res_uom = self.env['product.multi.uom.price']

            new_uom = uom_obj.create({
                "uom_id": uom_id.id,
                "price": list_price
                })

            res_uom |= new_uom

            default_ratio = uom_id.factor if uom_id.uom_type == 'smaller' else uom_id.factor_inv if uom_id.uom_type == "bigger" else 1

            for uom in all_uom:
                current_ratio = uom.factor if uom.uom_type == 'smaller' else uom.factor_inv if uom.uom_type == "bigger" else 1
                temp_uom = uom_obj.create({
                        "uom_id": uom.id,
                        "price": default_ratio * list_price / current_ratio
                    })

                res_uom |= temp_uom

            vals['multi_uom_price_id'] = [(6, 0, res_uom.ids)]
        
        res = super(ProductTemplate, self).create(vals)
        return res

    def write(self, vals):
        if vals.get('uom_id', '') or vals.get('list_price', '') or vals.get('lst_price', ''):
            uom_id = self.env['uom.uom'].sudo().browse(vals['uom_id']) if vals.get('uom_id') else self.uom_id
            uom_categ = uom_id.category_id

            all_uom = self.env['uom.uom'].sudo().search([('category_id', '=', uom_categ.id), ('active', '=', True), ('id', '!=', uom_id.id)])
            
            uom_obj = self.env['product.multi.uom.price'].sudo()

            list_price = vals.get('list_price') or self.list_price

            res_uom = self.env['product.multi.uom.price']

            vals['multi_uom_price_id'] = []

            if uom_id not in self.multi_uom_price_id.mapped('uom_id'):

                values = {
                    "uom_id": uom_id.id,
                    "price": list_price
                    }

                vals['multi_uom_price_id'] = [(0, 0, values)]   

            default_ratio = uom_id.factor if uom_id.uom_type == 'smaller' else uom_id.factor_inv if uom_id.uom_type == "bigger" else 1

            for uom in all_uom:
                if uom not in self.multi_uom_price_id.mapped('uom_id'):
                    current_ratio = uom.factor if uom.uom_type == 'smaller' else uom.factor_inv if uom.uom_type == "bigger" else 1
                    print(uom.name)
                    print(default_ratio ,'*', list_price ,'/', current_ratio)
                    values = {
                            "uom_id": uom.id,
                            "price": default_ratio * list_price / current_ratio
                        }

                    vals['multi_uom_price_id'] += [(0, 0, values)]     
        res = super(ProductTemplate, self).write(vals)
        return res

    def update_multi_uom_price(self):
        for rec in self:
            uom_id = rec.uom_id
            uom_categ = uom_id.category_id

            all_uom = self.env['uom.uom'].sudo().search([('category_id', '=', uom_categ.id), ('active', '=', True), ('id', '!=', uom_id.id)])
            
            uom_obj = self.env['product.multi.uom.price'].sudo()

            list_price = rec.list_price

            res_uom = self.env['product.multi.uom.price']


            if uom_id not in rec.multi_uom_price_id.mapped('uom_id'):

                values = {
                    "uom_id": uom_id.id,
                    "price": list_price
                    }

                rec.write({'multi_uom_price_id': [(0, 0, values)]})   

            default_ratio = uom_id.factor if uom_id.uom_type == 'smaller' else uom_id.factor_inv if uom_id.uom_type == "bigger" else 1

            for uom in all_uom:
                if uom not in rec.multi_uom_price_id.mapped('uom_id'):
                    current_ratio = uom.factor if uom.uom_type == 'smaller' else uom.factor_inv if uom.uom_type == "bigger" else 1
                    values = {
                            "uom_id": uom.id,
                            "price": default_ratio * list_price / current_ratio
                        }

                    rec.write({'multi_uom_price_id': [(0, 0, values)]}) 
