import base64
import cStringIO
import csv
import datetime

from openerp.osv import fields,osv
from openerp.tools.translate import _

class webdust_product_price_export(osv.TransientModel):
    _name = "webdust.product.price.export"

    _columns = {
            'name': fields.char('File Name', readonly=True),
            'partner': fields.many2one('res.partner', 'Partner', select=True, required=True),
            'data': fields.binary('File', readonly=True),
            'state': fields.selection([('choose', 'choose'),   # choose partner
                                       ('get', 'get')])        # get the file
    }
    _defaults = {
        'state': 'choose',
        'name': 'pricing.csv',
    }

    def act_getfile(self, cr, uid, ids, context=None):
        this = self.browse(cr, uid, ids)[0]
        prices = self.calculate_prices(cr, uid, this.partner)
        filename = '.'.join([this.partner.name, 'csv'])


        buf = cStringIO.StringIO()
        writer = csv.writer(buf, 'UNIX')
        writer.writerow(("id","name","ean13","price"))
        for price in prices:
            writer.writerow((price['id'], price['name'], price['ean13'], price['price']))

        out = base64.encodestring(buf.getvalue())
        buf.close()
        self.write(cr, uid, ids, {'state': 'get',
                                  'data': out,
                                  'name':filename}, context=context)
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'webdust.product.price.export',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': this.id,
            'views': [(False, 'form')],
            'target': 'new',
        }



    def calculate_prices(self, cr, uid, partner):
        today = datetime.datetime.today()
        prod_db = self.pool.get('product.product')
        price_db = self.pool.get('product.pricelist')
        products = prod_db.read(cr, uid, prod_db.search(cr, uid, []), ['id', 'name', 'ean13'])

        for prod in products:
            prod['price'] = price_db.price_get(cr, uid, [partner.property_product_pricelist.id],
                                                         prod['id'], 1.0, partner.id,
                                                         { 'uom': 1, 'date': today, })[partner.property_product_pricelist.id]

        return products
