# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2016 Agilorg (<http://www.agilorg.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#e
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################
from openerp import tools
from openerp.osv import fields, osv
from openerp.tools.translate import _


class mbu_crm_lead_blender_model(osv.osv):
    
    _name = "crm.lead.blender.model"
    _description = "Blender Models - Versions"
    _columns = {
        'lead_id': fields.many2one('crm.lead', 'Lead Reference', required=True, 
                                   ondelete='cascade', select=True, readonly=True),
        'user_id': fields.many2one('res.users', 'Utilisateur', required=True, 
                                   ondelete='cascade', select=True, readonly=True),
        'name': fields.char('Description', size=64, required=True, select=True),
        'blender_file' : fields.text('Pathname Blender file'),
    }

    def get_all_blender_model(self,cr,uid,lead_id,context):
        if lead_id:
            blender_ids = self.search(cr,uid,[('lead_id','in',[lead_id])])
            if blender_ids: 
                return self.browse(cr,uid,blender_ids)
        return False
            
            
    def get_last_blender_model(self,cr,uid,lead_id,context):
        sql_query = "SELECT MAX(create_date) FROM crm_lead_blender_model where lead_id in (" + str(lead_id)+")" 
        cr.execute(sql_query)
        blender_model = cr.fetchone()
        if blender_model:
            return blender_model[0] 
        
    def save_last_blender_model(self,cr,uid,lead_id,context):
        blender_select = context.get('blender_select',None)
        if lead_id and blender_select:
            
            self.pool.get('crm.lead').blender_set_products(cr,uid,lead_id,context)
            return self.create(cr,uid,{'lead_id':lead_id,
                                'user_id':uid,
                                'name':blender_select['name'],
                                'blender_file':blender_select['blender_file'],
                                })
        else:
            return False
        
            
        
class mbu_crm_lead(osv.osv):
    _inherit= "crm.lead"
    _columns = { 
               'is_blender_lead': fields.boolean("Mise en scène 3D"), 
               'lead_product_ids': fields.one2many('crm.lead.product', 
                                                'lead_id', 
                                                'Lead Products', readonly=True),
                }
    
    _defaults = {'blender_project': 'none' }
    
    def blender_set_products(self,cr,uid,lead_id,context):
        if lead_id:
            pool_lead_prod = self.pool.get('crm.lead.product')
            lead_prod_ids = pool_lead_prod.search(cr,uid,[('lead_id','in',[lead_id])])
            if lead_prod_ids:
                pool_lead_prod.unlink(cr,uid,lead_prod_ids)
            blender_select = context.get('blender_select',None)
            if blender_select:
                pool_product = self.pool.get('product.product')
                sequence = 0
                items=[]
                for ref_prod, quantity in blender_select['products'].iteritems():
                    product_id = pool_product.search(cr,uid,[('default_code','=',ref_prod)])[0]
                    if product_id:
                        lead_prod = {'lead_id':lead_id,
                                     'sequence':sequence,
                                     'name':ref_prod,
                                     'product_id': product_id,
                                     'product_qty':quantity,   
                                     }
                        items.append((0,0,lead_prod))
                        sequence +=1 
                    else: 
                        print 'reference produit inexistante ',ref_prod
                
        return self.write(cr,uid,lead_id,{'lead_product_ids':items})
    
class mbu_crm_lead_product(osv.osv):
    
    _name = "crm.lead.product"
    _description = "Liste des produits - Model 3D Blender"
    _columns = {
        'lead_id': fields.many2one('crm.lead', 'Lead Reference', required=True, 
                                   ondelete='cascade', select=True, readonly=True),
        'name': fields.char('Description', size=64),
        'sequence': fields.integer('Sequence', help="Gives the sequence order when displaying a list of product lines."),
        'product_id': fields.many2one('product.product', 'Product', ondelete='restrict'),
        'product_qty': fields.float('Quantity ' ,readonly=True),
    }
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

