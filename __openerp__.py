# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Oppotunity to Blender interface',
    'version': '1.0',
    'category' : 'Modelisation 3D',
    'description': """
     Interface entre UE4 et Odoo
    """,
    'author': ["Agilorg "],
    'website': ['http://www.agilorg.com'],
    'summary': 'Interface odoo-Blender',
    'sequence': 0,
    'depends': ['crm','sale_crm'],
    'data': [
        'views/mbu_crm_view.xml',
        'security/mbu3d_security.xml',
        'security/ir.model.access.csv',],
    'demo': [],
    'auto_install': True,
    'installable': True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
