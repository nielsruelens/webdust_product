from openerp.osv import osv, fields
from openerp.tools.translate import _

class webdust_image(osv.Model):

    _name = "webdust.image"
    _description = "Image URLs"


    _columns = {
        'product_id': fields.many2one('product.product', 'Product', select=True, required=True, ondelete='cascade'),
        'supplier': fields.many2one('res.partner','Supplier'),
        'url' : fields.char('URL', size=256, required=True),
    }