class crm_make_sale(osv.osv_memory):
    _inherit= "crm.make.sale"
    
    def makeOrder(self, cr, uid, ids, context=None):
        """
        This function  create Quotation on given case.
        @param self: The object pointer
        @param cr: the current row, from the database cursor,
        @param uid: the current user’s ID for security checks,
        @param ids: List of crm make sales' ids
        @param context: A standard dictionary for contextual values
        @return: Dictionary value of created sales order.
        """
        # update context: if come from phonecall, default state values can make the quote crash lp:1017353
        context = dict(context or {})
        context.pop('default_state', False)        
        
        case_obj = self.pool.get('crm.lead')
        sale_obj = self.pool.get('sale.order')
        partner_obj = self.pool.get('res.partner')
        data = context and context.get('active_ids', []) or []

        for make in self.browse(cr, uid, ids, context=context):
            partner = make.partner_id
            partner_addr = partner_obj.address_get(cr, uid, [partner.id],
                    ['default', 'invoice', 'delivery', 'contact'])
            pricelist = partner.property_product_pricelist.id
            fpos = partner.property_account_position and partner.property_account_position.id or False
            payment_term = partner.property_payment_term and partner.property_payment_term.id or False
            new_ids = []
            for case in case_obj.browse(cr, uid, data, context=context):
                
                if not partner and case.partner_id:
                    partner = case.partner_id
                    fpos = partner.property_account_position and partner.property_account_position.id or False
                    payment_term = partner.property_payment_term and partner.property_payment_term.id or False
                    partner_addr = partner_obj.address_get(cr, uid, [partner.id],
                            ['default', 'invoice', 'delivery', 'contact'])
                    pricelist = partner.property_product_pricelist.id
                if False in partner_addr.values():
                    raise osv.except_osv(_('Insufficient Data!'), _('No address(es) defined for this customer.'))
 
                vals = {
                    'origin': _('Opportunity: %s') % str(case.id),
                    'section_id': case.section_id and case.section_id.id or False,
                    'categ_ids': [(6, 0, [categ_id.id for categ_id in case.categ_ids])],
                    'partner_id': partner.id,
                    'pricelist_id': pricelist,
                    'partner_invoice_id': partner_addr['invoice'],
                    'partner_shipping_id': partner_addr['delivery'],
                    'date_order': fields.datetime.now(),
                    'fiscal_position': fpos,
                    'payment_term':payment_term,
                    'note': sale_obj.get_salenote(cr, uid, [case.id], partner.id, context=context),
                }
                
                if case.is_blender_lead:
                    orderlines = self.prepare_quotation_lines(cr, uid,case,context=context)
                    vals.update({'order_line':orderlines})
                    
                if partner.id:
                    vals['user_id'] = partner.user_id and partner.user_id.id or uid
                new_id = sale_obj.create(cr, uid, vals, context=context)
                sale_order = sale_obj.browse(cr, uid, new_id, context=context)
                case_obj.write(cr, uid, [case.id], {'ref': 'sale.order,%s' % new_id})
                new_ids.append(new_id)
                message = _("Opportunity has been <b>converted</b> to the quotation <em>%s</em>.") % (sale_order.name)
                case.message_post(body=message)
            if make.close:
                case_obj.case_mark_won(cr, uid, data, context=context)
            if not new_ids:
                return {'type': 'ir.actions.act_window_close'}
            if len(new_ids)<=1:
                value = {
                    'domain': str([('id', 'in', new_ids)]),
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'sale.order',
                    'view_id': False,
                    'type': 'ir.actions.act_window',
                    'name' : _('Quotation'),
                    'res_id': new_ids and new_ids[0]
                }
            else:
                value = {
                    'domain': str([('id', 'in', new_ids)]),
                    'view_type': 'form',
                    'view_mode': 'tree,form',
                    'res_model': 'sale.order',
                    'view_id': False,
                    'type': 'ir.actions.act_window',
                    'name' : _('Quotation'),
                    'res_id': new_ids
                }
            return value

    def prepare_quotation_lines(self, cr, uid, case, context=None):        
        orderlines=[]
        for line in case.lead_product_ids:
            product = self.pool.get('product.product').browse(cr, uid, line.product_id.id, context=context)
            if product:
                orderlines.append((0,0,{'product_id'        :product.id,
                                        'product_uom_qty'   :line.product_qty,
                                        'name'              :product.name,
                                        'product_uom'       :product.uom_id.id,
                                        'price_unit'        :product.lst_price,
                                        'tax_id'            :[(6,0,[tax_id.id for tax_id in product.taxes_id])]
                                        }))
        return orderlines