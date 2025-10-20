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
Import Handlers
"""

import os
import sys
import shutil
import tempfile
import logging
from collections import OrderedDict

import humanize
import markupsafe

from rattail.util import get_object_spec
from rattail.exceptions import ConfigurationError


log = logging.getLogger(__name__)


class ImportHandler(object):
    """
    Base class for all import handlers.

    .. attribute:: direction

       Should be a string, either ``'import'`` or ``'export'``.  This value is
       used to improve verbiage for logging and other output, for a better
       overall user experience.  It may also be used by importer logic, where
       the direction would otherwise be ambiguous.

       For "most" handlers the distinction is somewhat implied, e.g. Rattail ->
       POS is almost certainly thought of as an *export*, whereas POS ->
       Rattail would be an *import*.  However "export" handlers should still
       define this value accordingly; it's optional for "import" since that is
       the default.

       The value is most useful though, where it is otherwise ambiguous.
       Within a Rattail -> Rattail handler for instance, importer logic may
       consult this value in order to do different things depending on which
       "side" is the local "default" DB.  For example you may have a "host" and
       multiple "store" nodes, and you want to "push" some tables from host ->
       store, but not the other way around.  Since presumably *both* of the
       ``rattail import-rattail`` and ``rattail export-rattail`` (i.e. pull and
       push) commands should be valid to run from any given node, and since the
       importers themselves are "direction-agnostic", the importers must
       consult :attr:`~rattail.importing.importers.Importer.direction` (as well
       as :meth:`~rattail.config.RattailConfig.node_type()`) to know which
       tables to support for each command run.

    .. attribute:: extra_importer_kwargs

       Dictionary of "extra" kwargs which should be passed as-is to the
       constructor when making a new importer instance.  Note that these kwargs
       will be used when making a new importer *of any type*.  Ultimately the
       logic for this is to be found in :meth:`get_importer_kwargs()`.
    """
    host_title = None
    local_title = None
    progress = None
    dry_run = False
    commit_host_partial = False
    diff_max_display = 15
    direction = 'import'
    collect_changes_for_processing = True
    safe_for_web_app = False

    def __init__(self, config=None, **kwargs):
        self.config = config
        if self.config:
            self.app = self.config.get_app()
            self.enum = self.config.get_enum()
            try:
                self.model = self.app.model
            except ImportError:
                pass

        # nb. must assign extra attrs before we get_importers() since
        # attrs may need to affect that behavior
        for key, value in kwargs.items():
            setattr(self, key, value)

        self.importers = self.get_importers()
        self.extra_importer_kwargs = kwargs.pop('extra_importer_kwargs', {})

    @classmethod
    def get_key(cls):
        return 'to_{}.from_{}.{}'.format(cls.local_key, cls.host_key, cls.direction)

    @classmethod
    def get_spec(cls):
        return '{}:{}'.format(cls.__module__, cls.__name__)

    @classmethod
    def get_generic_host_title(cls):
        if hasattr(cls, 'generic_host_title'):
            return cls.generic_host_title
        return "TODO: define `{}.generic_host_title`".format(cls.__name__)

    @classmethod
    def get_generic_local_title(cls):
        if hasattr(cls, 'generic_local_title'):
            return cls.generic_local_title
        return "TODO: define `{}.generic_local_title`".format(cls.__name__)

    @classmethod
    def get_generic_title(cls):
        if hasattr(cls, 'generic_title'):
            return cls.generic_title
        host_title = cls.get_generic_host_title()
        local_title = cls.get_generic_local_title()
        return "{} -> {}".format(host_title, local_title)

    def get_importers(self):
        """
        Returns a dict of all available importers, where the keys are model
        names and the values are importer factories.  All subclasses will want
        to override this.  Note that if you return an
        :class:`python:collections.OrderedDict` instance, you can affect the
        ordering of keys in the command line help system, etc.
        """
        return {}

    def get_importer_keys(self):
        """
        Returns the list of keys corresponding to the available importers.
        """
        return list(self.importers.keys())

    def get_default_keys(self):
        """
        Returns the list of keys corresponding to the "default" importers.
        Override this if you wish certain importers to be excluded by default,
        e.g. when first testing them out etc.
        """
        return self.get_importer_keys()

    def get_importer(self, key, **kwargs):
        """
        Returns an importer instance corresponding to the given key.
        """
        if key in self.importers:
            kwargs.setdefault('handler', self)
            kwargs.setdefault('config', self.config)
            kwargs.setdefault('host_system_title', self.host_title)
            kwargs.setdefault('direction', self.direction)
            kwargs.setdefault('collect_changes_for_processing', self.collect_changes_for_processing)
            if hasattr(self, 'batch_size'):
                kwargs.setdefault('batch_size', self.batch_size)
            if hasattr(self, 'runas_username') and self.runas_username:
                kwargs['runas_username'] = self.runas_username
            if hasattr(self, 'runas_user') and self.runas_user:
                kwargs['runas_user'] = self.runas_user
                kwargs['runas_username'] = self.runas_user.username
            kwargs = self.get_importer_kwargs(key, **kwargs)
            kwargs['key'] = kwargs.pop('key_fields', None)
            if hasattr(self, 'args') and 'args' not in kwargs:
                kwargs['args'] = self.args
            return self.importers[key](**kwargs)

    def get_importer_kwargs(self, key, **kwargs):
        """
        Return a dict of kwargs to be used when construcing an importer with
        the given key.  Default behaior here is just to ensure everything in
        :attr:`extra_importer_kwargs` gets included.
        """
        kw = dict(self.extra_importer_kwargs)
        kw.update(kwargs)
        return kw

    def make_batches(self, *keys, **kwargs):
        """
        Make new import/export batch for each specified model key.
        """
        from rattail.db import Session

        session = Session()
        model = self.app.model
        metadata = sa.MetaData(schema='batch', bind=session.bind)
        user = session.merge(kwargs['runas_user'])
        handler_spec = self.config.get('rattail.batch', 'importer.handler',
                                       default='rattail.batch.importer:ImporterBatchHandler')

        self.progress = kwargs.pop('progress', getattr(self, 'progress', None))

        self.setup()
        self.begin_transaction()
        batches = []

        for key in keys:

            importer = self.get_importer(key, **kwargs)
            if importer and importer.batches_supported:
                log.info("making batch for model: %s", key)
                importer._handler_key = key

                batch = model.ImporterBatch()
                batch.uuid = self.app.make_uuid()
                batch.created_by = user
                batch.batch_handler_spec = handler_spec
                batch.import_handler_spec = get_object_spec(self)
                batch.host_title = self.host_title
                batch.local_title = self.local_title
                batch.importer_key = key
                batch.rowcount = 0

                batch.description = "{} -> {} for {}".format(
                    batch.host_title,
                    batch.local_title,
                    batch.importer_key)

                batch.row_table = batch.uuid

                session.add(batch)
                session.flush()

                row_table = self.make_row_table(metadata, importer, batch)
                self.populate_row_table(session, importer, batch, row_table)
                batches.append(batch)

            elif importer:
                log.info("batches not supported for importer: %s", key)

            else:
                log.warning("skipping unknown model: %s", key)

        self.teardown()
        # TODO: necessary?
        # self.rollback_transaction()
        # self.commit_transaction()

        session.commit()
        session.close()
        return batches

    def make_row_table(self, metadata, importer, batch):
        columns = [
            sa.Column('uuid', sa.String(length=32), nullable=False, primary_key=True),
            sa.Column('sequence', sa.Integer(), nullable=False),
            sa.Column('object_key', sa.String(length=255), nullable=False, default=''),
            sa.Column('object_str', sa.String(length=255), nullable=False, default=''),
        ]

        for field in importer.fields:
            typ = importer.field_coltypes.get(field)

            if not typ and importer.model_class:
                mapper = sa.inspect(importer.model_class)
                if mapper.has_property(field):
                    prop = mapper.get_property(field)
                    if prop:
                        assert len(prop.columns) == 1, "multiple columns ({}) unsupported: {}.{}".format(
                            len(prop.columns), batch.importer_key, field)
                        typ = prop.columns[0].type

            if not typ:
                typ = sa.String(length=255)

            if field in importer.key:
                columns.append(sa.Column('key_{}'.format(field), typ))
            else:
                for prefix in ('pre', 'post'):
                    columns.append(sa.Column('{}_{}'.format(prefix, field), typ))

        columns.extend([
            sa.Column('status_code', sa.Integer(), nullable=False),
            sa.Column('status_text', sa.String(length=255), nullable=True),
        ])

        row_table = sa.Table(batch.row_table, metadata, *columns)
        row_table.create()
        return row_table

    def populate_row_table(self, session, importer, batch, row_table):
        importer.now = self.app.make_utc(tzinfo=True)
        importer.setup()

        # obtain host data
        host_data = importer.normalize_host_data()
        host_data, unique = importer.unique_data(host_data)
        if not host_data:
            return

        # cache local data if appropriate
        if importer.caches_local_data:
            importer.cached_local_data = importer.cache_local_data(host_data)

        # create and/or update
        if importer.create or importer.update:
            self._populate_create_update(session, importer, batch, row_table, host_data)

        # delete
        if importer.delete:
            self._populate_delete(session, importer, batch, row_table, host_data, set(unique))

    def _populate_delete(self, session, importer, batch, row_table, host_data, host_keys):
        deleting = importer.get_deletion_keys() - host_keys

        def delete(key, i):
            cached = importer.cached_local_data.pop(key)
            local_data = cached['data']
            local_data['_object_str'] = str(cached['object'])
            sequence = batch.rowcount + 1
            self.make_batch_row(session, importer, row_table, sequence, None, local_data,
                                status_code=self.enum.IMPORTER_BATCH_ROW_STATUS_DELETE)
            batch.rowcount += 1

        self.app.progress_loop(delete, sorted(deleting), self.progress,
                               message=f"Deleting {importer.model_name} data")

    def _populate_create_update(self, session, importer, batch, row_table, data):

        def record(host_data, i):

            # fetch local object, using key from host data
            key = importer.get_key(host_data)
            local_object = importer.get_local_object(key)
            status_code = self.enum.IMPORTER_BATCH_ROW_STATUS_NOCHANGE
            status_text = None
            make_row = False

            # if we have a local object, but its data differs from host, make an update record
            if local_object and importer.update:
                make_row = True
                local_data = importer.normalize_local_object(local_object)
                diffs = importer.data_diffs(local_data, host_data)
                if diffs:
                    status_code = self.enum.IMPORTER_BATCH_ROW_STATUS_UPDATE
                    status_text = ','.join(diffs)

            # if we did not yet have a local object, make a create record
            elif not local_object and importer.create:
                make_row = True
                local_data = None
                status_code = self.enum.IMPORTER_BATCH_ROW_STATUS_CREATE

            if make_row:
                sequence = batch.rowcount + 1
                self.make_batch_row(session, importer, row_table, sequence, host_data, local_data,
                                    status_code=status_code, status_text=status_text)
                batch.rowcount += 1

        self.app.progress_loop(record, data, self.progress,
                               message=f"Populating batch for {importer._handler_key}")

    def make_batch_row(self, session, importer, row_table, sequence, host_data, local_data, status_code=None, status_text=None):
        values = {
            'uuid': self.app.make_uuid(),
            'sequence': sequence,
            'object_str': '',
            'status_code': status_code,
            'status_text': status_text,
        }

        if host_data:
            if '_object_str' in host_data:
                values['object_str'] = host_data['_object_str']
            elif '_host_object' in host_data:
                values['object_str'] = str(host_data['_host_object'])
            values['object_key'] = ','.join([str(host_data[f]) for f in importer.key])
        elif local_data:
            if '_object_str' in local_data:
                values['object_str'] = local_data['_object_str']
            elif '_object' in local_data:
                values['object_str'] = str(local_data['_object'])
            values['object_key'] = ','.join([local_data[f] for f in importer.key])

        for field in importer.fields:
            if field in importer.key:
                data = host_data or local_data
                values['key_{}'.format(field)] = data[field]
            else:
                if host_data and field in host_data:
                    values['post_{}'.format(field)] = host_data[field]
                if local_data and field in local_data:
                    values['pre_{}'.format(field)] = local_data[field]

        session.execute(row_table.insert(values))

    def import_data(self, *keys, **kwargs):
        """
        Import all data for the given importer/model keys.

        :param retain_used_importers: Optional flag to indicate the handler
           should retain references to all importers it creates/runs.  If this
           flag is set then the handler will have a ``used_importers``
           attribute after this method completes.  This would be a dictionary
           whose keys are model names and values are the importer instances.
        """
        self.import_began = self.app.make_utc(tzinfo=True)
        retain_used_importers = kwargs.pop('retain_used_importers', False)
        if 'dry_run' in kwargs:
            self.dry_run = kwargs['dry_run']
        self.progress = kwargs.pop('progress', getattr(self, 'progress', None))
        self.warnings = kwargs.get('warnings', False)
        kwargs.update({'dry_run': self.dry_run,
                       'progress': self.progress})

        self.setup()
        self.begin_transaction()
        changes = OrderedDict()

        # in here we'll retain the actual importer *instances* which were used,
        # since some of them may have state which callers need to reference for
        # display to user etc.  this doesn't seem like the most elegant
        # solution perhaps, but gets the job done for now.
        if retain_used_importers:
            self.used_importers = {}

        try:
            for key in keys:
                importer = self.get_importer(key, **kwargs)
                if importer:
                    created, updated, deleted = importer.import_data()
                    changed = bool(created or updated or deleted)
                    msg = "{} -> {}: added {:,d}; updated {:,d}; deleted {:,d} {} records"
                    if self.dry_run:
                        msg += " (dry run)"
                    logger = log.warning if changed and self.warnings else log.info
                    logger(msg.format(
                        self.host_title, self.local_title, len(created), len(updated), len(deleted), key))
                    if changed:
                        changes[key] = created, updated, deleted
                    # keep track of actual importer instance, in case caller
                    # needs to reference its state etc.
                    if retain_used_importers:
                        self.used_importers[key] = importer
                else:
                    log.warning("skipping unknown importer: {}".format(key))
        except:
            if self.commit_host_partial and not self.dry_run:
                log.warning("{host} -> {local}: committing partial transaction on host {host} (despite error)".format(
                    host=self.host_title, local=self.local_title))
                self.commit_host_transaction()
            raise
        else:
            if changes:
                self.process_changes(changes)
            if self.dry_run:
                self.rollback_transaction()
            else:
                self.commit_transaction()

        self.teardown()
        return changes

    def setup(self):
        """
        Perform any additional setup if/as necessary, prior to running the
        import task(s).
        """

    def teardown(self):
        """
        Perform any cleanup necessary, after running the import task(s).
        """

    def begin_transaction(self):
        self.begin_host_transaction()
        self.begin_local_transaction()

    def begin_host_transaction(self):
        pass

    def begin_local_transaction(self):
        pass

    def rollback_transaction(self):
        # nb. it can sometimes be important to rollback the local
        # transaction first.  in particular when the import takes a
        # long time, it may be that no activity occurs on the host DB
        # session after the initial data read.  then at the end
        # rolling back the host transaction may trigger a connection
        # timeout error, which then prevents local transaction from
        # being rolled back.  so now we always rollback local first.
        # TODO: maybe sequence should be configurable?
        self.rollback_local_transaction()
        self.rollback_host_transaction()

    def rollback_host_transaction(self):
        pass

    def rollback_local_transaction(self):
        pass

    def commit_transaction(self):
        # nb. it can sometimes be important to commit the local
        # transaction first.  in particular when the import takes a
        # long time, it may be that no activity occurs on the host DB
        # session after the initial data read.  then at the end
        # committing the host transaction may trigger a connection
        # timeout error, which then prevents local transaction from
        # committing.  so now we just commit local first instead.
        # TODO: maybe sequence should be configurable?
        self.commit_local_transaction()
        self.commit_host_transaction()

    def commit_host_transaction(self):
        pass

    def commit_local_transaction(self):
        pass

    def get_cmd(self, ignore_errors=False):
        handler_key = self.get_key()

        cmd = self.config.getlist('rattail.importing', f'{handler_key}.cmd')
        if not cmd or len(cmd) != 2:
            cmd = self.config.getlist('rattail.importing',
                                      f'{handler_key}.default_cmd')

            if not cmd or len(cmd) != 2:
                msg = (f"Missing or invalid config; please set '{handler_key}.default_cmd' in the "
                       "[rattail.importing] section of your config file")
                if ignore_errors:
                    return
                raise ConfigurationError(msg)

        return cmd

    def process_changes(self, changes):
        """
        This method is called any time changes occur, regardless of whether the
        import is running in "warnings" mode.  Default implementation does
        nothing; override as needed.
        """
        # TODO: This whole thing needs a re-write...but for now, waiting until
        # the old importer has really gone away, so we can share its email
        # template instead of bothering with something more complicated.

        if not self.warnings:
            return

        now = self.app.make_utc(tzinfo=True)
        data = {
            'local_title': self.local_title,
            'host_title': self.host_title,
            'direction': self.direction,
            'argv': sys.argv,
            'runtime': humanize.naturaldelta(now - self.import_began),
            'changes': changes,
            'dry_run': self.dry_run,
            'render_record': RecordRenderer(self.config),
            'max_display': self.diff_max_display,
        }

        command = self.get_cmd(ignore_errors=True)
        if command:
            command, subcommand = command

        if command:
            data['command'] = f'{command} {subcommand}'
            key = f'{command}_{subcommand}_updates'
            key = key.replace('-', '_')
        else:
            data['command'] = None
            key = 'rattail_import_updates'

        self.app.send_email(key, fallback_key='rattail_import_updates', data=data)
        log.info("{} -> {}: warning email was sent".format(self.host_title, self.local_title))


class BulkImportHandler(ImportHandler):
    """
    Base class for bulk import handlers.
    """

    def import_data(self, *keys, **kwargs):
        """
        Import all data for the given importer/model keys.
        """
        # TODO: still need to refactor much of this so can share with parent class
        self.import_began = self.app.make_utc(tzinfo=True)
        if 'dry_run' in kwargs:
            self.dry_run = kwargs['dry_run']
        self.progress = kwargs.pop('progress', getattr(self, 'progress', None))
        self.warnings = kwargs.pop('warnings', False)
        kwargs.update({'dry_run': self.dry_run,
                       'progress': self.progress})
        self.setup()
        self.begin_transaction()
        changes = OrderedDict()

        try:
            for key in keys:
                importer = self.get_importer(key, **kwargs)
                if not importer:
                    log.warning("skipping unknown importer: {}".format(key))
                    continue

                created = importer.import_data()
                msg = "%s -> %s: added %s, updated 0, deleted 0 %s records"
                if self.dry_run:
                    msg += " (dry run)"
                logger = log.warning if created and self.warnings else log.info
                logger(msg, self.host_title, self.local_title, created, key)
                if created:
                    changes[key] = created
        except:
            if self.commit_host_partial and not self.dry_run:
                log.warning("{host} -> {local}: committing partial transaction on host {host} (despite error)".format(
                    host=self.host_title, local=self.local_title))
                self.commit_host_transaction()
            raise
        else:
            if self.dry_run:
                self.rollback_transaction()
            else:
                self.commit_transaction()

        self.teardown()
        return changes


class FromFileHandler(ImportHandler):
    """
    Handler for imports whose data comes from file(s) on the host side.
    """

    def get_importer_kwargs(self, key, **kwargs):
        kwargs = super(FromFileHandler, self).get_importer_kwargs(key, **kwargs)

        # tell importers where input dir lives
        kwargs['input_dir'] = self.input_dir

        return kwargs


class ToFileHandler(ImportHandler):
    """
    Handler for imports which target data file(s) on the local side.
    """

    def begin_local_transaction(self):
        # make temp and output dirs. we make the latter first b/c it may not be
        # allowed, in which case let's fail as quick as we can
        self.make_output_dir()
        self.temp_dir = tempfile.mkdtemp()

    def make_output_dir(self):
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def commit_local_transaction(self):
        # move temp files to final dir; remove temp dir
        for name in os.listdir(self.temp_dir):
            temp = os.path.join(self.temp_dir, name)
            path = os.path.join(self.output_dir, name)
            os.rename(temp, path)
        os.rmdir(self.temp_dir)

    def rollback_local_transaction(self):
        # remove temp dir
        shutil.rmtree(self.temp_dir)

    def get_importer_kwargs(self, key, **kwargs):
        kwargs = super(ToFileHandler, self).get_importer_kwargs(key, **kwargs)

        # tell importers to use temp dir for output
        kwargs['output_dir'] = self.temp_dir

        return kwargs


class ToCSVHandler(ToFileHandler):
    """
    Handler for imports which target CSV file(s) on the local side.
    """
    local_key = 'csv'
    generic_local_title = "CSV"


# TODO: this is still pretty hacky, but needed to get it in here for now
class RecordRenderer(object):
    """
    Record renderer for email notifications sent from data import jobs.
    """

    def __init__(self, config):
        self.config = config

    def __call__(self, record):
        return self.render(record)

    def render(self, record):
        """
        Render the given record.
        """
        key = record.__class__.__name__.lower()
        renderer = getattr(self, 'render_{}'.format(key), None)
        if renderer:
            return renderer(record)

        label = self.get_label(record)
        url = self.get_url(record)
        if url:
            return markupsafe.Markup(f'<a href="{url}">{label}</a>')
        return label

    def get_label(self, record):
        key = record.__class__.__name__.lower()
        label = getattr(self, 'label_{}'.format(key), self.label)
        return label(record)

    def label(self, record):
        return str(record)

    def get_url(self, record):
        """
        Fetch / generate a URL for the given data record.  You should *not*
        override this method, but do :meth:`url()` instead.
        """
        key = record.__class__.__name__.lower()
        url = getattr(self, 'url_{}'.format(key), self.url)
        return url(record)

    def url(self, record):
        """
        Fetch / generate a URL for the given data record.
        """
        if hasattr(record, 'uuid'):
            url = self.config.base_url()
            if url:
                name = '{}s'.format(record.__class__.__name__.lower())
                if name == 'persons': # FIXME, obviously this is a hack
                    name = 'people'
                url = '{}/{}/{{uuid}}'.format(url, name)
                return url.format(uuid=record.uuid)


try:
    import sqlalchemy as sa
except ImportError:
    pass
else:

    class FromSQLAlchemyHandler(ImportHandler):
        """
        Handler for imports for which the host data source is represented by a
        SQLAlchemy engine and ORM.
        """
        host_session = None

        def make_host_session(self):
            """
            Subclasses must override this to define the host database connection.
            """
            raise NotImplementedError

        def get_importer_kwargs(self, key, **kwargs):
            kwargs = super(FromSQLAlchemyHandler, self).get_importer_kwargs(key, **kwargs)
            kwargs.setdefault('host_session', self.host_session)
            return kwargs

        def begin_host_transaction(self):
            self.host_session = self.make_host_session()

        def rollback_host_transaction(self):
            self.host_session.rollback()
            self.host_session.close()
            self.host_session = None

        def commit_host_transaction(self):
            self.host_session.commit()
            self.host_session.close()
            self.host_session = None


    class ToSQLAlchemyHandler(ImportHandler):
        """
        Handler for imports which target a SQLAlchemy ORM on the local side.
        """
        session = None

        def make_session(self):
            """
            Subclasses must override this to define the local database connection.
            """
            raise NotImplementedError

        def get_importer_kwargs(self, key, **kwargs):
            kwargs = super(ToSQLAlchemyHandler, self).get_importer_kwargs(key, **kwargs)
            kwargs.setdefault('session', self.session)
            return kwargs

        def begin_local_transaction(self):
            self.session = self.make_session()

        def rollback_local_transaction(self):
            self.session.rollback()
            self.session.close()
            self.session = None

        def commit_local_transaction(self):
            self.session.commit()
            self.session.close()
            self.session = None
