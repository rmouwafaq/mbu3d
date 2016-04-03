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

class res_partner(osv.osv):  
    
    _inherit= "res.partner" 
    
    def to_dict(self,cr,uid,id=None):
        
        dict_partner={}
        id = self.search(cr,uid, [('id','=',id)])
        
        if id:
            partner = self.browse(cr,uid, id)[0]  
            dict_partner['id']=partner.id
            dict_partner['name']=partner.name
            
            return dict_partner
        else:
            return dict_partner

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
                for ref_prod in blender_select.products.iteritems():
                    product_id = pool_product.search(cr,uid,[('ref_product','=',ref_prod['ref_interne'])])
                    if product_id:
                        lead_prod = {'lead_id':lead_id,
                                     'sequence':sequence,
                                     'name':ref_prod['name'],
                                     'product_id': product_id,
                                     'product_qty':ref_prod['product_qty'],   
                                     }
                        pool_lead_prod.create(cr,uid,lead_prod)
                        sequence +=1 
                    else: 
                        print 'reference produit inexistante ',ref_prod['ref_interne']
    
class mbu_crm_lead_product(osv.osv):
    
    _name = "crm.lead.product"
    _description = "Liste des produits - Model 3D Blender"
    _columns = {
        'lead_id': fields.many2one('crm.lead', 'Lead Reference', required=True, 
                                   ondelete='cascade', select=True, readonly=True),
        'name': fields.char('Description', size=64, required=True, select=True),
        'sequence': fields.integer('Sequence', help="Gives the sequence order when displaying a list of product lines."),
        'product_id': fields.many2one('product.product', 'Product', domain=[('sale_ok', '=', True)], change_default=True, readonly=True, states={'draft': [('readonly', False)]}, ondelete='restrict'),
        'product_qty': fields.float('Quantity ' ,readonly=True),
    }
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
