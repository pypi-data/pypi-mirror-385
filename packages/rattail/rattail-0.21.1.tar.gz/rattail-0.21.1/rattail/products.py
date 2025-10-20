# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2024 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#  details.
#
#  You should have received a copy of the GNU General Public License along with
#  Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Products Handler
"""

import decimal
import warnings
import logging

from rattail import pod
from rattail.app import GenericHandler, MergeMixin
from rattail.gpc import GPC
from rattail.barcodes import upce_to_upca, upc_check_digit


log = logging.getLogger(__name__)


class ProductsHandler(GenericHandler, MergeMixin):
    """
    Base class and default implementation for product handlers.

    A products handler of course should get the final say in how products are
    handled.  This means everything from pricing, to whether or not a
    particular product can be deleted, etc.
    """

    def make_gpc(self, value, ignore_errors=False, **kwargs):
        """
        Try to convert the given value to a GPC, and return the
        result.

        :param value: Value to be converted.  This should be either a
           string or integer value.

        :param ignore_errors: If ``value`` is not valid for a GPC, an
           error will be raised unless this param is set to true.

        :returns: A :class:`~rattail.gpc.GPC` instance.  Or, if the
           ``value`` is not valid, and ``ignore_errors`` was true,
           then returns ``None``.
        """
        # normalize to string; remove unwanted chars
        if not isinstance(value, str):
            value = str(value)
        value = value.replace(' ', '')
        value = value.replace('-', '')

        # auto-handle check digit unless specified
        kwargs.setdefault('calc_check_digit', 'auto')

        try:
            return GPC(value, **kwargs)
        except:
            if not ignore_errors:
                raise

    def make_full_description(self, product=None,
                              brand_name=None, description=None, size=None,
                              **kwargs):
        """
        Return a "full" description for the given product, or
        attributes thereof.

        :param product: Optional, but can be a reference to either a
           :class:`~rattail.db.model.products.Product` or
           :class:`~rattail.db.model.products.PendingProduct`
           instance.

        :param brand_name: Optional; brand name as string.  If not
           provided then will be obtained from ``product`` param.

        :param description: Optional; description as string.  If not
           provided then will be obtained from ``product`` param.

        :param size: Optional; size as string.  If not provided then
           will be obtained from ``product`` param.
        """
        from rattail.db.util import make_full_description

        model = self.model

        if brand_name is None and product:
            if product.brand:
                brand_name = product.brand.name
            elif isinstance(product, model.PendingProduct):
                brand_name = product.brand_name

        if description is None and product:
            description = product.description

        if size is None and product:
            size = product.size

        return make_full_description(brand_name, description, size)

    def upc_check_digits_needed(self, values):
        """
        Figure out whether the given UPC-ish values need to have check
        digits calculated, or if they're already present.

        In practice what this does, is look for any values which *are*
        in need of a check digit.  If any are found, it will be
        assumed that "all" values need a check digit.

        :param values: Sequence of UPC-ish values.  Each value is
           assumed to be a string.

        :returns: Boolean; ``True`` means check digits need to be
           calculated for each value; ``False`` means check digits are
           already present.
        """
        for value in values:

            # assuming the last char in string is the check digit, we
            # calculate again based on all but last char.  if *not* a
            # match, then this value needs a check digit!
            data = value[:-1]
            check = value[-1]
            calculated = upc_check_digit(data)
            if check != calculated:
                return True

        # no check digits needed
        return False

    def units_only(self):
        """
        Returns boolean indicating whether products are "unit only".
        So if this returns ``False`` (the default) then products are
        expected to have case size also.
        """
        return self.config.getbool('rattail', 'products.units_only',
                                   default=False)

    def locate_product_for_entry(
            self,
            session,
            entry,
            include_not_for_sale=False,
            **kwargs):
        """
        This method aims to provide sane default logic for locating a
        :class:`~rattail.db.model.products.Product` record for the
        given "entry" value.

        The default logic here will try to honor the "configured"
        product key field, and prefer that when attempting the lookup.

        :param session: Reference to current DB session.

        :param entry: Value to use for lookup.  This is most often a
           simple string, but the method can handle a few others.  For
           instance it is common to read values from a spreadsheet,
           and sometimes those come through as integers etc.  If this
           value is a :class:`~rattail.gpc.GPC` instance, special
           logic may be used for the lookup.

        :param lookup_fields: Optional list of fields to use for
           lookup.  The default value is ``['uuid', '_product_key_']``
           which means to lookup by UUID as well as "product key"
           field, which is configurable.  You can include any of the
           following in ``lookup_fields``:

           * ``uuid``
           * ``_product_key_`` - :meth:`locate_product_for_key`
           * ``upc`` - :meth:`locate_product_for_upc`
           * ``item_id`` - :meth:`locate_product_for_item_id`
           * ``scancode`` - :meth:`locate_product_for_scancode`
           * ``vendor_code`` - :meth:`locate_product_for_vendor_code`
           * ``alt_code`` - :meth:`locate_product_for_alt_code`

        :param include_not_for_sale: Optional flag to include items
           which are "not for sale" in the search results.

        :returns: First :class:`~rattail.db.model.products.Product`
           instance found if there was a match; otherwise ``None``.
        """
        model = self.model
        if not entry:
            return

        # figure out which fields we should match on
        # TODO: let config declare default lookup_fields
        lookup_fields = kwargs.pop('lookup_fields', [
            'uuid',
            '_product_key_',
        ])
        if kwargs.pop('lookup_vendor_code', False): # pragma: no cover
            warnings.warn("`lookup_vendor_code` param is deprecated, "
                          "please include 'vendor_code' in `lookup_fields` "
                          "instead", DeprecationWarning, stacklevel=2)
            if 'vendor_code' not in lookup_fields:
                lookup_fields.append('vendor_code')
        if kwargs.pop('lookup_by_code', False): # pragma: no cover
            warnings.warn("`lookup_by_code` param is deprecated, "
                          "please include 'alt_code' in `lookup_fields` "
                          "instead", DeprecationWarning, stacklevel=2)
            if 'alt_code' not in lookup_fields:
                lookup_fields.append('alt_code')

        kwargs['include_not_for_sale'] = include_not_for_sale

        # if entry is GPC then only look for that type of match
        if isinstance(entry, GPC):
            return self.locate_product_for_gpc(session, entry, **kwargs)

        # try to locate product by uuid before other, more specific key
        if 'uuid' in lookup_fields:
            if isinstance(entry, str):
                product = session.get(model.Product, entry)
                # TODO: should we ever return deleted product?
                if product and not product.deleted:
                    if include_not_for_sale or not product.not_for_sale:
                        return product

        lookups = {
            'uuid': None,
            '_product_key_': self.locate_product_for_key,
            'upc': self.locate_product_for_upc,
            'item_id': self.locate_product_for_item_id,
            'scancode': self.locate_product_for_scancode,
            'vendor_code': self.locate_product_for_vendor_code,
            'alt_code': self.locate_product_for_alt_code,
        }

        for field in lookup_fields:
            if field in lookups:
                lookup = lookups[field]
                if lookup:
                    product = lookup(session, entry, **kwargs)
                    if product:
                        return product
            else:
                log.warning("unknown lookup field: %s", field)

    def locate_product_for_upc(self, session, entry, **kwargs):
        """
        Locate the product which matches the given UPC value.

        This will do a lookup on the
        :attr:`rattail.db.model.products.Product.upc` field only.

        The ``entry`` value provided is expected to be a string, which
        will be coerced to a :class:`~rattail.gpc.GPC` value in
        various ways while attempting the lookup.  If you already have
        a known-good GPC value then you probably should be using
        :meth:`locate_product_for_gpc()` instead.

        Note that instead of calling this method directly, you might
        consider calling :meth:`locate_product_for_key` instead.

        :param session: Current session for Rattail DB.

        :param entry: String value representing the UPC (or EAN13).

        :returns: First :class:`~rattail.db.model.products.Product`
           instance found if there was a match; otherwise ``None``.
        """
        if not entry:
            return

        # assume entry is string; valid only if all digits
        entry = str(entry)
        if not entry.isdigit():
            return

        # we first assume the user entry *does* include check digit
        provided = self.make_gpc(entry, calc_check_digit=False)
        product = self.locate_product_for_gpc(session, provided, **kwargs)
        if product:
            return product

        # but we can also calculate a check digit and try that
        checked = self.make_gpc(entry, calc_check_digit='upc')
        product = self.locate_product_for_gpc(session, checked, **kwargs)
        if product:
            return product

        # one last trick is to expand UPC-E to UPC-A and then reattempt
        # the lookup, *with* check digit (since it would be known)
        if len(entry) in (6, 8):
            checked = self.make_gpc(upce_to_upca(entry), calc_check_digit='upc')
            product = self.locate_product_for_gpc(session, checked, **kwargs)
            if product:
                return product

    def locate_product_for_item_id(
            self,
            session,
            entry,
            include_not_for_sale=False,
            include_deleted=False,
            **kwargs):
        """
        Locate the product which matches the given item ID.

        This will do a lookup on the
        :attr:`rattail.db.model.products.Product.item_id` field only.

        Note that instead of calling this method directly, you might
        consider calling :meth:`locate_product_for_key` instead.

        :param session: Current session for Rattail DB.

        :param entry: Item ID value as string.

        :param include_not_for_sale: Optional flag to include items
           which are "not for sale" in the search results.

        :param include_deleted: Whether "deleted" products should ever
           match (and be returned).

        :returns: First :class:`~rattail.db.model.products.Product`
           instance found if there was a match; otherwise ``None``.
        """
        from sqlalchemy import orm

        if not entry:
            return

        # assume entry is string
        entry = str(entry)

        model = self.model
        products = session.query(model.Product)
        if not include_deleted:
            products = products.filter(model.Product.deleted == False)
        if not include_not_for_sale:
            products = products.filter(model.Product.not_for_sale == False)

        try:
            return products.filter(model.Product.item_id == entry).one()
        except orm.exc.NoResultFound:
            pass

    def locate_product_for_scancode(
            self,
            session,
            entry,
            include_not_for_sale=False,
            include_deleted=False,
            first_if_multiple=False,
            **kwargs):
        """
        Locate the product which matches the given scancode.

        This will do a lookup on the
        :attr:`rattail.db.model.products.Product.scancode` field only.

        Note that instead of calling this method directly, you might
        consider calling :meth:`locate_product_for_key` instead.

        :param session: Current session for Rattail DB.

        :param entry: Scancode value as string.

        :param include_not_for_sale: Optional flag to include items
           which are "not for sale" in the search results.

        :param include_deleted: Whether "deleted" products should ever
           match (and be returned).

        :param first_if_multiple: If this is true, and multiple
           product matches are found for the given scancode, then the
           "first" match is returned.  Note that this behavior is *not
           determinate* - i.e. no guarantee which match is returned.

           If this is false (the default) and multiple matches are
           found, an error will be raised.

        :returns: First :class:`~rattail.db.model.products.Product`
           instance found if there was a match; otherwise ``None``.
        """
        from sqlalchemy import orm

        if not entry:
            return

        # assume entry is string
        entry = str(entry)

        model = self.model
        products = session.query(model.Product)\
                          .filter(model.Product.scancode == entry)

        if not include_deleted:
            products = products.filter(model.Product.deleted == False)

        if not include_not_for_sale:
            products = products.filter(model.Product.not_for_sale == False)

        if first_if_multiple:
            return products.first()

        try:
            return products.one()
        except orm.exc.NoResultFound:
            pass

    def locate_product_for_key(
            self,
            session,
            entry,
            product_key=None,
            **kwargs):
        """
        Locate the product which matches the given key value.

        This is an abstraction layer so calling logic need not care
        which product key field is configured.  Under the hood this
        will invoke one of:

        * :meth:`locate_product_for_upc`
        * :meth:`locate_product_for_item_id`
        * :meth:`locate_product_for_scancode`

        This will do a lookup on the product key field only.  It
        normally checks config to determine which field to use for
        product key (via
        :meth:`~rattail.config.RattailConfig.product_key()`), but you
        can override by specifying, e.g.  ``product_key='item_id'``.

        :param session: Current session for Rattail DB.

        :param entry: Key value to use for the lookup.

        :param product_key: Optional key field to use for the lookup.
           If not specified, will be read from config.

        :returns: First :class:`~rattail.db.model.products.Product`
           instance if a match was found; otherwise ``None``.
        """
        # prefer caller-provided key over configured key
        if not product_key:
            product_key = self.app.get_product_key_field()

        product = None

        if product_key == 'upc':
            product = self.locate_product_for_upc(session, entry, **kwargs)

        elif product_key == 'item_id':
            product = self.locate_product_for_item_id(session, entry, **kwargs)

        elif product_key == 'scancode':
            product = self.locate_product_for_scancode(session, entry, **kwargs)

        return product

    def locate_product_for_gpc(
            self,
            session,
            gpc,
            type2_lookup=None,
            include_not_for_sale=False,
            **kwargs):
        """
        Try to locate a product for the given GPC value.

        :param session: Current session for Rattail DB.

        :param gpc: :class:`~rattail.gpc.GPC` instance to match on.

        :param type2_lookup: Optional boolean indicating whether a
           "type 2" UPC lookup should be attempted, if applicable.  By
           default, config will determine whether a type 2 lookup may
           be attempted.

        :param include_not_for_sale: Optional flag to include items
           which are "not for sale" in the search results.

        :returns: First :class:`~rattail.db.model.products.Product`
           instance found if there was a match; otherwise ``None``.
        """
        from sqlalchemy import orm

        if not gpc:
            return

        model = self.model

        def lookup(gpc_):
            products = session.query(model.Product)\
                              .filter(model.Product.upc == gpc_)

            # TODO: do we need to support this kwarg?
            #if not kwargs.get('include_deleted'):
            products = products.filter(model.Product.deleted == False)

            if not include_not_for_sale:
                products = products.filter(model.Product.not_for_sale == False)

            # TODO: maybe should just use first() instead?
            try:
                return products.one()
            except orm.exc.NoResultFound:
                pass

        # first we try the normal search
        product = lookup(gpc)
        if product:
            return product

        # maybe also try special search for "Type 2 UPC"
        if gpc.type2_upc:
            if type2_lookup is None:
                type2_lookup = self.convert_type2_for_gpc_lookup()
            if type2_lookup:
                cleaned = self.make_gpc('002{}00000'.format(gpc.data_str[1:6]),
                                        calc_check_digit='upc')
                return lookup(cleaned)

    def convert_type2_for_gpc_lookup(self):
        return self.config.getbool(
            'rattail', 'products.convert_type2_for_gpc_lookup',
            default=False)

    def locate_product_for_vendor_code(
            self,
            session,
            entry,
            vendor=None,
            include_not_for_sale=False,
            **kwargs):
        """
        Locate the product which matches the given vendor code.

        This will do a lookup on the
        :attr:`rattail.db.model.products.ProductCost.code` field only.

        :param session: Current session for Rattail DB.

        :param entry: Vendor item code value as string.

        :param vendor: :class:`~rattail.db.model.vendors.Vendor` to
           which to restrict the search.  While technically optional,
           in most cases you should specify the vendor when doing this
           type of lookup.

        :param include_not_for_sale: Optional flag to include items
           which are "not for sale" in the search results.

        :returns: First :class:`~rattail.db.model.products.Product`
           instance found if there was a match; otherwise ``None``.
        """
        model = self.model
        query = session.query(model.Product)\
                       .join(model.ProductCost)\
                       .filter(model.ProductCost.code == entry)

        if vendor:
            query = query.filter(model.ProductCost.vendor == vendor)

        if not include_not_for_sale:
            query = query.filter(model.Product.not_for_sale == False)

        if not kwargs.get('include_deleted'):
            query = query.filter(model.Product.deleted == False)

        products = query.all()
        if products:

            # when multiple matches are found, prefer the unit item
            # TODO: this still seems rather arbitrary, should add more
            # configurable smarts at some point maybe
            if len(products) > 1:
                units = [p for p in products
                         if p.is_unit_item()]
                if units:
                    return units[0]

            return products[0]

    def locate_product_for_alt_code(
            self,
            session,
            entry,
            include_not_for_sale=False,
            include_deleted=False,
            **kwargs):
        """
        Locate the product which matches the given alternate code.

        This will do a lookup on the
        :attr:`rattail.db.model.products.ProductCode.code` field only.

        :param session: Current session for Rattail DB.

        :param entry: Alternate code value as string.

        :param include_not_for_sale: Optional flag to include items
           which are "not for sale" in the search results.

        :param include_deleted: Whether "deleted" products should ever
           match (and be returned).

        :returns: First :class:`~rattail.db.model.products.Product`
           instance found if there was a match; otherwise ``None``.
        """
        if not entry:
            return

        model = self.model
        products = session.query(model.Product).join(model.ProductCode)
        if not include_not_for_sale:
            products = products.filter(model.Product.not_for_sale == False)
        if not include_deleted:
            products = products.filter(model.Product.deleted == False)
        return products.filter(model.ProductCode.code == entry).first()

    def search_products(self, session, entry, **kwargs):
        """
        Perform a product search across multiple fields, and return
        results as JSON data rows.
        """
        model = self.model
        final_results = []

        # first we'll attempt "lookup" logic..

        lookup_fields = kwargs.get('lookup_fields', [
            '_product_key_',
        ])

        if lookup_fields:
            product = self.locate_product_for_entry(
                session, entry, lookup_fields=lookup_fields)
            if product:
                final_results.append(product)

        # then we'll attempt "search" logic..

        search_fields = kwargs.get('search_fields', [
            'item_id',
            'brand',
            'description',
            'size',
        ])

        searches = {
            'item_id': self.search_products_for_item_id,
            'brand': self.search_products_for_brand,
            'description': self.search_products_for_description,
            'size': self.search_products_for_size,
        }

        for field in search_fields:
            if field in searches:
                search = searches[field]
                if search:
                    products = search(session, entry, **kwargs)
                    final_results.extend(products)
            else:
                log.warning("unknown search field: %s", field)

        return [self.normalize_product(c)
                for c in final_results]

    def search_products_for_item_id(
            self,
            session,
            entry,
            include_not_for_sale=False,
            **kwargs):
        """
        Search for products where the
        :attr:`~rattail.db.model.products.Product.item_id` contains
        the given value.

        :param entry: Search term.

        :param include_not_for_sale: Optional flag to include items
           which are "not for sale" in the search results.

        :returns: List of products matching the search.
        """
        model = self.model
        entry = entry.lower()

        products = session.query(model.Product)\
                          .filter(model.Product.item_id.ilike(f'%{entry}%'))

        if not include_not_for_sale:
            products = products.filter(model.Product.not_for_sale == False)

        return products.all()

    def search_products_for_brand(
            self,
            session,
            entry,
            include_not_for_sale=False,
            **kwargs):
        """
        Search for products where the brand
        :attr:`~rattail.db.model.products.Brand.name` contains the
        given value.

        :param entry: Search term.

        :param include_not_for_sale: Optional flag to include items
           which are "not for sale" in the search results.

        :returns: List of products matching the search.
        """
        model = self.model
        entry = entry.lower()

        products = session.query(model.Product)\
                          .join(model.Brand)\
                          .filter(model.Brand.name.ilike(f'%{entry}%'))

        if not include_not_for_sale:
            products = products.filter(model.Product.not_for_sale == False)

        return products.all()

    def search_products_for_description(
            self,
            session,
            entry,
            include_not_for_sale=False,
            **kwargs):
        """
        Search for products where the
        :attr:`~rattail.db.model.products.Product.description`
        contains the given value.

        :param entry: Search term.

        :param include_not_for_sale: Optional flag to include items
           which are "not for sale" in the search results.

        :returns: List of products matching the search.
        """
        model = self.model
        entry = entry.lower()

        products = session.query(model.Product)\
                          .filter(model.Product.description.ilike(f'%{entry}%'))

        if not include_not_for_sale:
            products = products.filter(model.Product.not_for_sale == False)

        return products.all()

    def search_products_for_size(
            self,
            session,
            entry,
            include_not_for_sale=False,
            **kwargs):
        """
        Search for products where the
        :attr:`~rattail.db.model.products.Product.size` contains the
        given value.

        :param entry: Search term.

        :param include_not_for_sale: Optional flag to include items
           which are "not for sale" in the search results.

        :returns: List of products matching the search.
        """
        model = self.model
        entry = entry.lower()

        products = session.query(model.Product)\
                          .filter(model.Product.size.ilike(f'%{entry}%'))

        if not include_not_for_sale:
            products = products.filter(model.Product.not_for_sale == False)

        return products.all()

    def is_active_for_store(self, product, store, **kwargs):
        """
        Return boolean indicating whether the given product is
        considered "active" at the given store.
        """
        info = product.store_infos.get(store.uuid)
        if info and info.recently_active:
            return True
        return False

    def normalize_product(self, product, fields=None, **kwargs):
        """
        Normalize the given product to a JSON-serializable dict.
        """
        data = {
            'uuid': product.uuid,
            'product_key': self.render_product_key(product),
            'description': product.description,
            'size': product.size,
            '_str': str(product),
            'organic': product.organic,
        }

        if not fields:
            fields = [
                'brand_name',
                'full_description',
                'department_name',
                'unit_price_display',
            ]

        if 'url' in fields:
            data['url'] = self.get_url(product)

        if 'image_url' in fields:
            data['image_url'] = self.get_image_url(product)

        if 'brand_name' in fields:
            data['brand_name'] = product.brand.name if product.brand else None

        if 'full_description' in fields:
            data['full_description'] = self.make_full_description(product)

        if 'department_name' in fields:
            data['department_name'] = product.department.name if product.department else None

        if 'unit_price_display' in fields:
            data['unit_price_display'] = self.render_price(product.regular_price)

        if 'vendor_name' in fields:
            vendor = product.cost.vendor if product.cost else None
            data['vendor_name'] = vendor.name if vendor else None

        if 'costs' in fields:
            costs = []
            for cost in product.costs:
                costs.append({
                    'uuid': cost.uuid,
                    'vendor_uuid': cost.vendor_uuid,
                    'vendor_name': cost.vendor.name,
                    'preference': cost.preference,
                    'code': cost.code,
                    'case_size': cost.case_size,
                    'case_cost': cost.case_cost,
                    'unit_cost': cost.unit_cost,
                })
            data['costs'] = costs

        current_price = None
        if not product.not_for_sale:

            margin_fields = [
                'true_margin',
                'true_margin_display',
            ]
            if any([f in fields for f in margin_fields]):
                if product.volatile:
                    data['true_margin'] = product.volatile.true_margin
                    data['true_margin_display'] = self.app.render_percent(
                        product.volatile.true_margin, places=2)

            current_fields = [
                'current_price',
                'current_price_display',
                'current_ends',
                'current_ends_display',
            ]
            if any([f in fields for f in current_fields]):
                current_price = product.current_price
                if current_price:
                    if current_price.price:
                        data['current_price'] = float(current_price.price)
                    data['current_price_display'] = self.render_price(current_price)
                    current_ends = current_price.ends
                    if current_ends:
                        current_ends = self.app.localtime(current_ends, from_utc=True).date()
                        data['current_ends'] = str(current_ends)
                        data['current_ends_display'] = self.app.render_date(current_ends)

            sale_fields = [
                'sale_price',
                'sale_price_display',
                'sale_ends',
                'sale_ends_display',
            ]
            if any([f in fields for f in sale_fields]):
                sale_price = product.sale_price
                if sale_price:
                    if sale_price.price:
                        data['sale_price'] = float(sale_price.price)
                    data['sale_price_display'] = self.render_price(sale_price)
                    sale_ends = sale_price.ends
                    if sale_ends:
                        sale_ends = self.app.localtime(sale_ends, from_utc=True).date()
                        data['sale_ends'] = str(sale_ends)
                        data['sale_ends_display'] = self.app.render_date(sale_ends)

            tpr_fields = [
                'tpr_price',
                'tpr_price_display',
                'tpr_ends',
                'tpr_ends_display',
            ]
            if any([f in fields for f in tpr_fields]):
                tpr_price = product.tpr_price
                if tpr_price:
                    if tpr_price.price:
                        data['tpr_price'] = float(tpr_price.price)
                    data['tpr_price_display'] = self.render_price(tpr_price)
                    tpr_ends = tpr_price.ends
                    if tpr_ends:
                        tpr_ends = self.app.localtime(tpr_ends, from_utc=True).date()
                        data['tpr_ends'] = str(tpr_ends)
                        data['tpr_ends_display'] = self.app.render_date(tpr_ends)

        if 'case_quantity' in fields:
            data['case_quantity'] = self.app.render_quantity(
                self.get_case_size(product))

        if 'case_price' in fields or 'case_price_display' in fields:
            case_price = None
            if product.regular_price and product.regular_price is not None:
                case_size = self.get_case_size(product)
                # use "current" price if there is one, else normal unit price
                unit_price = product.regular_price.price
                if current_price:
                    unit_price = current_price.price
                case_price = (case_size or 1) * unit_price
                case_price = case_price.quantize(decimal.Decimal('0.01'))
            data['case_price'] = str(case_price) if case_price is not None else None
            data['case_price_display'] = self.app.render_currency(case_price)

        if 'uom_choices' in fields:
            data['uom_choices'] = self.get_uom_choices(product)

        return data

    def get_uom_choices(self, product=None, **kwargs):
        """
        Return a list of UOM choices for the given product, or if no
        product specified then should return the default choices.
        """
        choices = []

        # TODO: not sure how generically useful this method even is? i
        # think it is only used when making a new custorder so far..

        # TODO: for instance "pound" vs. "each" is really just 2 ways
        # of saying "unit" - and does not consider i18n etc.

        # Each
        ea_unit_name = self.enum.UNIT_OF_MEASURE[self.enum.UNIT_OF_MEASURE_EACH]
        if not product or not product.weighed:
            choices.append({'key': self.enum.UNIT_OF_MEASURE_EACH,
                            'value': ea_unit_name})

        # Pound
        lb_unit_name = self.enum.UNIT_OF_MEASURE[self.enum.UNIT_OF_MEASURE_POUND]
        if not product or product.weighed:
            choices.append({'key': self.enum.UNIT_OF_MEASURE_POUND,
                            'value': lb_unit_name})

        unit_name = lb_unit_name if product and product.weighed else ea_unit_name

        # Case
        case_text = None
        case_size = None
        if product:
            case_size = self.get_case_size(product)
        if case_size is None:
            case_text = (f"{self.enum.UNIT_OF_MEASURE[self.enum.UNIT_OF_MEASURE_CASE]} "
                         f"(&times; ?? {unit_name})")
        elif case_size > 1:
            case_text = (f"{self.enum.UNIT_OF_MEASURE[self.enum.UNIT_OF_MEASURE_CASE]} "
                         f"(&times; {self.app.render_quantity(case_size)} {unit_name})")
        if case_text:
            choices.append({'key': self.enum.UNIT_OF_MEASURE_CASE,
                            'value': case_text})

        return choices

    def get_case_size(self, product):
        """
        Return the effective case size for the given product.
        """
        if product.case_size:
            return product.case_size

        cost = product.cost
        if cost:
            return cost.case_size

    def get_url(self, product, **kwargs):
        """
        Return the Tailbone "view" URL for the given product.
        """
        base_url = self.config.base_url()
        if base_url:
            return '{}/products/{}'.format(base_url, product.uuid)

    def get_image_url(self, product=None, upc=None, **kwargs):
        """
        Return the preferred image URL for the given UPC or product.
        """
        base_url = self.config.base_url()

        # we prefer the "image on file" if available
        if base_url and product and product.image:
            return '{}/products/{}/image'.format(base_url, product.uuid)

        # and if this product is a pack item, then we prefer the unit
        # item image as fallback, if available
        if base_url and product and product.is_pack_item():
            unit = product.unit
            if unit and unit.image:
                return '{}/products/{}/image'.format(base_url, unit.uuid)

        # fallback to the POD image, if available and so configured
        if self.config.getbool('tailbone', 'products.show_pod_image',
                               default=False):
            if product and not upc:
                upc = product.upc
            if upc:
                return self.get_pod_image_url(upc)

        if base_url:
            return '{}/tailbone/img/product.png'.format(base_url)

    def get_pod_image_url(self, upc, **kwargs):
        """
        Return the POD image URL for the given UPC.
        """
        if upc:
            return pod.get_image_url(self.config, upc)

    def get_last_sold(self, product, store=None, **kwargs):
        """
        Fetch the "last sold" date for the given product (and store).
        """
        raise NotImplementedError

    def render_product_key(self, product, **kwargs):
        """
        Render the key value for the given product, as human-readable
        text.
        """
        product_key = self.app.get_product_key_field()
        if product_key == 'upc':
            return self.app.render_gpc(product.upc)
        return str(getattr(product, product_key))

    def render_price(self, price, html=False, **kwargs):
        """
        Render the given ``price`` object as text.

        :returns: String containing the rendered price, or ``None`` if
           nothing was applicable.
        """
        if not price:
            return ""
        if price.price is not None and price.pack_price is not None:
            if price.multiple > 1:
                return "{} / {}  ({} / {})".format(
                    self.app.render_currency(price.price),
                    price.multiple,
                    self.app.render_currency(price.pack_price),
                    price.pack_multiple)
            return "{}  ({} / {})".format(
                self.app.render_currency(price.price),
                self.app.render_currency(price.pack_price),
                price.pack_multiple)
        if price.price is not None:
            if price.multiple is not None and price.multiple > 1:
                return "{} / {}".format(
                    self.app.render_currency(price.price),
                    price.multiple)
            return self.app.render_currency(price.price)
        if price.pack_price is not None:
            return "{} / {}".format(
                self.app.render_currency(price.pack_price),
                price.pack_multiple)

    def make_pending_product(self, **kwargs):
        """
        Create and return a new
        :class:`~rattail.db.model.products.PendingProduct` instance,
        per the given kwargs.
        """
        model = self.model
        kwargs.setdefault('status_code', self.enum.PENDING_PRODUCT_STATUS_PENDING)
        pending = model.PendingProduct(**kwargs)
        return pending

    def resolve_product(self, pending, product, user, **kwargs):
        """
        Resolve a pending product.

        :param pending: Reference to a PendingProduct instance.

        :param product: Reference to a Product instance.

        :param user: Reference to the User responsible.
        """
        custorder_handler = self.app.get_custorder_handler()
        custorder_handler.resolve_product(pending, product, user, **kwargs)

        pending.product = product
        pending.resolved = self.app.make_utc()
        pending.resolved_by = user
        pending.status_code = self.enum.PENDING_PRODUCT_STATUS_RESOLVED

    def get_uom_sil_codes(self, session, uppercase=False, **kwargs):
        """
        This should return a dict, keys of which are UOM abbreviation strings,
        and values of which are corresponding SIL code strings.

        :param session: Reference to current Rattail DB session.
        :param uppercase: Set to ``True`` to cause all UOM abbreviations to be
           upper-cased when adding to the map.
        :returns: Dictionary containing all known UOM / SIL code mappings.
        """
        model = self.model

        def normalize(uom):
            if uom.sil_code:
                return uom.sil_code

        def make_key(uom, normal):
            key = uom.abbreviation
            if uppercase:
                key = key.upper()
            return key

        return self.app.cache_model(session,
                                    model.UnitOfMeasure,
                                    normalizer=normalize,
                                    key=make_key)

    def get_uom_sil_code(self, session, uom, uppercase=False, **kwargs):
        """
        This should return a SIL code which corresponds to the given UOM
        abbreviation string.  Useful when you just need one out of the blue,
        but if you need multiple codes looked up then you're probably better
        off using :meth:`get_uom_sil_codes()` for efficiency.

        :param session: Reference to current Rattail DB session.
        :param uppercase: Set to ``True`` to cause the UOM abbreviation to be
           upper-cased before performing the lookup.  This effectively makes
           the search case-insensitive.
        :param uom:  Unit of measure as abbreviated string, e.g. ``'LB'``.
        :returns: SIL code for the UOM, as string (e.g. ``'49'``), or ``None``
           if no matching code was found.
        """
        import sqlalchemy as sa
        from sqlalchemy import orm

        model = self.model
        query = session.query(model.UnitOfMeasure)
        if uppercase:
            query = query.filter(sa.func.upper(model.UnitOfMeasure.abbreviation) == uom.upper())
        else:
            query = query.filter(model.UnitOfMeasure.abbreviation == uom)
        try:
            match = query.one()
        except orm.exc.NoResultFound:
            pass
        else:
            return match.sil_code

    def collect_wild_uoms(self, **kwargs):
        """
        Collect all UOM abbreviations "from the wild" and ensure each is
        represented within the Rattail Units of Measure table.

        Note that you should not need to override this method.  Please override
        :meth:`find_wild_uoms()` instead.
        """
        session = self.make_session()
        model = self.model

        wild_uoms = self.find_wild_uoms(session, **kwargs)

        known_uoms = self.app.cache_model(session,
                                          model.UnitOfMeasure,
                                          key='abbreviation')

        for wild_uom in wild_uoms:
            if wild_uom not in known_uoms:
                uom = model.UnitOfMeasure()
                uom.abbreviation = wild_uom
                session.add(uom)

        session.commit()
        session.close()

    def find_wild_uoms(self, session, **kwargs):
        """
        Query some database(s) in order to discover all UOM abbreviations which
        exist "in the wild".

        You are encouraged to override this method as needed.  Note that
        certain POS integration packages may provide some common logic which
        may be used for this.

        :param session: Reference to current Rattail DB session.

        :returns: A list of strings, e.g. ``['OZ', 'LB', ...]``.
        """
        return []

    def make_future_cost_current(self, future, **kwargs):
        """
        Take the given future cost, and make it current.
        """
        if not future.cost:
            raise NotImplementedError("don't know how to create costs yet")

        cost = future.cost

        if not future.product:
            raise ValueError("future cost does not have product association: {}".format(future))

        if not future.vendor:
            raise ValueError("future cost does not have vendor association: {}".format(future))

        if future.product is not cost.product:
            raise ValueError("product mismatch for future/current costs: {}".format(future))

        if future.vendor is not cost.vendor:
            raise ValueError("vendor mismatch for future/current costs: {}".format(future))

        for field in future_cost_fieldmap:
            setattr(cost, future_cost_fieldmap[field], getattr(future, field))

        session = self.app.get_session(future)
        session.delete(future)
        log.debug("future cost became current: %s", cost)

    def get_merge_preview_fields(self, **kwargs):
        F = self.make_merge_field
        return [
            F('uuid'),
            F('item_id'),
            F('upc'),
            F('brand_name'),
            F('description'),
            F('size'),
            F('department_number'),
            F('department_name'),
            F('subdepartment_number'),
            F('subdepartment_name'),
            F('discontinued'),
            F('deleted'),
        ]

    def get_merge_preview_data(self, product, **kwargs):
        """
        Must return a data dictionary for the given product, which can
        be presented to the user during a merge preview.
        """
        department = product.department
        subdepartment = product.subdepartment
        return {
            'uuid': product.uuid,
            'item_id': product.item_id,
            'upc': product.upc,
            'brand_name': product.brand.name if product.brand else None,
            'description': product.description,
            'size': product.size,
            'department_number': department.number if department else None,
            'department_name': department.name if department else None,
            'subdepartment_number': subdepartment.number if subdepartment else None,
            'subdepartment_name': subdepartment.name if subdepartment else None,
            'discontinued': product.discontinued,
            'deleted': product.deleted,
        }


def get_products_handler(config, **kwargs):
    """
    Create and return the configured :class:`ProductsHandler` instance.
    """
    app = config.get_app()
    spec = config.get('rattail', 'products.handler')
    if spec:
        factory = app.load_object(spec)
    else:
        factory = ProductsHandler
    return factory(config, **kwargs)
