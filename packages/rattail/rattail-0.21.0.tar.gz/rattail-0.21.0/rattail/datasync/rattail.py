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
DataSync for Rattail
"""

import logging

from rattail.db.util import make_topo_sortkey
from rattail.datasync import DataSyncWatcher, DataSyncConsumer, DataSyncImportConsumer


log = logging.getLogger(__name__)


class RattailWatcher(DataSyncWatcher):
    """
    DataSync watcher for Rattail databases.
    """
    prunes_changes = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.engine = self.config.appdb_engines[self.dbkey]
        self.topo_sortkey = make_topo_sortkey(self.app.model)

    def get_changes(self, lastrun):
        """
        Checks the :class:`~rattail.db.model.core.Change` table in a
        Rattail database, to see if there are any pending changes for
        the datasync daemon.
        """
        model = self.model
        session = self.app.make_session(bind=self.engine)
        changes = session.query(model.Change).all()
        session.expunge_all()
        # nb. fetch config flag while we have session open
        deleted_first = self.config.getbool(
            'rattail.datasync', 'rattail_watcher_deleted_first',
            session=session,
            default=False)
        session.close()
        if not changes:
            return

        # here we sort our payload types (class names) topologically, to take
        # foreign key dependencies into account etc.  but we start with a
        # simple lexical sort on class name, just for kicks maybe..?
        class_names = sorted(set([c.class_name for c in changes]))
        class_names.sort(key=self.topo_sortkey)

        # collect datasync changes for new/dirty and deleted
        dirty = self.get_new_dirty(changes, class_names)
        deleted = self.get_deleted(changes, class_names)

        # we traditionally have processed new/dirty first, then
        # deleted.  but config can reverse that, to test new logic
        # which is meant to help with one particular scenario: when a
        # record with "unique code" is effectively moved; the new
        # record can't be created until the old is deleted
        # TODO: once "deleted first" has been tested, should make it
        # the default, unless there is some reason not to...
        # TODO: original logic comments said: note that we must first
        # add new/dirty changes only, then we add deleted at the end.
        # so that deletes are processed last, by the consumer(s), to
        # hopefully avoid dependency issues
        if deleted_first:
            final = deleted + dirty
        else:
            final = dirty + deleted

        # when a Product has a price relationship change (e.g. it is
        # given or loses the "current price"), the Product record is
        # the only thing technically updated, but the simple Rattail
        # -> Rattail sync will use an importer which *skips* those
        # price relation fields.  so here we explicitly add changes to
        # the queue, which can force processing of the price relation
        # changes.  and we definitely want these to happen *last*.
        if 'Product' in class_names:
            for change in [c for c in changes
                           if c.class_name == 'Product' and not c.deleted]:
                final.append((None, # no uuid since this need not be pruned
                              model.DataSyncChange(
                                  payload_type='ProductPriceAssociation',
                                  payload_key=change.instance_uuid)))

        return final

    def get_new_dirty(self, changes, class_names):
        model = self.model
        result = []
        for class_name in class_names:
            for change in [c for c in changes
                           if c.class_name == class_name
                           and not c.deleted]:
                result.append((change.uuid,
                               model.DataSyncChange(
                                   payload_type=class_name,
                                   payload_key=change.instance_uuid,
                                   deletion=change.deleted)))
        return result

    def get_deleted(self, changes, class_names):
        model = self.model
        result = []
        for class_name in class_names:
            for change in [c for c in changes
                           if c.class_name == class_name
                           and c.deleted]:
                result.append((change.uuid,
                               model.DataSyncChange(
                                   payload_type=class_name,
                                   payload_key=change.instance_uuid,
                                   deletion=change.deleted)))
        return result

    def prune_changes(self, keys):
        model = self.model
        deleted = 0
        try:
            session = self.app.make_session(bind=self.engine)
        except:
            log.exception("failed to make session for pruning changes")
            raise
        try:
            for key in keys:
                if key: # note that key can sometimes be None
                    change = session.get(model.Change, key)
                    if change:
                        session.delete(change)
                        session.flush()
                        deleted += 1
        except:
            log.exception("failed to prune changes")
            session.rollback()
            raise
        else:
            session.commit()
        finally:
            session.close()
        return deleted


# TODO: this is awful and needs to go away!
class RattailConsumer(DataSyncConsumer):
    """
    DataSync consumer for Rattail databases.
    """
    # Set this to a sequence of model names if you wish to *consume* data
    # *only* for those models (and ignore all others).
    consume_models = None

    # Set this to a sequence of model names if you wish to *ignore* data *only*
    # for those models (and consume all others).
    ignore_models = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.engine = self.config.appdb_engines[self.dbkey]
        self.model = self.get_data_model()
        self.topo_sortkey = make_topo_sortkey(self.model)

    # TODO: deprecate / remove this
    def get_data_model(self):
        """
        Subclasses may override this if they have extended the schema.
        Defaults to ``rattail.db.model``.
        """
        return self.app.model

    def process_changes(self, host_session, changes):
        """
        Process changes for a Rattail database.
        """
        # First determine which models are represented in the change set.  Some
        # models may be ignored, depending on the subclass logic etc.
        class_names = set([c.payload_type for c in changes])
        if self.consume_models is not None:
            class_names = [c for c in class_names if c in self.consume_models]
        elif self.ignore_models is not None:
            class_names = [c for c in class_names if c not in self.ignore_models]

        # The order will matter because of table foreign key dependencies.  We
        # start with a lexical sort just for kicks maybe...
        class_names = sorted(class_names)
        class_names.sort(key=self.topo_sortkey)

        session = self.app.make_session(bind=self.engine)
        if self.runas_username:
            session.set_continuum_user(self.runas_username)

        for class_name in class_names:

            # this consumer does not need to process these changes; see
            # FromRattailToRattailBase for one which can process them
            if class_name == 'ProductPriceAssociation':
                continue

            cls = getattr(self.model, class_name)

            for change in [c for c in changes if c.payload_type == class_name]:
                log.debug("processing {0} for {1} {2}".format(
                    "deletion" if change.deletion else "change",
                    change.payload_type, change.payload_key))

                if change.deletion:
                    instance = session.get(cls, change.payload_key)
                    if instance:
                        self.delete_instance(session, instance)
                        session.flush()
                    else:
                        log.warning("could not find instance to delete")

                else: # add/update
                    host_instance = host_session.get(cls, change.payload_key)
                    if host_instance:

                        # if processing a pack item, must process its unit item
                        # first.  this is because both may be "new" in which
                        # case the unit item must exist before the pack may
                        # reference it.
                        if class_name == 'Product' and host_instance.is_pack_item():
                            self.merge_instance(session, host_instance.unit)

                        self.merge_instance(session, host_instance)
                        session.flush()
                    else:
                        log.warning("could not find host instance to merge")

        session.commit()
        session.close()

    def merge_instance(self, session, instance):
        """
        Merge the given model instance into the given database session.

        Subclasses may define model-specific methods instead of or in addition
        to overriding this generic one.
        """
        class_name = instance.__class__.__name__.lower()
        merger = getattr(self, 'merge_{0}'.format(class_name), None)
        if merger:
            return merger(session, instance)

        # Nothing special defined, so just do the normal thing.
        return session.merge(instance)

    def delete_instance(self, session, instance):
        """
        Delete the given model instance from the given database session.

        Subclasses may define model-specific methods instead of or in addition
        to overriding this generic one.
        """
        class_name = instance.__class__.__name__.lower()

        deleter = getattr(self, 'delete_{0}'.format(class_name), None)
        if deleter:
            return deleter(session, instance)

        predeleter = getattr(self, 'predelete_{0}'.format(class_name), None)
        if predeleter:
            predeleter(session, instance)

        session.delete(instance)

    def merge_product(self, session, source_product):
        """
        This method is somewhat of a hack, in order to properly handle
        :class:`rattail.db.model.Product` instances and the interdependent
        nature of the related :class:`rattail.db.model.ProductPrice` instances.
        """

        target_product = session.merge(source_product)

        # I'm not 100% sure I understand this correctly, but here's my
        # thinking: First we clear the price relationships in case they've
        # actually gone away; then we re-establish any which are currently
        # valid.

        # Setting the price relationship attributes to ``None`` isn't enough to
        # force the ORM to notice a change, since the UUID field is ultimately
        # what it's watching.  So we must explicitly use that field here.
        target_product.regular_price_uuid = None
        target_product.tpr_price_uuid = None
        target_product.sale_price_uuid = None
        target_product.current_price_uuid = None
        target_product.suggested_price_uuid = None

        # If the source instance has currently valid price relationships, then
        # we re-establish them.  We must merge the source price instance in
        # order to be certain it will exist in the target session, and avoid
        # foreign key errors.  However we *still* must also set the UUID fields
        # because again, the ORM is watching those...  This was noticed to be
        # the source of some bugs where successive database syncs were
        # effectively "toggling" the price relationship.  Setting the UUID
        # field explicitly seems to solve it.
        if source_product.regular_price_uuid:
            target_product.regular_price = session.merge(source_product.regular_price)
            target_product.regular_price_uuid = target_product.regular_price.uuid
        if source_product.tpr_price_uuid:
            target_product.tpr_price = session.merge(source_product.tpr_price)
            target_product.tpr_price_uuid = target_product.tpr_price.uuid
        if source_product.sale_price_uuid:
            target_product.sale_price = session.merge(source_product.sale_price)
            target_product.sale_price_uuid = target_product.sale_price.uuid
        if source_product.current_price_uuid:
            target_product.current_price = session.merge(source_product.current_price)
            target_product.current_price_uuid = target_product.current_price.uuid
        if source_product.suggested_price_uuid:
            target_product.suggested_price = session.merge(source_product.suggested_price)
            target_product.suggested_price_uuid = target_product.suggested_price.uuid

        return target_product

    def predelete_department(self, session, department):

        # Disconnect from all subdepartments.
        q = session.query(model.Subdepartment).filter(
            model.Subdepartment.department == department)
        for subdept in q:
            subdept.department = None

        # Disconnect from all products.
        q = session.query(model.Product).filter(
            model.Product.department == department)
        for product in q:
            product.department = None

    def predelete_subdepartment(self, session, subdepartment):

        # Disconnect from all products.
        q = session.query(model.Product).filter(
            model.Product.subdepartment == subdepartment)
        for product in q:
            product.subdepartment = None

    def predelete_family(self, session, family):

        # Disconnect from all products.
        q = session.query(model.Product).filter(
            model.Product.family == family)
        for product in q:
            product.family = None

    def predelete_vendor(self, session, vendor):

        # Remove all product costs.
        q = session.query(model.ProductCost).filter(
            model.ProductCost.vendor == vendor)
        for cost in q:
            session.delete(cost)

    def predelete_customergroup(self, session, group):

        # Disconnect from all customers.
        q = session.query(model.CustomerGroupAssignment).filter(
            model.CustomerGroupAssignment.group == group)
        for assignment in q:
            session.delete(assignment)


class FromRattailToRattailBase(DataSyncImportConsumer):
    """
    Base class for Rattail -> Rattail datasync consumers
    """

    def setup(self):
        super().setup()
        self.topo_sortkey = make_topo_sortkey(self.model)
        self.handle_price_xref = self.get_handle_price_xref()

    def get_handle_price_xref(self):
        if hasattr(self, 'handle_price_xref'):
            return self.handle_price_xref

        # TODO: this should default to True, once logic is proven
        return self.config.getbool(
            'rattail.datasync', 'rattail.handle_price_xref',
            default=False)

    def get_importers(self):
        importers = super().get_importers()

        # add the GlobalRole importer, in place of Role, unless latter
        # is already present.
        if 'Role' not in importers:
            importers['Role'] = self.handler.get_importer('GlobalRole')

        # maybe add importer to handle product price reference changes
        if self.get_handle_price_xref() and 'ProductPriceAssociation' not in importers:
            importers['ProductPriceAssociation'] = self.handler.get_importer('ProductPriceAssociation')

        return importers

    def get_host_object(self, session, change):
        if change.payload_type == 'ProductPriceAssociation':
            cls = self.model.Product
        else:
            cls = getattr(self.model, change.payload_type)
        return session.get(cls, change.payload_key)


class FromRattailToRattailExportConsumer(FromRattailToRattailBase):
    """
    Export data changes from "local" Rattail to another
    """
    handler_spec = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.target_engine = self.config.appdb_engines[self.dbkey]
        self.model = self.app.model

    def make_target_session(self):
        return self.app.make_session(bind=self.target_engine)

    def begin_transaction(self):
        self.local_session = self.app.make_session()
        self.target_session = self.make_target_session()

    def rollback_transaction(self):
        self.target_session.rollback()
        self.target_session.close()

        self.local_session.rollback()
        self.local_session.close()

    def commit_transaction(self):
        self.local_session.commit()
        self.local_session.close()

        self.target_session.commit()
        self.target_session.close()

    def pre_process_changes(self, session, changes):
        if self.runas_username:
            self.target_session.set_continuum_user(self.runas_username)

        # update all importers with current sessions
        for importer in self.importers.values():
            importer.host_session = self.local_session
            importer.session = self.target_session


class FromRattailToRattailImportConsumer(FromRattailToRattailBase):
    """
    Import data changes from another Rattail to "local"
    """
    handler_spec = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.host_engine = self.config.appdb_engines[self.watcher.dbkey]
        self.local_engine = self.config.appdb_engines[self.dbkey]
        self.model = self.app.model

    def process_changes(self, session, changes):
        self.host_session = self.app.make_session(bind=self.host_engine)
        local_session = self.app.make_session(bind=self.local_engine)
        if self.runas_username:
            local_session.set_continuum_user(self.runas_username)

        # update all importers with current sessions
        for importer in self.importers.values():
            importer.host_session = self.host_session
            importer.session = local_session

        # topographically sort changes, i.e. per schema table dependencies.
        # we start with a lexical sort just for kicks maybe...
        class_names = set([c.payload_type for c in changes])
        class_names = sorted(class_names)
        class_names.sort(key=self.topo_sortkey)

        for class_name in class_names:
            cls = getattr(self.model, class_name)
            for change in [c for c in changes if c.payload_type == class_name]:
                self.invoke_importer(session, change)

        local_session.commit()
        local_session.close()
        # TODO: should we ever commit this..?
        # self.host_session.commit()
        self.host_session.close()

    def get_host_object(self, session, change):
        # we use base logic to get the object, but must substitute the
        # session to ensure we read from actual host and not local
        return super().get_host_object(self.host_session, change)
