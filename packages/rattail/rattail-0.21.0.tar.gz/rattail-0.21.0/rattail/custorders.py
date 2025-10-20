# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2023 Lance Edgar
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
Customer Orders Handler

Please note this is different from the Customer Order Batch Handler.
"""

import decimal

from rattail.app import GenericHandler


class CustomerOrderHandler(GenericHandler):
    """
    Base class and default implementation for customer order handlers.
    """

    def get_default_item_discount(self, product=None, **kwargs):
        """
        Returns default item discount available.  If product is given,
        the default may be specific to its department etc.
        """
        if product:
            department = product.department
            if department and department.default_custorder_discount is not None:
                return department.default_custorder_discount

        discount = self.config.get('rattail.custorders',
                                   'default_item_discount')
        if discount:
            return decimal.Decimal(discount)

    def resolve_person(self, pending, person, user, **kwargs):
        """
        Resolve a pending person for all customer orders.
        """
        for order in list(pending.custorder_records):
            order.person = person
            order.pending_customer = None
            for item in order.items:
                item.add_event(self.enum.CUSTORDER_ITEM_EVENT_CUSTOMER_RESOLVED,
                               user)

    def resolve_product(self, pending, product, user, **kwargs):
        """
        Resolve a pending product for all customer orders.
        """
        for item in pending.custorder_item_records:
            item.product = product
            item.pending_product = None

            item.product_upc = product.upc
            item.product_item_id = product.item_id
            item.product_scancode = product.scancode
            item.product_brand = product.brand.name if product.brand else None
            item.product_description = product.description
            item.product_size = product.size

            # TODO: not sure this is needed really?
            item.product_weighed = product.weighed

            # TODO: model notes say this is not needed
            #item.product_unit_of_measure = product.unit_of_measure

            department = product.department
            item.department_number = department.number if department else None
            item.department_name = department.name if department else None

            # TODO: should be smarter about getting this
            item.case_quantity = product.case_size

            cost = product.cost
            item.product_unit_cost = cost.unit_cost if cost else None

            regprice = product.regular_price
            item.unit_regular_price = regprice.price if regprice else None

            curprice = product.current_price
            item.unit_sale_price = curprice.price if curprice else None
            item.sale_ends = curprice.ends if curprice else None

            item.unit_price = item.unit_sale_price or item.unit_regular_price

            # TODO: should recalculate total price
            #item.total_price = ...

            item.add_event(self.enum.CUSTORDER_ITEM_EVENT_PRODUCT_RESOLVED,
                           user)

    def mark_received(self, order_items, user, **kwargs):
        """
        Mark the given set of customer order items as having been
        received (i.e. from the vendor).
        """
        model = self.model

        event_kw = {
            'type_code': self.enum.CUSTORDER_ITEM_EVENT_RECEIVED,
            'user': user,
            'note': kwargs.get('note'),
        }

        for item in order_items:
            item.status_code = self.enum.CUSTORDER_ITEM_STATUS_RECEIVED
            item.status_text = None
            item.events.append(model.CustomerOrderItemEvent(**event_kw))

    def add_note(self, item, note_text, user, apply_all=False, **kwargs):
        """
        Add a note to the given order item.

        :param apply_all: If set, the note should be added to all
           items on the order, instead of just the one item given.
        """
        model = self.model

        if apply_all:
            items = item.order.items
        else:
            items = [item]

        occurred = kwargs.get('occurred')
        for item in items:
            item.events.append(model.CustomerOrderItemEvent(
                type_code=self.enum.CUSTORDER_ITEM_EVENT_NOTE_ADDED,
                user=user, note=note_text, occurred=occurred))
