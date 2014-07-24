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
            ------------------------------------------------------------- '''

        # Perform the super update before revalidating the ok flags.
        # This way we can avoid deserializing the vals and the objects
        # in a tiresome comparison process
        # ------------------------------------------------------------
        result = super(product_product, self).write(cr, uid, ids, vals, context=context)
        supplier_db = self.pool.get('product.supplierinfo')

        for product in self.read(cr, uid, ids, ['id', 'procure_method', 'state', 'cost_price', 'seller_ids', 'qty_available'], context=context):

            # Make to order
            # -------------
            if product['procure_method'] == 'make_to_order':
                vals = {'sale_ok' : True, 'purchase_ok' : True}
                if product['state'] == 'obsolete' or len(product['seller_ids']) == 0 or not product['cost_price']:
                    vals = {'sale_ok' : False, 'purchase_ok' : False}
                else:
                    supplier_info = supplier_db.read(cr, uid, product['seller_ids'], ['state'], context=context)
                    if not [x for x in supplier_info if x['state'] == 'available' or x['state'] == 'limited' ]:
                        vals = {'sale_ok' : False, 'purchase_ok' : False}

            # Make to stock
            # -------------
            elif product['procure_method'] == 'make_to_stock':
                vals = {'sale_ok' : True, 'purchase_ok' : False}
                if product['state'] == 'obsolete' or product['qty_available'] == 0:
                    vals['sale_ok'] = False

            super(product_product, self).write(cr, uid, product['id'], vals, context=context)


        return result



















