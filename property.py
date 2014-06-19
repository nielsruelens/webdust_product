from openerp.osv import osv, fields
from openerp.tools.translate import _


class webdust_property(osv.Model):

    _name = "webdust.property"
    _description = "Property extension for products"

    _columns = {
        'name' : fields.char('Name', size=64, required=True),
        'info' : fields.char('Info', size=256),
        'visibility': fields.selection([('internal','Internal'),('external','External')], 'Visibility'),
    }


class webdust_product_property(osv.Model):

    _name = "webdust.product.property"
    _description = "Link between products and properties"

    _columns = {
        'product_id': fields.many2one('product.product', 'Product', select=True, required=True, ondelete='cascade'),
        'name': fields.many2one('webdust.property', 'Property', required=True, ondelete='cascade'),
        'value' : fields.char('Value', size=256, required=True),
    }
