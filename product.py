from openerp.osv import osv, fields
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp

class product_product(osv.Model):

    _name = "product.product"
    _inherit = 'product.product'
    _description = "Product extensions"



    def _cost_price(self, cr, uid, ids, field_name, arg, context=None):
        ''' product.product:_cost_price()
            -----------------------------
            This method overwrites the standard OpenERP method to
            calculate the cost price. In case the costing method is
            'lowest', the cost needs to be calculated based on the
            supplier data.
            -------------------------------------------------------- '''

        result = super(product_product, self)._cost_price(cr, uid, ids, field_name, arg, context)

        for product in self.browse(cr, uid, ids):
            if product.cost_method != 'lowest': continue
            lowest = 9999999999
            for supplier in product.seller_ids:
                price = next((x for x in supplier.pricelist_ids if x.min_quantity == 1),None)
                if price and price.price < lowest:
                    lowest = price.price
            if lowest == 9999999999: lowest = 0
            result[product.id] = lowest

        return result

    _columns = {
        'properties': fields.one2many('webdust.product.property', 'product_id', 'Properties'),
        'recommended_price': fields.float('Recommended Price', digits_compute=dp.get_precision('Product Price'), help="Recommended retail price"),
        'short_description': fields.char('Short Description', size=256, required=False),
        'images': fields.one2many('webdust.image', 'product_id', 'Images'),
        'cost_method': fields.selection([('standard','Standard Price'), ('average','Average Price'),('lowest', 'Lowest Price')], 'Costing Method', required=True,
            help="Standard Price: The cost price is manually updated at the end of a specific period (usually every year). \nAverage Price: The cost price is recomputed at each incoming shipment.\nLowest Price: The cost price is recomputed every time the product is changed, based on current supplier pricing data."),
        'cost_price': fields.function(_cost_price,
                                      method=True,
                                      string='Cost Price',
                                      digits_compute = dp.get_precision('Sale Price'),
                                      help="The cost price is the standard price unless you install the product_cost_incl_bom module."),
    }


    _defaults = {
        'cost_method': 'lowest',
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
            qty_available = 0
            seller_ids = 0

            if 'procure_method' in vals: procure_method = vals['procure_method']
            else: procure_method = product.procure_method

            if 'state' in vals: state = vals['state']
            else: state = product.state

            if 'qty_available' in vals: qty_available = vals['qty_available']
            else: qty_available = product.qty_available

            seller_ids = len(product.seller_ids)
            if 'seller_ids' in vals:
                to_delete = [x for x in vals['seller_ids'] if x[0] == 2]
                if to_delete and len(to_delete) == seller_ids and not [x for x in vals['seller_ids'] if x[0] != 2]:
                    seller_ids = 0
                else:
                    seller_ids = 1


            # Draw a conclusion, can this product be sold?
            # --------------------------------------------
            if procure_method == 'make_to_order':

                vals['purchase_ok'] = True
                vals['sale_ok'] = True
                if state == 'obsolete' or seller_ids == 0:
                    vals['purchase_ok'] = False
                    vals['sale_ok'] = False

            elif procure_method == 'make_to_stock':
                vals['sale_ok'] = True
                if state == 'obsolete' or qty_available == 0:
                    vals['sale_ok'] = False


        result = super(product_product, self).write(cr, uid, ids, vals, context=context)
        return result


















