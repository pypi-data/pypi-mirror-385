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
Rattail -> Rattail data import
"""

import logging
from collections import OrderedDict

import sqlalchemy as sa

from rattail.importing import model
from rattail.importing.handlers import FromSQLAlchemyHandler, ToSQLAlchemyHandler
from rattail.importing.sqlalchemy import FromSQLAlchemySameToSame


log = logging.getLogger(__name__)


class FromRattailHandler(FromSQLAlchemyHandler):
    """
    Base class for import handlers which target a Rattail database on the local side.
    """
    host_key = 'rattail'
    generic_host_title = "Rattail"

    @property
    def host_title(self):
        return self.app.get_title()

    def make_host_session(self):
        return self.app.make_session()


class ToRattailHandler(ToSQLAlchemyHandler):
    """
    Base class for import handlers which target a Rattail database on the local side.
    """
    generic_local_title = "Rattail"
    local_key = 'rattail'

    @property
    def local_title(self):
        return self.app.get_title()

    def make_session(self):
        kwargs = {}
        if hasattr(self, 'runas_user'):
            kwargs['continuum_user'] = self.runas_user
        return self.app.make_session(**kwargs)

    def begin_local_transaction(self):
        self.session = self.make_session()

        # load "runas user" into current session
        if hasattr(self, 'runas_user') and self.runas_user:
            dbmodel = self.app.model
            runas_user = self.session.get(dbmodel.User, self.runas_user.uuid)
            if not runas_user:
                log.info("runas_user does not exist in target session: %s",
                         self.runas_user.username)
            # this may be None if user does not exist in target session
            self.runas_user = runas_user

        # declare "runas user" is data versioning author
        if hasattr(self, 'runas_username') and self.runas_username:
            self.session.set_continuum_user(self.runas_username)


class FromRattailToRattailBase(object):
    """
    Common base class for Rattail -> Rattail data import/export handlers.
    """

    def get_importers(self):
        importers = OrderedDict()
        importers['Person'] = PersonImporter
        importers['GlobalPerson'] = GlobalPersonImporter
        importers['PersonEmailAddress'] = PersonEmailAddressImporter
        importers['PersonPhoneNumber'] = PersonPhoneNumberImporter
        importers['PersonMailingAddress'] = PersonMailingAddressImporter
        importers['MergePeopleRequest'] = MergePeopleRequestImporter
        importers['Role'] = RoleImporter
        importers['GlobalRole'] = GlobalRoleImporter
        importers['User'] = UserImporter
        importers['AdminUser'] = AdminUserImporter
        importers['GlobalUser'] = GlobalUserImporter
        importers['Message'] = MessageImporter
        importers['MessageRecipient'] = MessageRecipientImporter
        importers['Store'] = StoreImporter
        importers['StorePhoneNumber'] = StorePhoneNumberImporter
        importers['Employee'] = EmployeeImporter
        importers['EmployeeStore'] = EmployeeStoreImporter
        importers['EmployeeEmailAddress'] = EmployeeEmailAddressImporter
        importers['EmployeePhoneNumber'] = EmployeePhoneNumberImporter
        importers['ScheduledShift'] = ScheduledShiftImporter
        importers['WorkedShift'] = WorkedShiftImporter
        importers['Customer'] = CustomerImporter
        importers['CustomerGroup'] = CustomerGroupImporter
        importers['CustomerGroupAssignment'] = CustomerGroupAssignmentImporter
        importers['CustomerShopper'] = CustomerShopperImporter
        importers['CustomerShopperHistory'] = CustomerShopperHistoryImporter
        importers['CustomerPerson'] = CustomerPersonImporter
        importers['CustomerEmailAddress'] = CustomerEmailAddressImporter
        importers['CustomerPhoneNumber'] = CustomerPhoneNumberImporter
        importers['Member'] = MemberImporter
        importers['MemberEmailAddress'] = MemberEmailAddressImporter
        importers['MemberPhoneNumber'] = MemberPhoneNumberImporter
        importers['MemberEquityPayment'] = MemberEquityPaymentImporter
        importers['Tender'] = TenderImporter
        importers['Vendor'] = VendorImporter
        importers['VendorEmailAddress'] = VendorEmailAddressImporter
        importers['VendorPhoneNumber'] = VendorPhoneNumberImporter
        importers['VendorContact'] = VendorContactImporter
        importers['VendorSampleFile'] = VendorSampleFileImporter
        importers['Department'] = DepartmentImporter
        importers['EmployeeDepartment'] = EmployeeDepartmentImporter
        importers['Subdepartment'] = SubdepartmentImporter
        importers['Category'] = CategoryImporter
        importers['Family'] = FamilyImporter
        importers['ReportCode'] = ReportCodeImporter
        importers['DepositLink'] = DepositLinkImporter
        importers['Tax'] = TaxImporter
        importers['InventoryAdjustmentReason'] = InventoryAdjustmentReasonImporter
        importers['Brand'] = BrandImporter
        importers['Product'] = ProductImporter
        importers['ProductCode'] = ProductCodeImporter
        importers['ProductCost'] = ProductCostImporter
        importers['ProductPrice'] = ProductPriceImporter
        importers['ProductPriceAssociation'] = ProductPriceAssociationImporter
        importers['ProductStoreInfo'] = ProductStoreInfoImporter
        importers['ProductVolatile'] = ProductVolatileImporter
        importers['ProductImage'] = ProductImageImporter
        importers['LabelProfile'] = LabelProfileImporter
        return importers

    def get_default_keys(self):
        keys = self.get_importer_keys()

        avoid_by_default = [
            'Role',
            'GlobalRole',
            'GlobalPerson',
            'AdminUser',
            'GlobalUser',
            'ProductImage',
            'ProductPriceAssociation',
        ]

        for key in avoid_by_default:
            if key in keys:
                keys.remove(key)

        return keys


class FromRattailToRattailImport(FromRattailToRattailBase, FromRattailHandler, ToRattailHandler):
    """
    Handler for Rattail (other) -> Rattail (local) data import.

    .. attribute:: direction

       Value is ``'import'`` - see also
       :attr:`rattail.importing.handlers.ImportHandler.direction`.
    """
    dbkey = 'other'

    @property
    def host_title(self):
        app_title = self.app.get_title()
        return f"{app_title} ({self.dbkey})"

    @property
    def local_title(self):
        app_title = self.app.get_title()
        node_title = self.app.get_node_title()
        if node_title != app_title:
            return node_title
        return f"{app_title} (local)"

    def make_host_session(self):
        return self.app.make_session(bind=self.config.appdb_engines[self.dbkey])


class FromRattailToRattailExport(FromRattailToRattailBase, FromRattailHandler, ToRattailHandler):
    """
    Handler for Rattail (local) -> Rattail (other) data export.

    .. attribute:: direction

       Value is ``'export'`` - see also
       :attr:`rattail.importing.handlers.ImportHandler.direction`.
    """
    direction = 'export'
    dbkey = 'other'

    @property
    def host_title(self):
        return self.app.get_node_title()

    @property
    def local_title(self):
        app_title = self.app.get_title()
        return f"{app_title} ({self.dbkey})"

    def make_session(self):
        return self.app.make_session(bind=self.config.appdb_engines[self.dbkey])


class FromRattail(FromSQLAlchemySameToSame):
    """
    Base class for Rattail -> Rattail data importers.
    """


class PersonImporter(FromRattail, model.PersonImporter):
    pass


class GlobalPersonImporter(FromRattail, model.GlobalPersonImporter):
    """
    This is a customized version of the :class:`PersonImporter`, which simply
    avoids "local only" person accounts.
    """

    def query(self):
        query = super().query()

        # never include "local only" people
        query = query.filter(sa.or_(
            self.host_model_class.local_only == False,
            self.host_model_class.local_only == None))

        return query

    def normalize_host_object(self, person):

        # must check this here for sake of datasync
        if person.local_only:
            return

        data = super().normalize_host_object(person)
        return data


class PersonEmailAddressImporter(FromRattail, model.PersonEmailAddressImporter):
    pass

class PersonPhoneNumberImporter(FromRattail, model.PersonPhoneNumberImporter):
    pass

class PersonMailingAddressImporter(FromRattail, model.PersonMailingAddressImporter):
    pass

class MergePeopleRequestImporter(FromRattail, model.MergePeopleRequestImporter):
    pass

class RoleImporter(FromRattail, model.RoleImporter):
    pass


class GlobalRoleImporter(RoleImporter):
    """
    Role importer which only will handle roles which have the
    :attr:`~rattail.db.model.users.Role.sync_me` flag set.  (So it
    syncs those roles but avoids others.)
    """

    @property
    def supported_fields(self):
        fields = list(super().supported_fields)
        fields.extend([
            'permissions',
            'users',
        ])
        return fields

    # nb. we must override both cache_query() and query() b/c they use
    # different sessions!

    def cache_query(self):
        """
        Return the query to be used when caching "local" data.
        """
        query = super().cache_query()
        model = self.model

        # only want roles which are *meant* to be synced
        query = query.filter(model.Role.sync_me == True)

        return query

    def query(self):
        query = super().query()
        model = self.model

        # only want roles which are *meant* to be synced
        query = query.filter(model.Role.sync_me == True)

        return query

    # nb. we do not need to override normalize_host_object() b/c it
    # just calls normalize_local_object() by default

    def normalize_local_object(self, role):

        # only want roles which are *meant* to be synced
        if not role.sync_me:
            return

        data = super().normalize_local_object(role)
        if data:

            # users
            if 'users' in self.fields:
                data['users'] = sorted([user.uuid for user in role.users])

            # permissions
            if 'permissions' in self.fields:
                auth = self.app.get_auth_handler()
                perms = auth.cache_permissions(self.session, role,
                                               include_guest=False)
                data['permissions'] = sorted(perms)

            return data

    def update_object(self, role, host_data, local_data=None, **kwargs):
        role = super().update_object(role, host_data, local_data=local_data, **kwargs)
        model = self.model

        # users
        # nb. we only update users if this role has flag set
        if 'users' in self.fields and role.sync_users:

            new_users = host_data['users']
            old_users = local_data['users'] if local_data else []
            changed = False

            # add some users
            for new_user in new_users:
                if new_user not in old_users:
                    user = self.session.get(model.User, new_user)
                    if user:
                        user.roles.append(role)
                        changed = True

            # remove some users
            for old_user in old_users:
                if old_user not in new_users:
                    user = self.session.get(model.User, old_user)
                    if user:
                        user.roles.remove(role)
                        changed = True

            if changed:
                self.session.flush()
                self.session.refresh(role)
                # also record a change to the role, for datasync.
                # this is done "just in case" the role is to be
                # synced to all nodes
                if self.session.rattail_record_changes:
                    self.session.add(model.Change(class_name='Role',
                                                  instance_uuid=role.uuid,
                                                  deleted=False))

        # permissions
        if 'permissions' in self.fields:
            auth = self.app.get_auth_handler()
            new_perms = host_data['permissions']
            old_perms = local_data['permissions'] if local_data else []

            # grant permissions
            for new_perm in new_perms:
                if new_perm not in old_perms:
                    auth.grant_permission(role, new_perm)

            # revoke permissions
            for old_perm in old_perms:
                if old_perm not in new_perms:
                    auth.revoke_permission(role, old_perm)

        return role


class UserImporter(FromRattail, model.UserImporter):
    pass


class GlobalUserImporter(FromRattail, model.GlobalUserImporter):
    """
    This is a customized version of the :class:`UserImporter`, which simply
    avoids "local only" user accounts.
    """

    def query(self):
        query = super().query()

        # never include "local only" users
        query = query.filter(sa.or_(
            self.host_model_class.local_only == False,
            self.host_model_class.local_only == None))

        return query

    def normalize_host_object(self, user):

        # must check this here for sake of datasync
        if user.local_only:
            return

        data = super().normalize_host_object(user)
        return data


class AdminUserImporter(FromRattail, model.AdminUserImporter):

    @property
    def supported_fields(self):
        return super().supported_fields + [
            'admin',
        ]

    def normalize_host_object(self, user):
        data = super().normalize_local_object(user) # sic
        if 'admin' in self.fields: # TODO: do we really need this, after the above?
            data['admin'] = self.admin_uuid in [r.role_uuid for r in user._roles]
        return data


class MessageImporter(FromRattail, model.MessageImporter):
    pass

class MessageRecipientImporter(FromRattail, model.MessageRecipientImporter):
    pass

class StoreImporter(FromRattail, model.StoreImporter):
    pass

class StorePhoneNumberImporter(FromRattail, model.StorePhoneNumberImporter):
    pass

class EmployeeImporter(FromRattail, model.EmployeeImporter):
    pass

class EmployeeStoreImporter(FromRattail, model.EmployeeStoreImporter):
    pass

class EmployeeDepartmentImporter(FromRattail, model.EmployeeDepartmentImporter):
    pass

class EmployeeEmailAddressImporter(FromRattail, model.EmployeeEmailAddressImporter):
    pass

class EmployeePhoneNumberImporter(FromRattail, model.EmployeePhoneNumberImporter):
    pass

class ScheduledShiftImporter(FromRattail, model.ScheduledShiftImporter):
    pass

class WorkedShiftImporter(FromRattail, model.WorkedShiftImporter):
    pass

class CustomerImporter(FromRattail, model.CustomerImporter):
    pass

class CustomerGroupImporter(FromRattail, model.CustomerGroupImporter):
    pass

class CustomerGroupAssignmentImporter(FromRattail, model.CustomerGroupAssignmentImporter):
    pass

class CustomerShopperImporter(FromRattail, model.CustomerShopperImporter):
    pass

class CustomerShopperHistoryImporter(FromRattail, model.CustomerShopperHistoryImporter):
    pass

class CustomerPersonImporter(FromRattail, model.CustomerPersonImporter):
    pass

class CustomerEmailAddressImporter(FromRattail, model.CustomerEmailAddressImporter):
    pass

class CustomerPhoneNumberImporter(FromRattail, model.CustomerPhoneNumberImporter):
    pass

class MemberImporter(FromRattail, model.MemberImporter):
    pass

class MemberEmailAddressImporter(FromRattail, model.MemberEmailAddressImporter):
    pass

class MemberPhoneNumberImporter(FromRattail, model.MemberPhoneNumberImporter):
    pass

class MemberEquityPaymentImporter(FromRattail, model.MemberEquityPaymentImporter):
    pass

class TenderImporter(FromRattail, model.TenderImporter):
    pass

class VendorImporter(FromRattail, model.VendorImporter):
    pass

class VendorEmailAddressImporter(FromRattail, model.VendorEmailAddressImporter):
    pass

class VendorPhoneNumberImporter(FromRattail, model.VendorPhoneNumberImporter):
    pass

class VendorContactImporter(FromRattail, model.VendorContactImporter):
    pass

class VendorSampleFileImporter(FromRattail, model.VendorSampleFileImporter):
    pass

class DepartmentImporter(FromRattail, model.DepartmentImporter):
    pass

class SubdepartmentImporter(FromRattail, model.SubdepartmentImporter):
    pass

class CategoryImporter(FromRattail, model.CategoryImporter):
    pass

class FamilyImporter(FromRattail, model.FamilyImporter):
    pass

class ReportCodeImporter(FromRattail, model.ReportCodeImporter):
    pass

class DepositLinkImporter(FromRattail, model.DepositLinkImporter):
    pass

class TaxImporter(FromRattail, model.TaxImporter):
    pass

class InventoryAdjustmentReasonImporter(FromRattail, model.InventoryAdjustmentReasonImporter):
    pass

class BrandImporter(FromRattail, model.BrandImporter):
    pass


class ProductWithPriceImporter(FromRattail, model.ProductImporter):
    """
    This can perhaps be thought of as the "complete" Product record
    importer.  The "normal" Product importer will typically avoid the
    "price uuid" reference fields, b/c of that foreign key chaos.

    Note that this importer is not (yet?) used directly, but is
    primarily useful as a base class.
    """
    # these require special handling due to the 2-way table dependency
    price_reference_fields = [
        'regular_price_uuid',
        'tpr_price_uuid',
        'sale_price_uuid',
        'current_price_uuid',
        'suggested_price_uuid',
    ]

    def query(self):
        query = super().query()

        # make sure potential unit items (i.e. rows with NULL unit_uuid) come
        # first, so they will be created before pack items reference them
        # cf. https://www.postgresql.org/docs/current/static/queries-order.html
        # cf. https://stackoverflow.com/a/7622046
        query = query.order_by(self.host_model_class.unit_uuid.desc())

        return query


class ProductPriceAssociationImporter(ProductWithPriceImporter):
    """
    Note that this importer is *only* for sake of handling the "price
    uuid" fields.
    """

    @property
    def simple_fields(self):
        return ['uuid'] + self.price_reference_fields


class ProductImporter(ProductWithPriceImporter):
    """
    Note that this is the "normal" Product record importer, but it
    inherits from the "complete" importer.  This one avoids the "price
    uuid" fields to avoid that foreign key chaos.
    """

    @property
    def simple_fields(self):
        fields = super().simple_fields
        # NOTE: it seems we can't consider these "simple" due to the
        # self-referencing foreign key situation.  an importer can still
        # "support" these fields, but they're excluded from the simple set for
        # sake of rattail <-> rattail
        for field in self.price_reference_fields:
            fields.remove(field)
        return fields


class ProductCodeImporter(FromRattail, model.ProductCodeImporter):
    pass

class ProductCostImporter(FromRattail, model.ProductCostImporter):
    pass

class ProductPriceImporter(FromRattail, model.ProductPriceImporter):

    @property
    def supported_fields(self):
        # nb. parent class FromRattail only supports simple_fields, so
        # we explicitly copy logic from model importer class here.
        return self.simple_fields + self.product_reference_fields


class ProductStoreInfoImporter(FromRattail, model.ProductStoreInfoImporter):
    pass

class ProductVolatileImporter(FromRattail, model.ProductVolatileImporter):
    pass


class ProductImageImporter(FromRattail, model.ProductImageImporter):
    """
    Importer for product images.  Note that this uses the "batch" approach
    because fetching all data up front is not performant when the host/local
    systems are on different machines etc.
    """

    def query(self):
        query = self.host_session.query(self.model_class)\
                                 .order_by(self.model_class.uuid)
        return query[self.host_index:self.host_index + self.batch_size]


class LabelProfileImporter(FromRattail, model.LabelProfileImporter):

    def query(self):
        query = super().query()

        if not self.config.getbool('rattail', 'labels.sync_all_profiles', default=False):
            # only fetch labels from host which are marked as "sync me"
            query = query .filter(self.model_class.sync_me == True)

        return query.order_by(self.model_class.ordinal)
