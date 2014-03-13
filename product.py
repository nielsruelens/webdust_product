from openerp.osv import osv, fields
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp

class product_product(osv.Model):

    _name = "product.product"
    _inherit = 'product.product'
    _description = "Product extensions"


    _columns = {
        'properties': fields.one2many('webdust.product.property', 'product_id', 'Properties'),
        'recommended_price': fields.float('Recommended Price', digits_compute=dp.get_precision('Product Price'), help="Recommended retail price"),
        'short_description': fields.char('Short Description', size=256, required=False),
        'images': fields.one2many('webdust.image', 'product_id', 'Images'),
    }



    def write(self, cr, uid, ids, vals, context=None):
        ''' product.product:write()
            -----------------------
            This method overwrites the standard OpenERP write() method
            to make sure all required pricing/availability stays in sync.
            The extension only applies if it the method is called for
            a single product.
            ------------------------------------------------------------- '''

        if len(ids) == 1:
            (product,) = self.browse(cr, uid, ids, context=context)

            procure_method = False
            state = False
            sale_ok = False
            purchase_ok = False
            qty_available = 0
            seller_ids = 0

            if 'procure_method' in vals:
                procure_method = vals['procure_method']
            else:
                procure_method = product.procure_method

            if 'state' in vals:
                state = vals['state']
            else:
                state = product.state

            if 'sale_ok' in vals:
                sale_ok = vals['sale_ok']
            else:
                sale_ok = product.sale_ok

            if 'purchase_ok' in vals:
                purchase_ok = vals['purchase_ok']
            else:
                purchase_ok = product.purchase_ok

            if 'qty_available' in vals:
                qty_available = vals['qty_available']
            else:
                qty_available = product.qty_available

            seller_ids = len(product.seller_ids)
            if 'seller_ids' in vals:
                to_delete = [x for x in vals['seller_ids'] if x[0] == 2]
                if to_delete and len(to_delete) == seller_ids and not [x for x in vals['seller_ids'] if x[0] != 2]:
                    seller_ids = 0
                else:
                    seller_ids = 1




            if procure_method == 'make_to_order':

                if state == 'obsolete' or purchase_ok == False or sale_ok == False or seller_ids == 0:
                    vals['purchase_ok'] = False
                    vals['sale_ok'] = False

            elif procure_method == 'make_to_stock':
                if state == 'obsolete' or qty_available == 0:
                    vals['sale_ok'] = False


        result = super(product_product, self).write(cr, uid, ids, vals, context=context)
        return result

















