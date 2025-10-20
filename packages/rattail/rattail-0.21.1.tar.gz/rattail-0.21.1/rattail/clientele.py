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
Clientele Handler
"""

from collections import OrderedDict
import logging
import warnings

from rattail.app import GenericHandler


log = logging.getLogger(__name__)


class ClienteleHandler(GenericHandler):
    """
    Base class and default implementation for clientele handlers.
    """

    def choice_uses_dropdown(self):
        """
        Returns boolean indicating whether a customer choice should be
        presented to the user via a dropdown (select) element, vs.  an
        autocomplete field.  The latter is the default because
        potentially the customer list can be quite large, so we avoid
        loading them all in the dropdown unless so configured.

        :returns: Boolean; if true then a dropdown should be used;
           otherwise (false) autocomplete is used.
        """
        return self.config.getbool('rattail', 'customers.choice_uses_dropdown',
                                   default=False)

    def ensure_customer(self, person):
        """
        Returns the customer record associated with the given person, creating
        it first if necessary.
        """
        customer = self.get_customer(person)
        if customer:
            return customer

        session = self.app.get_session(person)
        customer = self.make_customer(person)
        return customer

    def get_customer(self, obj):
        """
        Return the Customer associated with the given object, if any.
        """
        model = self.model

        if isinstance(obj, model.Customer):
            return obj

        else:
            person = self.app.get_person(obj)
            if person:
                # TODO: all 3 options below are indeterminate, since it's
                # *possible* for a person to hold multiple accounts
                # etc. but not sure how to fix in a generic way?  maybe
                # just everyone must override as needed
                if person.customer_accounts:
                    return person.customer_accounts[0]
                for shopper in person.customer_shoppers:
                    if shopper.shopper_number == 1:
                        return shopper.customer
                # legacy fallback
                if person.customers:
                    return person.customers[0]

    def get_email_address(self, customer, **kwargs):
        """
        Return the first email address found for the given customer.

        :returns: The email address as string, or ``None``.
        """
        warnings.warn("clientele.get_email_address(customer) is deprecated; please "
                      "use app.get_contact_email_address(customer) instead",
                      DeprecationWarning, stacklevel=2)
        return self.app.get_contact_email_address(customer)

    def get_all_customers(self, session, include_inactive=False, **kwargs):
        """
        Get the full list of customers, e.g. for dropdown choice.

        :param include_inactive: Flag indicating if "inactive"
           customers should be included.  This is false by default, in
           which case only "active" customers are returned.

        :returns: List of
           :class:`~rattail.db.model.customers.Customer` objects.
        """
        import sqlalchemy as sa

        model = self.model
        customers = session.query(model.Customer)\
                           .order_by(model.Customer.name)

        if not include_inactive:
            customers = customers.filter(sa.or_(
                model.Customer.active_in_pos == True,
                model.Customer.active_in_pos == None))

        return customers.all()

    def get_customers_for_account_holder(
            self,
            person,
            **kwargs
    ):
        """
        Return all Customer records for which the given Person is the
        account holder.
        """
        customers = OrderedDict()

        # find customers for which person is account holder
        for customer in person.customer_accounts:
            customers.setdefault(customer.uuid, customer)

        # find customers for which person is primary shopper
        for shopper in person.customer_shoppers:
            if shopper.shopper_number == 1:
                customer = shopper.customer
                customers.setdefault(customer.uuid, customer)

        # nb. legacy
        for customer in person.customers:
            customers.setdefault(customer.uuid, customer)

        return list(customers.values())

    def get_active_shopper(
            self,
            customer,
            **kwargs
    ):
        """
        Return the "active" shopper record for the given customer.

        This should never return multiple shoppers, either one or none.
        """
        for shopper in customer.shoppers:
            if shopper.active:
                return shopper

    def deactivate_shopper(self, shopper, **kwargs):
        """
        Deactivate the given shopper, i.e. make it no longer active
        for the customer account to which it belongs.

        :param shopper: The shopper to be deactivated.

        :param end_date: Optional end date for the deactivation.  If
           not specified, "today" is assumed.
        """
        # declare end date for current shopper history, if applicable
        if 'end_date' in kwargs:
            end_date = kwargs['end_date']
        else:
            end_date = self.app.today()
        if end_date:
            history = shopper.get_current_history()
            if history:
                history.end_date = end_date

        # mark shopper as no longer active
        shopper.active = False

    def shopper_was_active(self, shopper, date, **kwargs):
        """
        Inspect the shopper's history to determine if it was
        considered *active* (for the parent customer account) on the
        given date.

        :param shopper: The shopper to be checked.

        :param date: The date to be checked.

        :returns: Boolean indicating whether shopper was active on
           that date.
        """
        # try to find (all) applicable history for shopper
        applicable = []
        for history in reversed(shopper.history):
            if history.start_date > date:
                # this history began after the date
                continue
            if history.end_date and history.end_date < date:
                # this history ended before the date
                continue
            # okay, got one
            applicable.append(history)

        # if we found at least one "applicable" history record, that
        # means the shopper *was* indeed active on this date
        if applicable:
            # nb. there should only be *one* applicable record,
            # otherwise overlapping history records are implied
            if len(applicable) != 1:
                log.error("found (%s) applicable history records for shopper %s: %s",
                          len(applicable), shopper.uuid, shopper)
            return True

        # if we can't prove shopper was active, we assume they were *inactive*
        return False

    def get_person(self, customer):
        """
        Returns the person associated with the given customer, if there is one.
        """
        warnings.warn("ClienteleHandler.get_person() is deprecated; "
                      "please use AppHandler.get_person() instead")

        return self.app.get_person(customer)

    def make_customer(self, person, **kwargs):
        """
        Create and return a new customer record.
        """
        session = self.app.get_session(person)
        customer = self.model.Customer()
        customer.name = person.display_name
        customer.account_holder = person
        session.add(customer)
        session.flush()
        session.refresh(person)
        return customer

    def locate_customer_for_entry(self, session, entry, **kwargs):
        """
        This method aims to provide sane default logic for locating a
        :class:`~rattail.db.model.customers.Customer` record for the
        given "entry" value.

        The default logic here will try to honor the "configured"
        customer field, and prefer that when attempting the lookup.

        :param session: Reference to current DB session.

        :param entry: Value to use for lookup.  This is most often a
           simple string, but the method can handle a few others.  For
           instance it is common to read values from a spreadsheet,
           and sometimes those come through as integers etc.

        :param lookup_fields: Optional list of fields to use for
           lookup.  The default value is ``['uuid', '_customer_key_']``
           which means to lookup by UUID as well as "customer key"
           field, which is configurable.  You can include any of the
           following in ``lookup_fields``:

           * ``uuid``
           * ``_customer_key_`` - :meth:`locate_customer_for_key`

        :returns: First :class:`~rattail.db.model.customers.Customer`
           instance found if there was a match; otherwise ``None``.
        """
        model = self.model
        if not entry:
            return

        # figure out which fields we should match on
        # TODO: let config declare default lookup_fields
        lookup_fields = kwargs.get('lookup_fields', [
            'uuid',
            '_customer_key_',
        ])

        # try to locate customer by uuid before other, more specific key
        if 'uuid' in lookup_fields:
            if isinstance(entry, str):
                customer = session.get(model.Customer, entry)
                if customer:
                    return customer

        lookups = {
            'uuid': None,
            '_customer_key_': self.locate_customer_for_key,
        }

        for field in lookup_fields:
            if field in lookups:
                lookup = lookups[field]
                if lookup:
                    customer = lookup(session, entry, **kwargs)
                    if customer:
                        return customer
            else:
                log.warning("unknown lookup field: %s", field)

    def locate_customer_for_key(self, session, entry, customer_key=None, **kwargs):
        """
        Locate the customer which matches the given key value.

        This is an abstraction layer so calling logic need not care
        which customer key field is configured.  Under the hood this
        will invoke one of:

        * :meth:`locate_customer_for_id`
        * :meth:`locate_customer_for_number`

        This will do a lookup on the customer key field only.  It
        normally checks config to determine which field to use for
        customer key (via
        :meth:`~rattail.app.AppHandler.get_customer_key_field()`), but
        you can override by specifying, e.g.
        ``customer_key='number'``.

        :param session: Current session for Rattail DB.

        :param entry: Key value to use for the lookup.

        :param customer_key: Optional key field to use for the lookup.
           If not specified, will be read from config.

        :returns: First :class:`~rattail.db.model.customers.Customer`
           instance if a match was found; otherwise ``None``.
        """
        # prefer caller-provided key over configured key
        if not customer_key:
            customer_key = self.app.get_customer_key_field()

        customer = None

        if customer_key == 'id':
            customer = self.locate_customer_for_id(session, entry, **kwargs)

        elif customer_key == 'number':
            customer = self.locate_customer_for_number(session, entry, **kwargs)

        return customer

    def locate_customer_for_id(self, session, entry, **kwargs):
        """
        Locate the customer which matches the given ID.

        This will do a lookup on the
        :attr:`rattail.db.model.customers.Customer.id` field only.

        Note that instead of calling this method directly, you might
        consider calling :meth:`locate_customer_for_key()` instead.

        :param session: Current session for Rattail DB.

        :param entry: Customer ID value as string.

        :returns: First :class:`~rattail.db.model.customers.Customer`
           instance found if there was a match; otherwise ``None``.
        """
        from sqlalchemy import orm

        if not entry:
            return

        # assume entry is string
        entry = str(entry)

        model = self.model
        try:
            return session.query(model.Customer)\
                          .filter(model.Customer.id == entry).one()
        except orm.exc.NoResultFound:
            pass

    def locate_customer_for_number(self, session, entry, **kwargs):
        """
        Locate the customer which matches the given number.

        This will do a lookup on the
        :attr:`rattail.db.model.customers.Customer.number` field only.

        Note that instead of calling this method directly, you might
        consider calling :meth:`locate_customer_for_key()` instead.

        :param session: Current session for Rattail DB.

        :param entry: Customer number, as integer or string.

        :returns: First :class:`~rattail.db.model.customers.Customer`
           instance found if there was a match; otherwise ``None``.
        """
        from sqlalchemy import orm

        if not entry:
            return

        # assume entry is integer
        try:
            entry = int(entry)
        except:
            log.debug("cannot coerce to integer: %s", entry)
            return

        model = self.model
        try:
            return session.query(model.Customer)\
                          .filter(model.Customer.number == entry).one()
        except orm.exc.NoResultFound:
            pass

    def search_customers(self, session, entry, **kwargs):
        """
        Perform a customer search across multiple fields, and return
        results as JSON data rows.
        """
        model = self.model
        final_results = []

        # first we'll attempt "lookup" logic..

        lookup_fields = kwargs.get('lookup_fields', [
            '_customer_key_',
        ])

        if lookup_fields:
            customer = self.locate_customer_for_entry(
                session, entry, lookup_fields=lookup_fields)
            if customer:
                final_results.append(customer)

        # then we'll attempt "search" logic..

        search_fields = kwargs.get('search_fields', [
            'name',
            'email_address',
            'phone_number',
        ])

        searches = {
            'name': self.search_customers_for_name,
            'email_address': self.search_customers_for_email_address,
            'phone_number': self.search_customers_for_phone_number,
        }

        for field in search_fields:
            if field in searches:
                search = searches[field]
                if search:
                    customers = search(session, entry, **kwargs)
                    final_results.extend(customers)
            else:
                log.warning("unknown search field: %s", field)

        return [self.normalize_customer(c)
                for c in final_results]

    def search_customers_for_name(self, session, entry, **kwargs):
        model = self.model
        entry = entry.lower()

        customers = session.query(model.Customer)\
                           .filter(model.Customer.name.ilike(f'%{entry}%'))\
                           .all()
        results = customers

        return results

    def search_customers_for_email_address(self, session, entry, **kwargs):
        model = self.model
        entry = entry.lower()

        customers = session.query(model.Customer)\
                           .join(model.CustomerEmailAddress,
                                 model.CustomerEmailAddress.parent_uuid == model.Customer.uuid)\
                           .filter(model.CustomerEmailAddress.address.ilike(f'%{entry}%'))\
                           .all()
        results = customers

        customers = session.query(model.Customer)\
                           .join(model.Person)\
                           .join(model.PersonEmailAddress,
                                 model.PersonEmailAddress.parent_uuid == model.Person.uuid)\
                           .filter(model.PersonEmailAddress.address.ilike(f'%{entry}%'))\
                           .all()
        results.extend(customers)

        return results

    def search_customers_for_phone_number(self, session, entry, **kwargs):
        model = self.model
        entry = entry.lower()

        customers = session.query(model.Customer)\
                           .join(model.CustomerPhoneNumber,
                                 model.CustomerPhoneNumber.parent_uuid == model.Customer.uuid)\
                           .filter(model.CustomerPhoneNumber.number.ilike(f'%{entry}%'))\
                           .all()
        results = customers

        customers = session.query(model.Customer)\
                           .join(model.Person)\
                           .join(model.PersonPhoneNumber,
                                 model.PersonPhoneNumber.parent_uuid == model.Person.uuid)\
                           .filter(model.PersonPhoneNumber.number.ilike(f'%{entry}%'))\
                           .all()
        results.extend(customers)

        return results

    def normalize_customer(self, customer, fields=None, **kwargs):
        """
        Normalize the given customer to a JSON-serializable dict.
        """
        key = self.app.get_customer_key_field()
        return {
            'uuid': customer.uuid,
            '_customer_key_': getattr(customer, key),
            'id': customer.id,
            'number': customer.number,
            'name': customer.name,
            'phone_number': self.app.get_contact_phone_number(customer),
            'email_address': self.app.get_contact_email_address(customer),
            '_str': str(customer),
        }

    def get_customer_info_markdown(self, customer, **kwargs):
        """
        Returns a Markdown string containing pertinent info about a
        given customer account.
        """
        key_field = self.app.get_customer_key_field()
        key_label = self.app.get_customer_key_label()
        phone = self.app.get_contact_phone_number(customer)
        email = self.app.get_contact_email_address(customer)
        return (f"{key_label}: {getattr(customer, key_field)}\n\n"
                f"Name: {customer.name}\n\n"
                f"Phone: {phone or ''}\n\n"
                f"Email: {email or ''}\n\n")

    def get_first_phone(self, customer, **kwargs):
        """
        Return the first available phone record found, either for the
        customer, or its first person.
        """
        phone = customer.first_phone()
        if phone:
            return phone

        person = self.app.get_person(customer)
        if person:
            return person.first_phone()

    def get_first_phone_number(self, customer, **kwargs):
        """
        Return the first available phone number found, either for the
        customer, or its first person.
        """
        phone = self.get_first_phone(customer)
        if phone:
            return phone.number

    def get_first_email(self, customer, invalid=False, **kwargs):
        """
        Return the first available email record found, either for the
        customer, or its first person.
        """
        email = customer.first_email(invalid=invalid)
        if email:
            return email

        person = self.app.get_person(customer)
        if person:
            return person.first_email(invalid=invalid)

    def get_first_email_address(self, customer, invalid=False, **kwargs):
        """
        Return the first available email address found, either for the
        customer, or its first person.
        """
        email = self.get_first_email(customer, invalid=invalid)
        if email:
            return email.address


def get_clientele_handler(config, **kwargs):
    """
    Create and return the configured :class:`ClienteleHandler` instance.
    """
    app = config.get_app()
    spec = config.get('rattail', 'clientele.handler')
    if spec:
        factory = app.load_object(spec)
    else:
        factory = ClienteleHandler
    return factory(config, **kwargs)
