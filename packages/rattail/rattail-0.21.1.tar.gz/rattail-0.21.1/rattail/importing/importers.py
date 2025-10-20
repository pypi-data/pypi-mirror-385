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
Data Importers
"""

import datetime
import logging
from collections import OrderedDict

from rattail.util import data_diffs
from rattail.csvutil import UnicodeDictReader


log = logging.getLogger(__name__)


# TODO
class ImportLimitReached(Exception):
    pass


class Importer(object):
    """
    Base class for all data importers.

    .. attribute:: direction

       Should be a string, either ``'import'`` or ``'export'``.  This value is
       used to improve verbiage for logging and other output, for a better
       overall user experience.  It may also be used by importer logic, where
       the direction would otherwise be ambiguous.

       Note that the handler is responsible for assigning this value; the
       importer should not define it.  See also
       :attr:`rattail.importing.handlers.ImportHandler.direction`.

    :attr collect_changes_for_processing:

       If true (the default) then any changes occurring as a result of the
       import will be collected for processing by the handler, once the import
       has completed.  (I.e. it might send out a warning email with the
       changes.)  If the changes are not "important" per se, and they involve
       large data sets, then you may want to turn off this flag to avoid the
       overhead of collecting the changes.  In practice this is usually done if
       memory consumption is too great, as long as you don't actually need to
       track the changes.  Also note that the flag usually may be turned off 
       via command line kwarg (``--no-collect-changes``).
    """
    # Set this to the data model class which is targeted on the local side.
    model_class = None
    model_name = None

    key = None

    # The full list of field names supported by the importer, i.e. for the data
    # model to which the importer pertains.  By definition this list will be
    # restricted to what the local side can acommodate, but may be further
    # restricted by what the host side has to offer.
    supported_fields = []

    # The list of field names which may be considered "simple" and therefore
    # treated as such, i.e. with basic getattr/setattr calls.  Note that this
    # only applies to the local side, it has no effect on the host side.
    simple_fields = []

    allow_create = True
    allow_update = True
    allow_delete = True
    dry_run = False

    max_create = None
    max_update = None
    max_delete = None
    max_total = None
    batch_size = 200
    progress = None

    empty_local_data = False
    caches_local_data = False
    cached_local_data = None

    host_system_title = None
    local_system_title = None

    collect_changes_for_processing = True

    # TODO
    # Whether or not the registered "importer" batch handler is able to handle
    # batches for this importer (and/or, whether this importer is able to
    # provide what's needed for the same).
    batches_supported = False

    # TODO
    # If ``batches_supported`` is true, this should contain SQLAlchemy
    # ``Column`` instance overrides, keyed by fieldname.  Any field not
    # represented here will be given the default column type (string).
    field_coltypes = {}

    def __init__(self, config=None, key=None, direction='import',
                 fields=None, exclude_fields=None,
                 fuzzy_fields=None, fuzz_factor=None,
                 **kwargs):
        self.config = config
        self.app = config.get_app() if config else None
        self.enum = config.get_enum() if config else None
        try:
            self.model = self.app.model if config else None
        except ImportError:
            pass
        self.model_class = kwargs.pop('model_class', self.get_model_class())
        if key is not None:
            self.key = key
        self.direction = direction
        self.fields = fields or self.supported_fields
        if exclude_fields:
            self.exclude_fields(*exclude_fields)
        self.fuzzy_fields = fuzzy_fields or []
        self.fuzz_factor = fuzz_factor
        if isinstance(self.key, str):
            self.key = (self.key,)
        if self.key:
            for field in self.key:
                if field not in self.fields:
                    raise ValueError("Key field '{}' must be included in effective fields "
                                     "for {}".format(field, self.__class__.__name__))
        self.model_name = kwargs.pop('model_name', self.model_name)
        if not self.model_name and self.model_class:
            self.model_name = self.model_class.__name__
        self._setup(**kwargs)

    def get_local_system_title(self):
        """
        Retrieve the system title for the local/target side.
        """
        if hasattr(self, 'handler'):
            return self.handler.local_title
        return self.local_system_title or "??"

    def include_fields(self, *args):
        """
        Add the given fields to the supported field list for the importer.  May
        be used at runtime to customize behavior.
        """
        for field in args:
            if field not in self.fields:
                self.fields.append(field)

    def exclude_fields(self, *args):
        """
        Remove the given fields from the supported field list for the importer.
        May be used at runtime to customize behavior.
        """
        for field in args:
            if field in self.fields:
                self.fields.remove(field)

    def get_model_class(self):
        return self.model_class

    def fields_active(self, fields):
        """
        Convenience method to check if any of the given fields are currently
        "active" for the importer.  Returns ``True`` or ``False``.
        """
        for field in fields:
            if field in self.fields:
                return True
        return False

    def _setup(self, **kwargs):
        self.create = kwargs.pop('create', self.allow_create) and self.allow_create
        self.update = kwargs.pop('update', self.allow_update) and self.allow_update
        self.delete = kwargs.pop('delete', False) and self.allow_delete
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.establish_date_range()

    def establish_date_range(self):
        now = self.app.localtime()
        today = now.date()

        # start date is empty by default, unless specified
        start_date = None
        if hasattr(self, 'start_date'):
            start_date = self.start_date
        if not start_date and hasattr(self, 'args') and hasattr(self.args, 'start_date'):
            start_date = self.args.start_date
        self.start_date = start_date

        # start time defaults to 12am midnight of start date, if applicable
        start_time = None
        if hasattr(self, 'start_time'):
            start_time = self.start_time
        if not start_time and self.start_date:
            start_time = datetime.datetime.combine(self.start_date,
                                                   datetime.time(0))
            start_time = self.app.localtime(start_time)
        self.start_time = start_time

        # end date is empty by default, unless specified
        end_date = None
        if hasattr(self, 'end_date'):
            end_date = self.end_date
        if not end_date and hasattr(self, 'args') and hasattr(self.args, 'end_date'):
            end_date = self.args.end_date
        self.end_date = end_date

        # end time defaults to 12am midnight of *day after* end date, unless specified
        end_time = None
        if hasattr(self, 'end_time'):
            end_time = self.end_time
        if not end_time and self.end_date:
            end_date = self.end_date + datetime.timedelta(days=1)
            end_time = datetime.datetime.combine(end_date, datetime.time(0))
            end_time = self.app.localtime(end_time)
        self.end_time = end_time

        # and some commands use --year instead of date range
        year = None
        if hasattr(self, 'year'):
            year = self.year
        if not year and hasattr(self, 'args') and hasattr(self.args, 'year'):
            year = self.args.year
        self.year = year

    def setup(self):
        """
        Perform any setup necessary, e.g. cache lookups for existing data.
        """

    def datasync_setup(self):
        """
        Perform any setup necessary, in the context of a datasync job.
        """

    def teardown(self):
        """
        Perform any cleanup after import, if necessary.
        """

    def progress_loop(self, func, items, factory=None, **kwargs):
        factory = factory or self.progress
        return self.app.progress_loop(func, items, factory, **kwargs)

    def unique_data(self, host_data, warn=True):
        # Prune duplicate keys from host/source data.  This is for the sake of
        # sanity since duplicates typically lead to a ping-pong effect, where a
        # "clean" (change-less) import is impossible.
        unique = OrderedDict()
        for data in host_data:
            key = self.get_key(data)
            if key in unique:
                logger = log.warning if warn else log.debug
                logger("duplicate records detected from %s for key: %s",
                       self.host_system_title, key)
            else:
                unique[key] = data
        return list(unique.values()), unique

    def import_data(self, host_data=None, now=None, **kwargs):
        """
        Import some data!  This is the core body of logic for that, regardless
        of where data is coming from or where it's headed.  Note that this
        method handles deletions as well as adds/updates.
        """
        self.now = now or self.app.make_utc(tzinfo=True)
        if kwargs:
            self._setup(**kwargs)
        self.setup()
        created = []
        updated = []
        deleted = []

        # Get complete set of normalized host data.
        if host_data is None:
            host_data = self.normalize_host_data()
        host_data, unique = self.unique_data(host_data)

        # Cache local data if appropriate.
        if self.caches_local_data:
            self.cached_local_data = self.cache_local_data(host_data)

        # Create and/or update data.
        if self.create or self.update:
            if self.collect_changes_for_processing:
                created, updated = self._import_create_update(host_data)
            else:
                self._import_create_update(host_data)

        # Delete data.
        if self.delete:
            changes = len(created) + len(updated)
            if self.max_total and changes >= self.max_total:
                log.warning("max of {} total changes already reached; skipping deletions".format(self.max_total))
            elif self.collect_changes_for_processing:
                deleted = self._import_delete(host_data, set(unique), changes=changes)
            else:
                self._import_delete(host_data, set(unique), changes=changes)

        self.teardown()
        return created, updated, deleted

    # TODO: this should probably be used with datasync where possible?
    def import_single_object(self, host_object, **kwargs):
        """
        Import a single object from host.  This is meant primarily for
        use with scripts etc. and is not part of a "normal" (full)
        import run.
        """
        host_data = self.normalize_host_object(host_object)
        key = self.get_key(host_data)

        local_object = self.get_local_object(key)
        if local_object:
            if self.allow_update:

                # update local object only if data differs
                local_data = self.normalize_local_object(local_object)
                if self.data_diffs(local_data, host_data) and self.allow_update:
                    local_object = self.update_object(local_object, host_data, local_data)

            return local_object

        elif self.allow_create:

            # create new local object
            return self.create_object(key, host_data)

    def _import_create_update(self, data, created=None, updated=None):
        """
        Import the given data; create and/or update records as needed.
        """
        if created is None:
            created = []
        if updated is None:
            updated = []
        count = len(data)
        if not count:
            return created, updated
        dummy = object()

        def import_(host_data, i):
            
            # Fetch local object, using key from host data.
            key = self.get_key(host_data)
            local_object = self.get_local_object(key)

            # If we have a local object, but its data differs from host, update it.
            if local_object and self.update:
                local_data = self.normalize_local_object(local_object)
                diffs = self.data_diffs(local_data, host_data)
                if diffs:
                    log.debug("fields '{}' differed for local data: {}, host data: {}".format(
                        ','.join(diffs), local_data, host_data))
                    local_object = self.update_object(local_object, host_data, local_data=local_data)
                    if self.collect_changes_for_processing:
                        updated.append((local_object, local_data, host_data))
                    else:
                        updated.append(dummy)
                    if self.max_update and len(updated) >= self.max_update:
                        log.warning("max of {} *updated* records has been reached; stopping now".format(self.max_update))
                        raise ImportLimitReached()
                    if self.max_total and (len(created) + len(updated)) >= self.max_total:
                        log.warning("max of {} *total changes* has been reached; stopping now".format(self.max_total))
                        raise ImportLimitReached()

            # If we did not yet have a local object, create it using host data.
            elif not local_object and self.create:
                local_object = self.create_object(key, host_data)
                if local_object:
                    log.debug("created new %s %s: %s",
                              self.model_name, key, local_object)
                    if self.collect_changes_for_processing:
                        created.append((local_object, host_data))
                    else:
                        created.append(dummy)
                    if self.caches_local_data and self.cached_local_data is not None:
                        self.cached_local_data[key] = {'object': local_object, 'data': self.normalize_local_object(local_object)}
                    if self.max_create and len(created) >= self.max_create:
                        log.warning("max of {} *created* records has been reached; stopping now".format(self.max_create))
                        raise ImportLimitReached()
                    if self.max_total and (len(created) + len(updated)) >= self.max_total:
                        log.warning("max of {} *total changes* has been reached; stopping now".format(self.max_total))
                        raise ImportLimitReached()
                else:
                    log.debug("did NOT create new {} for key: {}".format(self.model_name, key))

            # flush changes every so often
            flush = False
            if not self.batch_size or self.batch_size == 1:
                # flush every time if no meaningful batch size
                flush = True
            elif created or updated:
                if (len(created) + len(updated)) % self.batch_size == 0:
                    flush = True
            if flush:
                self.flush_create_update()

        try:
            self.progress_loop(import_, data, message="{}ing {} data to {}".format(
                self.direction.capitalize(), self.model_name, self.get_local_system_title()))
        except ImportLimitReached:
            pass
        self.flush_create_update_final()
        return created, updated

    # def _populate_create_update(self, row_table, data):
    #     """
    #     Populate create and/or update records for the given batch row table,
    #     according to the given host data set.
    #     """
    #     created = []
    #     updated = []
    #     # count = len(data)
    #     # if not count:
    #     #     return created, updated

    #     def record(host_data, i):
            
    #         # fetch local object, using key from host data
    #         key = self.get_key(host_data)
    #         local_object = self.get_local_object(key)

    #         # if we have a local object, but its data differs from host, make an update record
    #         if local_object and self.update:
    #             local_data = self.normalize_local_object(local_object)
    #             diffs = self.data_diffs(local_data, host_data)
    #             if diffs:
    #                 log.debug("fields '{}' differed for local data: {}, host data: {}".format(
    #                     ','.join(diffs), local_data, host_data))
    #                 local_object = self.update_object(local_object, host_data, local_data)
    #                 updated.append((local_object, local_data, host_data))
    #                 if self.max_update and len(updated) >= self.max_update:
    #                     log.warning("max of {} *updated* records has been reached; stopping now".format(self.max_update))
    #                     raise ImportLimitReached()
    #                 if self.max_total and (len(created) + len(updated)) >= self.max_total:
    #                     log.warning("max of {} *total changes* has been reached; stopping now".format(self.max_total))
    #                     raise ImportLimitReached()

    #         # if we did not yet have a local object, make a create record
    #         elif not local_object and self.create:
    #             local_object = self.create_object(key, host_data)
    #             if local_object:
    #                 log.debug("created new {} {}: {}".format(self.model_name, key, local_object))
    #                 created.append((local_object, host_data))
    #                 if self.caches_local_data and self.cached_local_data is not None:
    #                     self.cached_local_data[key] = {'object': local_object, 'data': self.normalize_local_object(local_object)}
    #                 if self.max_create and len(created) >= self.max_create:
    #                     log.warning("max of {} *created* records has been reached; stopping now".format(self.max_create))
    #                     raise ImportLimitReached()
    #                 if self.max_total and (len(created) + len(updated)) >= self.max_total:
    #                     log.warning("max of {} *total changes* has been reached; stopping now".format(self.max_total))
    #                     raise ImportLimitReached()
    #             else:
    #                 log.debug("did NOT create new {} for key: {}".format(self.model_name, key))

    #         # flush changes every so often
    #         if not self.batch_size or (len(created) + len(updated)) % self.batch_size == 0:
    #             self.flush_create_update()

    #     try:
    #         self.progress_loop(record, data, message="Importing {} data".format(self.model_name))
    #     except ImportLimitReached:
    #         pass
    #     # self.flush_create_update_final()
    #     return created, updated

    def flush_create_update(self):
        """
        Perform any steps necessary to "flush" the create/update changes which
        have occurred thus far in the import.
        """

    def flush_create_update_final(self):
        """
        Perform any final steps to "flush" the created/updated data here.
        """
        self.flush_create_update()

    def _import_delete(self, host_data, host_keys, changes=0):
        """
        Import deletions for the given data set.
        """
        deleted = []
        deleting = self.get_deletion_keys() - host_keys
        count = len(deleting)
        log.debug("found {} instances to delete".format(count))
        dummy = object()

        def delete(key, i):
            cached = self.cached_local_data.pop(key)
            obj = cached['object']
            if self.delete_object(obj):
                if self.collect_changes_for_processing:
                    deleted.append((obj, cached['data']))
                else:
                    deleted.append(dummy)
                if self.max_delete and len(deleted) >= self.max_delete:
                    log.warning("max of {} *deleted* records has been reached; stopping now".format(self.max_delete))
                    raise ImportLimitReached()
                if self.max_total and (changes + len(deleted)) >= self.max_total:
                    log.warning("max of {} *total changes* has been reached; stopping now".format(self.max_total))
                    raise ImportLimitReached()

            # flush changes every so often
            flush = False
            if not self.batch_size or self.batch_size == 1:
                # flush every time if no meaningful batch size
                flush = True
            elif deleted and len(deleted) % self.batch_size == 0:
                flush = True
            if flush:
                self.flush_delete()

        try:
            self.progress_loop(delete, sorted(deleting),
                               message="Deleting {} data".format(self.model_name))
        except ImportLimitReached:
            pass

        return deleted

    def flush_delete(self):
        """
        Perform any steps necessary to "flush" the create/update changes which
        have occurred thus far in the import.
        """

    def get_key(self, data):
        """
        Return the key value for the given data dict.
        """
        return tuple(data[k] for k in self.key)

    def get_host_objects(self):
        """
        Return the "raw" (as-is, not normalized) host objects which are to be
        imported.  This may return any sequence-like object, which has a
        ``len()`` value and responds to iteration etc.  The objects contained
        within it may be of any type, no assumptions are made there.  (That is
        the job of the :meth:`normalize_host_data()` method.)
        """
        return []

    def normalize_host_data(self, host_objects=None):
        """
        Return a normalized version of the full set of host data.  Note that
        this calls :meth:`get_host_objects()` to obtain the initial raw
        objects, and then normalizes each object.  The normalization process
        may filter out some records from the set, in which case the return
        value will be smaller than the original data set.
        """
        if host_objects is None:
            host_objects = self.get_host_objects()
        normalized = []

        def normalize(obj, i):
            data = self.normalize_host_object_all(obj)
            if data:
                normalized.extend(data)

        self.progress_loop(normalize, host_objects,
                           message="Reading {} data from {}".format(
                               self.model_name, self.host_system_title))
        return normalized

    def normalize_host_object_all(self, obj):
        data = self.normalize_host_object(obj)
        if data:
            return [data]

    def normalize_host_object(self, obj):
        """
        Normalize a raw host object into a data dict, or return ``None`` if the
        object should be ignored for the importer's purposes.
        """
        return obj

    def get_next_counter_value(self, name, **kwargs):
        attr = '_next_counter_{}'.format(name)
        if hasattr(self, attr):
            next_value = getattr(self, attr)
        else:
            next_value = 1
        setattr(self, attr, next_value + 1)
        return next_value

    def get_local_objects(self, host_data=None):
        """
        Fetch all raw objects from the local system.
        """
        raise NotImplementedError

    def cache_local_data(self, host_data=None):
        """
        Cache all raw objects and normalized data from the local system.
        """
        objects = self.get_local_objects(host_data=host_data)
        cached = {}

        def cache(obj, i):
            data = self.normalize_local_object(obj)
            if data:
                key = self.get_key(data)
                cached[key] = {'object': obj, 'data': data}

        self.progress_loop(cache, objects,
                           message="Reading {} data from {}".format(
                               self.model_name, self.get_local_system_title()))
        return cached

    def cache_local_message(self):
        """
        Must return a message to be used for progress when fetching "local" data.
        """
        return "Reading {} data from {}".format(self.model_name, self.get_local_system_title())

    def get_cache_key(self, obj, normal):
        """
        Get the primary cache key for a given object and normalized data.

        Note that this method's signature is designed for use with the
        :func:`rattail.db.cache.cache_model()` function, and as such the
        ``normal`` parameter is understood to be a dict with a ``'data'`` key,
        value for which is the normalized data dict for the raw object.
        """
        return tuple(normal['data'].get(k) for k in self.key)

    def normalize_cache_object(self, obj, data=None):
        """
        Normalizer for cached local data.  This returns a simple dict with
        ``'object'`` and ``'data'`` keys; values are the raw object and its
        normalized data dict, respectively.
        """
        if data is None:
            data = self.normalize_local_object(obj)
        return {'object': obj, 'data': data}

    def normalize_local_object(self, obj):
        """
        Normalize a local (raw) object into a data dict.
        """
        fields = [f for f in self.simple_fields
                  if f in self.fields]
        # note, we normally should have a proper object here, but in
        # some (e.g. dry-run) cases we may just have a dict; we should
        # do the right thing if so
        if isinstance(obj, dict):
            data = dict([(field, obj[field])
                         for field in fields])
        else:
            data = dict([(field, getattr(obj, field))
                         for field in fields])
        return data

    def get_local_object(self, key):
        """
        Must return the local object corresponding to the given key, or
        ``None``.  Default behavior here will be to check the cache if one is
        in effect, otherwise return the value from
        :meth:`get_single_local_object()`.
        """
        if not self.empty_local_data:
            if self.caches_local_data and self.cached_local_data is not None:
                data = self.cached_local_data.get(key)
                return data['object'] if data else None
            return self.get_single_local_object(key)

    def get_single_host_object(self, key):
        """
        Must return the host object corresponding to the given key, or
        None.  This method should not consult the cache; it is meant
        to be called within datasync or other "one-off" scenarios.
        """
        raise NotImplementedError

    def get_single_local_object(self, key):
        """
        Must return the local object corresponding to the given key, or None.
        This method should not consult the cache; that is handled within the
        :meth:`get_local_object()` method.
        """
        raise NotImplementedError

    def cache_model(self, model, **kwargs):
        """
        Convenience method which invokes :func:`rattail.db.cache.cache_model()`
        with the given model and keyword arguments.  It will provide the
        ``session`` and ``progress`` parameters by default, setting them to the
        importer's attributes of the same names.
        """
        session = kwargs.pop('session', None)
        if not session:
            session = self.session
        kwargs.setdefault('progress', self.progress)
        return self.app.cache_model(session, model, **kwargs)

    def data_diffs(self, local_data, host_data):
        """
        Find all (relevant) fields which differ between the host and local data
        values for a given record.
        """
        return data_diffs(local_data, host_data,
                          fields=self.fields,
                          fuzzy_fields=self.fuzzy_fields,
                          fuzz_factor=self.fuzz_factor)

    def make_object(self):
        """
        Make a new/empty local object from scratch.
        """
        return self.model_class()

    def new_object(self, key):
        """
        Return a new local object to correspond to the given key.  Note that
        this method should only populate the object's key, and leave the rest
        of the fields to :meth:`update_object()`.
        """
        obj = self.make_object()
        for i, k in enumerate(self.key):
            if hasattr(obj, k):
                setattr(obj, k, key[i])
        return obj

    def create_object(self, key, host_data):
        """
        Create and return a new local object for the given key, fully populated
        from the given host data.  This may return ``None`` if no object is
        created.
        """
        if not host_data.get('_deleted_', False):
            obj = self.new_object(key)
            if obj:
                return self.update_object(obj, host_data)

    def update_object(self, obj, host_data, local_data=None, all_fields=False):
        """
        Update the local data object with the given host data, and return the
        object.
        """
        for field in self.simple_fields:
            if field not in self.key and field in host_data and (all_fields or field in self.fields):
                if not local_data or field not in local_data or local_data[field] != host_data[field]:
                    setattr(obj, field, host_data[field])
        return obj

    def get_deletion_keys(self):
        """
        Return a set of keys from the *local* data set, which are eligible for
        deletion.  By default this will be all keys from the local cached data
        set, or an empty set if local data isn't cached.
        """
        if not self.caches_local_data:
            return set()

        if self.cached_local_data is None:
            return set()

        all_keys = set(self.cached_local_data)
        keys = set()

        def check(key, i):
            data = self.cached_local_data[key]['data']
            obj = self.cached_local_data[key]['object']
            if self.can_delete_object(obj, data):
                keys.add(key)

        self.progress_loop(check, all_keys,
                           message="Determining which objects can be deleted")
        return keys

    def can_delete_object(self, obj, data):
        """
        Should return a boolean indiciating whether or not the given
        object "can" be deleted.  Default is to return ``True`` in all
        cases.

        If you return ``False`` then the importer will not perform any
        delete action on the object.
        """
        return True

    def delete_object(self, obj):
        """
        Delete the given object from the local system (or not), and return a
        boolean indicating whether deletion was successful.  What exactly this
        entails may vary; default implementation does nothing at all.
        """
        return True

    def prioritize_2(self, data, field, field2=None):
        """
        Prioritize the data values for the pair of fields implied by the given
        fieldname.  I.e., if only one non-empty value is present, make sure
        it's in the first slot.
        """
        if not field2:
            field2 = '{}_2'.format(field)
        if field in data and field2 in data:
            if data[field2] and not data[field]:
                data[field], data[field2] = data[field2], None


