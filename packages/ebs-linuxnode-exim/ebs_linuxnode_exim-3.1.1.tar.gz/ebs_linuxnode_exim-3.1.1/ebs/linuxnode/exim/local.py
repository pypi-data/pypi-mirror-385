

import os
import shutil
from collections import namedtuple

from twisted import logger
from twisted.internet.threads import deferToThread
from twisted.internet.defer import succeed, fail
from twisted.internet.defer import inlineCallbacks, returnValue


ExportSpec = namedtuple(
    'ExportSpec', ["source", "destination", "no_clear", "writer", "contexts", "delete_source"],
    defaults=['[id]', False, None, ['all'], False]
)


ImportSpec = namedtuple(
    'ImportSpec', ["destination", "source", "no_clear", "writer", "contexts", "delete_source"],
    defaults=['[id]', False, None, ['startup']]
)


class ChannelNotFound(Exception):
    pass


class ChannelNotAuthenticated(Exception):
    pass


class LocalEximManager(object):
    def __init__(self, actual):
        self._actual = actual
        self._log = None
        self._exports = {}
        self._imports = {}

    @property
    def actual(self):
        return self._actual

    @property
    def log(self):
        if not self._log:
            self._log = logger.Logger(namespace="exim.local", source=self)
        return self._log

    def register_export(self, tag, spec):
        tag = tag.upper()
        if tag not in self._exports.keys():
            self._exports[tag] = []
        if isinstance(spec, str):
            spec = ExportSpec(spec)
        self.log.debug("Registering '{}' Export from '{}'".format(tag, spec.source))
        self._exports[tag].append(spec)

    def register_import(self, tag, spec):
        tag = tag.upper()
        if tag in self._imports.keys():
            self.log.warn("Registered import '{}' with tag '{}' "
                          "is being overwritten by '{}'"
                          "".format(self._imports[tag], tag, spec))
        if isinstance(spec, str):
            spec = ImportSpec(spec)
        self.log.debug("Registering '{}' Import from '{}'".format(tag, spec.destination))
        self._imports[tag] = spec

    def install(self):
        self.log.info("Initializing Local Export/Import Infrastructure")

    @inlineCallbacks
    def clear_directory(self, directory):
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    yield deferToThread(shutil.rmtree(file_path))
            except Exception as e:
                self.log.warn('Failed to delete %s. Reason: %s' % (file_path, e))

    @inlineCallbacks
    def _remove_directory(self, directory):
        yield deferToThread(shutil.rmtree, directory)

    @inlineCallbacks
    def _copy_tree(self, src, dest):
        yield self.actual._shell_execute(['cp', '-rf', src, dest], lambda _: True)

    @inlineCallbacks
    def _execute_export(self, channel, tag, spec):
        target_path = os.path.join(channel, tag)
        if not os.path.exists(target_path):
            return False
        if not os.path.exists(spec.source):
            return False
        self.actual.signal_exim_action_start(tag, 'export')
        self.log.info("Executing Export {}".format(spec))
        if spec.destination:
            if spec.destination == '[id]':
                destination = self.actual.id
            else:
                destination = spec.destination
            destination = destination.upper()
            target_path = os.path.join(target_path, destination)
        if not os.path.exists(target_path):
            os.makedirs(target_path, exist_ok=True)
        path_part = os.path.basename(spec.source)
        target_path = os.path.join(target_path, path_part)
        if not spec.no_clear:
            if os.path.exists(target_path):
                if os.path.isdir(target_path):
                    yield self._remove_directory(target_path)
                else:
                    os.unlink(target_path)
        if spec.writer:
            yield spec.writer(target_path)
        else:
            yield self._copy_tree(spec.source, target_path)
        if spec.delete_source:
            yield self._remove_directory(spec.source)
        return True


    @inlineCallbacks
    def _execute_import(self, channel, tag, spec):
        source_path = os.path.join(channel, tag)
        if not os.path.exists(source_path):
            return False
        if spec.source:
            if spec.source == '[id]':
                source = self.actual.id
            elif spec.source == '[id]?':
                lsource = self.actual.id
                lsource = lsource.upper()
                if os.path.exists(os.path.join(source_path, lsource)):
                    source = self.actual.id
                else:
                    source = None
            else:
                source = spec.source
            if source:
                source = source.upper()
                source_path = os.path.join(source_path, source)
        if not os.path.exists(source_path):
            return False
        self.actual.signal_exim_action_start(tag, 'import')
        self.log.info("Executing Import {}".format(spec))
        if spec.writer:
            yield spec.writer(source_path)
        else:
            if not spec.no_clear:
                if os.path.exists(spec.destination):
                    if os.path.isdir(spec.destination):
                        yield self._remove_directory(spec.destination)
                    else:
                        os.unlink(spec.destination)
            yield self._copy_tree(source_path, spec.destination)
        if spec.delete_source:
            yield self._remove_directory(source_path)
        return True

    @inlineCallbacks
    def execute(self, channel, context=None):
        self.log.info("Executing Local Exports")
        for tag, specs in self._exports.items():
            for spec in specs:
                if context in spec.contexts or 'all' in spec.contexts:
                    yield self._execute_export(channel, tag, spec)
            self.actual.signal_exim_action_done(tag, 'export')
        self.log.info("Executing Local Imports")
        for tag, spec in self._imports.items():
            if context in spec.contexts or 'all' in spec.contexts:
                yield self._execute_import(channel, tag, spec)
            self.actual.signal_exim_action_done(tag, 'import')

    def _authenticate_channel(self, path):
        if not os.path.exists(os.path.join(path, '.ebs')):
            return fail(ChannelNotAuthenticated())
        return succeed(path)

    @inlineCallbacks
    def find_authenticated_channel(self):
        candidates = [self.actual.config.exim_local_mountpoint]
        for candidate in candidates:
            if not os.path.exists(candidate):
                self.log.debug("Channel '{}' not found.".format(candidate))
                continue
            try:
                yield self._authenticate_channel(candidate)
            except ChannelNotAuthenticated:
                self.log.debug("Channel '{}' not authenticated.".format(candidate))
                continue
            returnValue(candidate)
        returnValue(None)

    @inlineCallbacks
    def trigger(self, context):
        if not self.actual.config.exim_local_enabled:
            return
        self.log.info("Triggering Export/Import")
        channel = yield self.find_authenticated_channel()
        if not channel:
            self.log.info("No authenticated channel found. Not executing EXIM.")
            return
        self.log.info("Found Authenticated Channel '{}'. Executing EXIM.".format(channel))
        self.actual.busy_set()
        yield self.execute(channel, context=context)
        self.actual.busy_clear()
        self.log.info("Finished Export/Import")
