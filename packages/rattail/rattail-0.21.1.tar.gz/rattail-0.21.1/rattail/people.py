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
People Handler

See also :doc:`rattail-manual:base/handlers/other/people`.
"""

import warnings

from wuttjamaican import people as base

from rattail.app import MergeMixin


class PeopleHandler(base.PeopleHandler, MergeMixin):
    """
    Base class and default implementation for people handlers.
    """

    def get_person(self, obj, **kwargs):
        """
        Retrieve the Person related to the given object.

        This is a rather fundamental method, in that it is called by
        several other methods, both within this handler as well as
        others.  There is even a shortcut to it, accessible via
        :meth:`rattail.app.AppHandler.get_person()`.

        Its purpose is to navigate relationships as needed, to get at
        the "default" person associated with the object.  Depending on
        how the app tracks relationships, this logic may need to vary.
        """
        model = self.app.model

        if isinstance(obj, model.Person):
            return obj

        elif isinstance(obj, model.User):
            if obj.person:
                return obj.person

        elif isinstance(obj, model.Employee):
            return obj.person

        elif isinstance(obj, model.Customer):
            if obj.account_holder:
                return obj.account_holder
            if obj.shoppers:
                return obj.shoppers[0].person
            # legacy fallback
            if obj.people:
                return obj.people[0]

        elif isinstance(obj, model.Member):
            if obj.person:
                return obj.person

    def should_expose_quickie_search(self):
        return self.config.getbool('rattail',
                                   'people.expose_quickie_search',
                                   default=False)

    def should_use_preferred_first_name(self):
        return self.config.getbool('rattail',
                                   'people.use_preferred_first_name',
                                   default=False)

    def get_quickie_search_placeholder(self):
        return self.app.get_customer_key_label()

    def quickie_lookup(self, entry, session):
        """
        Attempt to locate a person based on the given entry.  By
        default this will do a lookup based on the configured Customer
        key field.  Override as needed.
        """
        from sqlalchemy import orm

        model = self.app.model
        field = self.app.get_customer_key_field()

        # validate/coerce data type
        # TOOD: this is a hack! should inspect field type etc.
        if field == 'number':
            if not entry.isdigit():
                return
            entry = int(entry)

        try:
            customer = session.query(model.Customer)\
                              .filter(getattr(model.Customer, field) == entry)\
                              .one()
        except orm.exc.NoResultFound:
            pass
        else:
            return self.app.get_person(customer)

    def normalize_full_name(self, first, last, **kwargs):
        """
        Normalize a "full" name based on the given first and last
        names.  Tries to be smart about collapsing whitespace etc.

        :param first: First name.
        :param last: Last name.
        :returns: First and last name combined.
        """
        from rattail.db.util import normalize_full_name
        return normalize_full_name(first, last)

    def make_person(self, **kwargs):
        """
        Make and return a new Person instance.
        """
        model = self.app.model
        person = model.Person()

        if 'first_name' in kwargs:
            person.first_name = kwargs.pop('first_name')
        if self.should_use_preferred_first_name():
            if 'preferred_first_name' in kwargs:
                person.preferred_first_name = kwargs.pop('preferred_first_name')
        if 'middle_name' in kwargs:
            person.middle_name = kwargs.pop('middle_name')
        if 'last_name' in kwargs:
            person.last_name = kwargs.pop('last_name')

        if 'display_name' in kwargs:
            person.display_name = kwargs.pop('display_name')
        else:
            person.display_name = self.normalize_full_name(
                person.first_name, person.last_name)

        for key, value in kwargs.items():
            if hasattr(person, key):
                setattr(person, key, value)

        return person

    def update_names(self, person, **kwargs):
        """
        Update name(s) for the given person.

        :param person: Reference to a ``Person`` record.
        :param first: First name for the person.
        :param preferred_first: Preferred first name for the person.
        :param middle: Middle name for the person.
        :param last: Last name for the person.
        :param full: Full (display) name for the person.
        """
        if 'first' in kwargs:
            person.first_name = kwargs['first']

        if self.should_use_preferred_first_name():
            if 'preferred_first' in kwargs:
                person.preferred_first_name = kwargs['preferred_first']

        if 'middle' in kwargs:
            person.middle_name = kwargs['middle']

        if 'last' in kwargs:
            person.last_name = kwargs['last']

        if 'full' in kwargs:
            if kwargs['full']:
                person.display_name = kwargs['full']
            else:
                person.display_name = self.normalize_full_name(
                    person.first_name, person.last_name)
        elif 'first' in kwargs and 'last' in kwargs:
            person.display_name = self.normalize_full_name(
                person.first_name, person.last_name)

    def add_phone(self, person, number, type='Home', preferred=False, **kwargs):
        """
        Add a phone record for the person.

        :param person: Reference to a ``Person`` record.
        :param number: Actual phone number to add.
        :param type: Type of phone number to add.
        :param preferred: Boolean indicating that this should be the
           new "preferred" number for the person.
        """
        reason = self.app.phone_number_is_invalid(number)
        if reason:
            raise ValueError("Phone number is not valid: {}".format(reason))

        phone = person.add_phone(number=self.app.format_phone_number(number),
                                 type=type)
        if preferred:
            person.set_primary_phone(phone)

        return phone

    def update_phone(self, person, phone, **kwargs):
        """
        Update a phone record for the person.

        :param person: Reference to a ``Person`` record.
        :param phone: Reference to the ``PersonPhoneNumber`` record to update.
        :param number: Actual phone number.
        :param type: Type of phone number.
        :param preferred: Boolean indicating that this should be the
           new "preferred" number for the person.
        """
        if phone not in person.phones:
            raise ValueError("Phone does not belong to this person.")

        if 'number' in kwargs:
            reason = self.app.phone_number_is_invalid(kwargs['number'])
            if reason:
                raise ValueError("Phone number is not valid: {}".format(reason))
            phone.number = self.app.format_phone_number(kwargs['number'])

        if 'type' in kwargs:
            phone.type = kwargs['type']

        if 'preferred' in kwargs:
            if kwargs['preferred']:
                person.set_primary_phone(phone)
            else: # should *not* prefer this one
                if phone.preferred and len(person.phones) > 1:
                    # make 2nd phone the new 1st
                    person.set_primary_phone(person.phones[1])

        return phone

    def add_email(self, person, address, type='Home',
                  invalid=False, preferred=False, **kwargs):
        """
        Add a email record for the person.

        :param person: Reference to a ``Person`` record.
        :param address: Actual email address to add.
        :param type: Type of email address to add.
        :param invalid: Boolean indicating the address is known to
           *not* be valid.
        :param preferred: Boolean indicating that this should (or not)
           be the "preferred" email address for the person.
        """
        email = person.add_email(address=address,
                                 type=type,
                                 invalid=invalid)
        if preferred:
            person.set_primary_email(email)

        return email

    def update_email(self, person, email, **kwargs):
        """
        Update a email record for the person.

        :param person: Reference to a ``Person`` record.
        :param email: Reference to the ``PersonEmailAddress`` record to update.
        :param address: Actual email address.
        :param type: Type of email address.
        :param invalid: Boolean indicating the address is known to
           *not* be valid.
        :param preferred: Boolean indicating that this should (or not)
           be the "preferred" address for the person.
        """
        if email not in person.emails:
            raise ValueError("Email does not belong to this person.")

        address_changed = False
        if 'address' in kwargs:
            address = kwargs['address']
            if self.should_force_email_to_lower_case():
                address = address.lower()
            if email.address != address:
                email.address = address
                address_changed = True

        if 'type' in kwargs:
            email.type = kwargs['type']

        if address_changed:
            if email.invalid:
                email.invalid = False
        elif 'invalid' in kwargs:
            email.invalid = kwargs['invalid']

        if 'preferred' in kwargs:
            if kwargs['preferred']:
                person.set_primary_email(email)
            else: # should *not* prefer this one
                if email.preferred and len(person.emails) > 1:
                    # make 2nd email the new 1st
                    person.set_primary_email(person.emails[1])

        return email

    def should_force_email_to_lower_case(self):
        return self.config.getbool('rattail',
                                   'people.should_force_email_to_lower_case',
                                   default=False)

    def add_address(self, person, type=None,
                    street=None, street2=None,
                    city=None, state=None, zipcode=None,
                    invalid=False, preferred=False, **kwargs):
        """
        Add a physical/mailing address record for the person.

        :param person: Reference to a ``Person`` record.
        :param type: Type of address to add.
        :param street: Street (line 1) for the address.
        :param street2: Street (line 2) for the address.
        :param city: City for the address.
        :param state: State for the address.
        :param zipcode: Zipcode for the address.
        :param invalid: Boolean indicating the address is known to
           *not* be valid.
        :param preferred: Boolean indicating that this should (or not)
           be the "preferred" address for the person.
        """
        address = person.add_address(type=type,
                                     street=street,
                                     street2=street2,
                                     city=city,
                                     state=state,
                                     zipcode=zipcode,
                                     invalid=invalid,
                                     flush=False)
        if preferred:
            person.set_primary_address(address)

        return address

    def ensure_address(self, person, **kwargs):
        """
        Returns the default address record associated with the given
        person, creating it first if necessary.
        """
        address = person.first_address()
        if not address:
            address = self.add_address(person, **kwargs)
        return address

    def update_address(self, person, address, **kwargs):
        """
        Update the given address with the given data.
        """
        if 'type' in kwargs:
            address.type = kwargs['type']

        if 'street' in kwargs:
            address.street = kwargs['street']

        if 'street2' in kwargs:
            address.street2 = kwargs['street2']

        if 'city' in kwargs:
            address.city = kwargs['city']

        if 'state' in kwargs:
            address.state = kwargs['state']

        if 'zipcode' in kwargs:
            address.zipcode = kwargs['zipcode']

        if 'invalid' in kwargs:
            self.mark_address_invalid(person, address, kwargs['invalid'])

    def address_is_invalid(self, person, address, **kwargs):
        """
        Returns a boolean indicating if the given person's address is
        invalid.

        :param person: Reference to a person.
        :param address: Reference to a person's address.
        """
        return address.invalid

    def mark_address_invalid(self, person, address, invalid, **kwargs):
        """
        Mark the person's address as invalid.

        :param person: Reference to a person.
        :param address: Reference to a person's address.
        :param invalid: Boolean indicating "invalid" status for
           person's address.
        """
        address.invalid = invalid

    def resolve_person(self, pending, person, user, **kwargs):
        """
        Resolve a pending person.

        :param pending: Reference to a PendingCustomer instance.

        :param person: Reference to a Person instance.

        :param user: Reference to the User responsible.
        """
        custorder_handler = self.app.get_custorder_handler()
        custorder_handler.resolve_person(pending, person, user)

        pending.status_code = self.enum.PENDING_CUSTOMER_STATUS_RESOLVED

    def request_merge(self, user, removing_uuid, keeping_uuid, **kwargs):
        """
        Submit an officical merge request for two Person records.

        The caller must obviously specify which is to be kept and
        which removed, but really this is arbitrary, as the user
        performing the merge is free to swap them around.
        """
        model = self.app.model
        session = self.app.get_session(user)
        merge = model.MergePeopleRequest()
        merge.removing_uuid = removing_uuid
        merge.keeping_uuid = keeping_uuid
        merge.requested_by = user
        merge.requested = self.app.make_utc()
        session.add(merge)
        session.flush()
        self.notify_of_merge_request(merge)
        return merge

    def notify_of_merge_request(self, merge):
        """
        Send an email alert regarding a new merge request.
        """
        session = self.app.get_session(merge)
        model = self.app.model

        removing = session.get(model.Person, merge.removing_uuid)
        keeping = session.get(model.Person, merge.keeping_uuid)

        context = {
            'user_display': merge.requested_by.display_name,
            'removing_display': str(removing) if removing else "(not found)",
            'keeping_display': str(keeping) if keeping else "(not found)",
        }

        url = self.config.base_url()
        if url:
            context['merge_request_url'] = '{}/people/merge-requests/{}'.format(url, merge.uuid)
            if removing:
                context['removing_url'] = '{}/people/{}/profile'.format(url, removing.uuid)
            if keeping:
                context['keeping_url'] = '{}/people/{}/profile'.format(url, keeping.uuid)

        self.app.send_email('person_merge_request', context)

    def get_merge_preview_fields(self, **kwargs):
        """
        Returns a sequence of fields which will be used during a merge
        preview.
        """
        F = self.make_merge_field
        return [
            F('uuid'),
            F('first_name'),
            F('last_name'),
            F('display_name'),
            F('usernames', additive=True),
            F('employee_uuid', coalesce=True),
            F('customer_account_uuids', additive=True),
            F('shopper_uuids', additive=True),
            F('member_uuids', additive=True),
        ]

    def get_merge_preview_data(self, person, **kwargs):
        """
        Must return a data dictionary for the given person, which can
        be presented to the user during a merge preview.
        """
        return {
            'uuid': person.uuid,
            'first_name': person.first_name,
            'last_name': person.last_name,
            'display_name': person.display_name,
            'usernames': [u.username for u in person.users],
            'employee_uuid': person.employee.uuid if person.employee else None,
            'member_uuids': [m.uuid for m in person.members],
            'customer_account_uuids': [c.uuid for c in person.customer_accounts],
            'shopper_uuids': [s.uuid for s in person.customer_shoppers],
        }

    def why_not_merge(self, removing, keeping, **kwargs):
        """
        Evaluate the given merge candidates and if there is a reason *not*
        to merge them, return that reason.

        :param removing: Person record which will be removed, should the
           merge happen.
        :param keeping: Person record which will be kept, should the
           merge happen.
        :returns: String indicating reason not to merge, or ``None``.
        """
        if removing.employee and keeping.employee:
            if removing.employee is not keeping.employee:
                return "Cannot merge 2 people who are distinct employees"

    def perform_merge(self, removing, keeping, **kwargs):

        # merge per usual
        super().perform_merge(removing, keeping, **kwargs)

        # if there were pending requests for this merge, declare them satisfied
        self.satisfy_merge_requests(removing, keeping, user=kwargs.get('user'))

    def merge_update_keeping_object(self, removing, keeping):

        # update per usual
        super().merge_update_keeping_object(removing, keeping)

        # move CustomerShopper records to final Person
        for shopper in list(removing.customer_shoppers):
            shopper.person = keeping

        # move Customer records to final Person
        for customer in list(removing.customer_accounts):
            removing.customer_accounts.remove(customer)
            keeping.customer_accounts.append(customer)

        # move Member records to final Person
        for member in list(removing.members):
            removing.members.remove(member)
            keeping.members.append(member)

        # move Employee record to final Person
        if removing.employee:
            if keeping.employee and keeping.employee is not removing.employee:
                raise RuntimeError("Cannot merge 2 people who are distinct employees")
            if not keeping.employee:
                employee = removing.employee
                employee.person = keeping

        # move User records to final Person
        for user in list(removing.users):
            removing.users.remove(user)
            keeping.users.append(user)

    def satisfy_merge_requests(self, removing, keeping, user):
        """
        If there was a merge request(s) for this pair, mark it complete.
        """
        import sqlalchemy as sa

        session = self.app.get_session(keeping)
        model = self.app.model
        merge_requests = session.query(model.MergePeopleRequest)\
                                .filter(sa.or_(
                                    sa.and_(
                                        model.MergePeopleRequest.removing_uuid == removing.uuid,
                                        model.MergePeopleRequest.keeping_uuid == keeping.uuid),
                                    sa.and_(
                                        model.MergePeopleRequest.removing_uuid == keeping.uuid,
                                        model.MergePeopleRequest.keeping_uuid == removing.uuid)))\
                                .all()
        for merge_request in merge_requests:
            # set the record straight re: removing vs. keeping
            merge_request.removing_uuid = removing.uuid
            merge_request.keeping_uuid = keeping.uuid
            merge_request.merged = self.app.make_utc()
            merge_request.merged_by = user

def get_people_handler(config, **kwargs):
    """
    Create and return the configured :class:`PeopleHandler` instance.

    .. warning::
       This function is deprecated; please use
       :meth:`~rattail.app.AppHandler.get_people_handler` instead.
    """
    warnings.warn("get_people_handler() function is deprecated, "
                  "please use app.get_people_handler() method instead",
                  DeprecationWarning, stacklevel=2)
    app = config.get_app()
    return app.get_people_handler(**kwargs)