class FromCSV(Importer):
    """
    Generic base class for importers whose data source is a CSV file.
    """

    def setup(self):
        if not hasattr(self, 'source_data_path'):
            if hasattr(self, 'args') and hasattr(self.args, 'source_csv'):
                self.source_data_path = self.args.source_csv

    def get_host_objects(self):
        source_csv_file = open(self.source_data_path, 'rt', encoding='latin_1')
        reader = UnicodeDictReader(source_csv_file)
        objects = list(reader)
        source_csv_file.close()
        return objects


class FromQuery(Importer):
    """
    Generic base class for importers whose raw external data source is a
    SQLAlchemy (or Django, or possibly other?) query.
    """

    def query(self):
        """
        Subclasses must override this, and return the primary query which will
        define the data set.
        """
        raise NotImplementedError

    def get_host_objects(self):
        """
        Returns (raw) query results as a sequence.
        """
        from rattail.db.util import QuerySequence

        query = self.query()
        if hasattr(self, 'sorted_query'):
            query = self.sorted_query(query)
        return QuerySequence(query)


class FromDjango(FromQuery):
    """
    Base class for importers using Django ORM on the host side.
    """
    django_dbkey = 'default'

    def query(self):
        return self.host_model_class.objects.using(self.django_dbkey).all()


