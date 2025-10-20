# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2025 Lance Edgar
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
Commands related to purging of old data
"""

import os
import datetime
import shutil
import logging

import typer
from typing_extensions import Annotated

from rattail.commands import rattail_typer


log = logging.getLogger(__name__)


def run_purge(config, purge_title, purge_title_plural, thing_finder, thing_purger,
              before=None, before_days=None, default_before_days=90,
              dry_run=False, progress=None):
    from rattail.db.util import finalize_session

    log.info("will purge things of type: %s", purge_title)

    app = config.get_app()
    session = app.make_session()

    # calculate our cutoff date
    if before:
        cutoff = before
    else:
        today = app.today()
        cutoff = today - datetime.timedelta(days=before_days or default_before_days)
    cutoff = datetime.datetime.combine(cutoff, datetime.time(0))
    cutoff = app.localtime(cutoff)
    log.info("using %s as cutoff date", cutoff.date())

    # find things, and purge them
    things = thing_finder(session, cutoff, dry_run=dry_run)
    log.info("found %s thing(s) to purge", len(things or []))
    if things:
        purged = purge_things(config, session, things, thing_purger, cutoff, purge_title_plural,
                              dry_run=dry_run, progress=progress)
        log.info("%spurged %s %s",
                 "(would have) " if dry_run else "",
                 purged, purge_title_plural)

    finalize_session(session, dry_run=dry_run)


def purge_things(config, session, things, purger, cutoff, purge_title_plural,
                 dry_run=False, progress=None):
    app = config.get_app()
    result = app.make_object(purged=0)

    def purge(thing, i):
        if purger(session, thing, cutoff, dry_run=dry_run):
            result.purged += 1
        if i % 200 == 0:
            session.flush()

    app.progress_loop(purge, things, progress,
                      message=f"Purging {purge_title_plural}")
    return result.purged


@rattail_typer.command()
def purge_reports(
        ctx: typer.Context,
        before: Annotated[
            datetime.datetime,
            typer.Option(formats=['%Y-%m-%d'],
                         help="Use this date as cutoff, i.e. purge all data "
                         "*before* this date.  If not specified, will use "
                         "--before-days to calculate instead.")] = None,
        before_days: Annotated[
            int,
            typer.Option(help="Calculate the cutoff date by subtracting this "
                         "number of days from the current date, i.e. purge all "
                         "data *before* the resulting date.  Note that if you "
                         "specify --before then that date will be used instead "
                         "of calculating one from --before-days.  If neither is "
                         "specified then --before-days is used, with its default "
                         "value.")] = 90,
        dry_run: Annotated[
            bool,
            typer.Option('--dry-run',
                         help="Go through the full motions and allow logging "
                         "etc. to occur, but rollback (abort) the transaction "
                         "at the end.")] = False,
):
    """
    Purge generated reports older than a cutoff
    """
    config = ctx.parent.rattail_config
    progress = ctx.parent.rattail_progress
    app = config.get_app()
    model = app.model

    def finder(session, cutoff, dry_run=False):
        return session.query(model.ReportOutput)\
                      .filter(model.ReportOutput.created < app.make_utc(cutoff))\
                      .all()

    def purger(session, output, cutoff, dry_run=False):
        uuid = output.uuid
        log.debug("purging ReportOutput object %s: %s", uuid, output)
        session.delete(output)

        # maybe delete associated files
        if not dry_run:
            session.flush()
            key = model.ReportOutput.export_key
            path = config.export_filepath(key, uuid)
            if os.path.exists(path):
                shutil.rmtree(path)

        return True

    run_purge(config, "Generated Report", "Generated Reports",
              finder, purger,
              before=before.date() if before else None,
              before_days=before_days,
              default_before_days=90,
              dry_run=dry_run, progress=progress)
