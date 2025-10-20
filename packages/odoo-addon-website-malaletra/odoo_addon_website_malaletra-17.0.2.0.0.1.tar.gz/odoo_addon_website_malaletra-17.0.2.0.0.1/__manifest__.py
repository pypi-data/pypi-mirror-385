{
    'name': 'Malaletra theme',
    'description': 'Odoo theme for Malaletra',
    'version': '17.0.2.0.0',
    'author': 'amoved | Luis H. Porras',
    'category': 'Website/Theme',
    'depends': ['website','website_sale'],
    'license': 'AGPL-3',
    'data': [
        # Options
        'data/presets.xml',
        # Pages
        'data/pages/home.xml',
        'data/pages/edlp.xml',
        'data/pages/hazte_amiga.xml',
        # Frontend
        'views/website_templates.xml',
        # Images
        'data/images.xml',
    ],
    'assets': {
        'web._assets_primary_variables': [
            'website_malaletra/static/scss/primary_variables.scss',
        ],
        'web._assets_frontend_helpers': [
            ('prepend', 'website_malaletra/static/scss/bootstrap_overridden.scss'),
        ],
        'web.assets_frontend': [
            'website_malaletra/static/scss/style.scss',
            'website_malaletra/static/js/carousel.js',
        ],
    },
    'images': [
        'static/img/theme_malaletra_screenshot.png',
    ],
}