class BatchImporter(Importer):
    """
    Base class for importers which split their jobs up into batches
    """

    def import_data(self, host_data=None, now=None, **kwargs):
        """
        Import some data!  We must override the default logic here, in order to
        chop up the job into proper batches.  This is because image data is
        relatively large, and fetching all at once is not performant.
        """
        if host_data is not None:
            raise ValueError("User-provided host data is not supported")

        self.now = now or self.app.make_utc(tzinfo=True)
        if kwargs:
            self._setup(**kwargs)
        self.setup()
        created = []
        updated = []
        deleted = []

        self.host_index = 0
        host_data = self.normalize_host_data()
        while host_data:
            if self.caches_local_data:
                self.cached_local_data = self.cache_local_data(host_data)

            if self.collect_changes_for_processing:
                created, updated = self._import_create_update(host_data, created=created, updated=updated)
            else:
                self._import_create_update(host_data)

            if self.max_create and len(created) >= self.max_create:
                log.warning("max of {} *created* records has been reached; stopping now".format(self.max_create))
                break
            if self.max_update and len(updated) >= self.max_update:
                log.warning("max of {} *updated* records has been reached; stopping now".format(self.max_update))
                break
            if self.max_total and (len(created) + len(updated)) >= self.max_total:
                log.warning("max of {} *total changes* has been reached; stopping now".format(self.max_total))
                break

            self.host_index += self.batch_size
            host_data = self.normalize_host_data()

        self.teardown()
        # note that these may not be accurate, if we didn't collect changes above
        return created, updated, deleted

    def cache_local_data(self, host_data=None):
        if host_data is None:
            raise ValueError("Must provide host data to this method")
        if len(self.key) != 1:
            raise RuntimeError("Compound key {} not supported for batch importer: {}".format(self.key, self))
        key = self.key[0]
        keys = [data[key] for data in host_data]
        if keys:
            query = self.session.query(self.model_class)\
                                .filter(getattr(self.model_class, key).in_(keys))
            return self.cache_model(self.model_class, key=self.get_cache_key,
                                    query=query, query_options=self.cache_query_options(),
                                    normalizer=self.normalize_cache_object,
                                    message=self.cache_local_message())
        return {} # empty cache


class BulkImporter(Importer):
    """
    Base class for bulk data importers.
    """

    def import_data(self, host_data=None, now=None, **kwargs):
        self.now = now or self.app.make_utc(tzinfo=True)
        if kwargs:
            self._setup(**kwargs)
        self.setup()
        if host_data is None:
            host_data = self.normalize_host_data()
        created = self._import_create(host_data)
        self.teardown()
        return created

    def _import_create(self, data):
        count = len(data)
        if not count:
            return 0
        created = count

        prog = None
        if self.progress:
            prog = self.progress("Importing {} data".format(self.model_name), count)

        for i, host_data in enumerate(data, 1):

            key = self.get_key(host_data)
            self.create_object(key, host_data)
            if self.max_create and i >= self.max_create:
                log.warning("max of {} *created* records has been reached; stopping now".format(self.max_create))
                created = i
                break

            # flush changes every so often
            if not self.batch_size or i % self.batch_size == 0:
                self.flush_create_update()

            if prog:
                prog.update(i)
        if prog:
            prog.destroy()

        self.flush_create_update_final()
        return created
