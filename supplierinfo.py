from openerp.osv import osv, fields
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp

class product_supplierinfo(osv.Model):

    _name = "product.supplierinfo"
    _inherit = 'product.supplierinfo'
    _description = "Supplierinfo extensions"



    def _default_price(self, cr, uid, ids, field_name, arg, context=None):
        ''' product.supplierinfo:_default_price()
            -------------------------------------
            This method gives back the default price for this supplier
            for this product.
            ---------------------------------------------------------- '''

        res = dict.fromkeys(ids, False)
        for info in self.browse(cr, uid, ids):
            if not info.pricelist_ids: continue
            res[info.id] = next((x.price for x in info.pricelist_ids if x.min_quantity == 1),None)
        return res

    _columns = {
        'default_price': fields.function(_default_price,
                                      method=True,
                                      string='Lowest Price',
                                      digits_compute = dp.get_precision('Sale Price')),
    }