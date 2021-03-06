# -*- coding: utf-8 -*-
# Copyright 2016 Eficent Business and IT Consulting Services S.L.
#   (http://www.eficent.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "MRP Production Service",
    "summary": "Creates procurement orders from manufacturing orders, for "
               "services included in the Bill of Materials",
    "version": "8.0.1.0.0",
    "author": "Eficent,"
              "Odoo Community Association (OCA)",
    "website": "https://www.odoo-community.org",
    "category": "Warehouse Management",
    "depends": ["stock", "mrp", "procurement_service"],
    "license": "AGPL-3",
    'installable': True,
    'application': False,
}
