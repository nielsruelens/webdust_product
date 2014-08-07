{
    'name': 'webdust_product',
    'version': '1.0',
    'category': 'Purchasing',
    'description': "Product Extensions",
    'author': 'Niels Ruelens',
    'website': 'http://clubit.be',
    'summary': "Product Extensions",
    'sequence': 9,
    'depends': [
        'purchase',
        'product',
        'base',
    ],
    'data': [
        'product.xml',
        'property.xml',
        'supplierinfo.xml',
        'wizard/price_export_view.xml'
    ],
    'demo': [
    ],
    'test': [
    ],
    'css': [
    ],
    'images': [
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}