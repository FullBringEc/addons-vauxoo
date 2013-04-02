# -*- encoding: utf-8 -*-
###########################################################################
#    Module Writen to OpenERP, Open Source Management Solution
#
#    Copyright (c) 2010 Vauxoo - http://www.vauxoo.com/
#    All Rights Reserved.
#    info Vauxoo (info@vauxoo.com)
############################################################################
#    Coded by: moylop260 (moylop260@vauxoo.com)
#    Coded by: Fernando Irene Garcia (fernando@vauxoo.com)
#    Launchpad Project Manager for Publication: Nhomar Hernandez - nhomar@vauxoo.com
############################################################################
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

from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import pooler, tools

#~ import wizard
import base64
import time
import datetime
from dateutil.relativedelta import relativedelta

class wizard_invoice_facturae_txt_v6(osv.osv_memory):
    _name = 'wizard.invoice.facturae.txt.v6'
    
    def _get_month_selection(self, cr, uid, context=None):
        months_selection = [
            (1,'January'),
            (2,'February'),
            (3,'March'),
            (4,'April'),
            (5,'May'),
            (6,'June'),
            (7,'July'),
            (8,'August'),
            (9,'September'),
            (10,'October'),
            (11,'November'),
            (12,'December'),
        ]
        return months_selection
        
    _columns = {
        'month':fields.selection(_get_month_selection, 'Mont', type="integer", help='Month to filter'),
        'year':fields.integer('Year', help='Year to filter'),
        'date_start':fields.datetime('Initial Date', help='Initial date for filter'),
        'date_end':fields.datetime('Finished date', help='Finished date for filter'),
        'invoice_ids':fields.many2many('account.invoice', 'invoice_facturae_txt_rel', 'invoice_id', 'facturae_id', "Invoice's", domain="[('type', 'in', ['out_invoice', 'out_refund'] )]", help="Invoice's that meet whit the filter"),
        'facturae':fields.binary("File Electronic Invoice's", readonly=True),
        'facturae_fname':fields.char('File Name', size=64),
        'note':fields.text('Log', readonly=True),
    }
    
    def _get_facturae_fname(self, cr, uid, context=None):
        if context is None:
            context = {}
        return context.get('facturae_fname', 0)
        
    def _get_facturae(self, cr, uid, context=None):
        if context is None:
            context = {}
        return context.get('facturae', 0)

    def _get_note(self, cr, uid, context=None):
        if context is None:
            context = {}
        return context.get('note', 0)
        
    _defaults = {
        'month':lambda*a: int(time.strftime("%m"))-1,
        'year':lambda*a: int(time.strftime("%Y")),
        'date_start':lambda*a: (datetime.datetime.strptime(time.strftime('%Y-%m-01 00:00:00'), '%Y-%m-%d 00:00:00' ) - relativedelta(months=1)).strftime('%Y-%m-%d %H:%M:%S'),
        'date_end':lambda*a: time.strftime('%Y-%m-%d 23:59:59'),
        'facturae_fname':_get_facturae_fname,
        'facturae':_get_facturae,
        'note':_get_note,
    
    }

    def get_invoices_date(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids, context=context)[0]
        #invoice_ids.append(19)
        if not context:
            context = {}
        invoice_obj = self.pool.get('account.invoice')
        if data['invoice_ids']:
            invoice_ids = []
        else:
            invoice_ids = data['invoice_ids']
        date_start = data['date_start']
        date_end = data['date_end']
        #context.update( {'date': date_start.strftime("%Y-%m-%d")} )
        invoice_ids.extend( 
            invoice_obj.search(cr, uid, [
                ( 'type', 'in', ['out_invoice', 'out_refund'] ),
                ( 'state', 'in', ['open', 'paid', 'cancel'] ),
                ( 'invoice_datetime', '>=', date_start ),
                ( 'invoice_datetime', '<', date_end ),
                ( 'number', '<>', False ),
            ], order='invoice_datetime', context=context)
        )
        invoice_ids.extend(
            invoice_obj.search(cr, uid, [
                ( 'type', 'in', ['out_invoice', 'out_refund'] ),
                ( 'state', 'in', ['cancel'] ),
                ( 'date_invoice_cancel', '>=', date_start ),
                ( 'date_invoice_cancel', '<', date_end ),
                ( 'number', '<>', False ),
            ], order='invoice_datetime', context=context)
        )
        self.write(cr, uid, ids, {'invoice_ids': [(6, 0, invoice_ids)] }, context=None)
        return {
            'type': 'ir.actions.act_window',
            'name': 'Electronic Invoice - Report Monthly TXT',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'wizard.invoice.facturae.txt.v6',
            'nodestroy': True,
            'target' : 'new',
            'res_id': ids[0], 
            'views': [(False, 'form')],
            }
        
    def get_invoices_month(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids, context=context)[0]
        if not context:
            context = {}
        invoice_obj = self.pool.get('account.invoice')
        invoice_ids = data['invoice_ids']
        year = data['year']
        month = int(data['month'])
        date_start = datetime.datetime(year, month, 1, 0, 0, 0)
        date_end = date_start + relativedelta(months=1)
        context.update( {'date': date_start.strftime("%Y-%m-%d")} )
        invoice_ids.extend(
            invoice_obj.search(cr, uid, [
                ( 'type', 'in', ['out_invoice', 'out_refund'] ),
                ( 'state', 'in', ['open', 'paid', 'cancel'] ),
                ( 'invoice_datetime', '>=', date_start.strftime("%Y-%m-%d %H:%M:%S") ),
                ( 'invoice_datetime', '<', date_end.strftime("%Y-%m-%d %H:%M:%S") ),
                #( 'number', '<>', False ),
                ( 'internal_number', '<>', False ),
                ], order='invoice_datetime', context=context)
        )
        invoice_ids.extend(  
            invoice_obj.search(cr, uid, [
                ( 'type', 'in', ['out_invoice', 'out_refund'] ),
                ( 'state', 'in', ['cancel'] ),
                ( 'date_invoice_cancel', '>=', date_start.strftime("%Y-%m-%d %H:%M:%S") ),
                ( 'date_invoice_cancel', '<', date_end.strftime("%Y-%m-%d %H:%M:%S") ),
                ( 'internal_number', '<>', False ),
                ], order='invoice_datetime', context=context)
        )
        invoice_ids = list(set(invoice_ids))
        self.write(cr, uid, ids, {'invoice_ids': [(6, 0, invoice_ids)] }, context=None)
        return {
            'type': 'ir.actions.act_window',
            'name': 'Electronic Invoice - Report Monthly TXT',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'wizard.invoice.facturae.txt.v6',
            'nodestroy': True,
            'target' : 'new',
            'res_id': ids[0], 
            'views': [(False, 'form')],
            }

    def create_facturae_txt(self, cr, uid, ids, context=None):
        obj_model = self.pool.get('ir.model.data')
        data = self.read(cr, uid, ids, context=context)[0]
        if not context:
            context = {}
        invoice_obj = self.pool.get('account.invoice')
        invoice_ids = data['invoice_ids']
        if invoice_ids:
            txt_data, fname = invoice_obj._get_facturae_invoice_txt_data(cr, uid, invoice_ids, context=context)
            if txt_data:
                txt_data = base64.encodestring( txt_data )
                context.update({'facturae': txt_data, 'facturae_fname': fname, 'note': _("Open the file & check that the information is correct, folios, RFC, amounts & reported status. \nPlease make sure that not this reporting folios that not belong to electronic invoice's (you can delete in the file directly).\nTIP: Remember that this file too contains folios of credit note.")})
                model_data_ids = obj_model.search(cr,uid,[('model','=','ir.ui.view'),('name','=','view_wizard_invoice_facturae_txt_v6_form2')])
                resource_id = obj_model.read(cr, uid, model_data_ids, fields=['res_id'])[0]['res_id']
                return {
                        'view_type': 'form',
                        'view_mode': 'form',
                        'res_model': 'wizard.invoice.facturae.txt.v6',
                        'views': [(resource_id,'form')],
                        'type': 'ir.actions.act_window',
                        'target': 'new',
                        'context': context,
                        }
        return True
wizard_invoice_facturae_txt_v6()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
