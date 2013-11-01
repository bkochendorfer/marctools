#!/usr/bin/env python
# coding: utf-8

from __future__ import print_function
import fnmatch
import hashlib
import luigi
import os
import random
import string
import subprocess
import tempfile

from timeit import default_timer
from colorama import Fore, Back, Style
from functools import wraps

import logging
logger = logging.getLogger('luigi-interface')

def dim(text):
    return Back.WHITE + Fore.BLACK + text + Fore.RESET + Back.RESET

def green(text):
    return Fore.GREEN + text + Fore.RESET

def red(text):
    return Fore.RED + text + Fore.RESET

def yellow(text):
    return Fore.YELLOW + text + Fore.RESET

def cyan(text):
    return Fore.CYAN + text + Fore.RESET

def magenta(text):
    return Fore.MAGENTA + text + Fore.RESET


class Timer(object):
    """ A timer as a context manager. """

    def __init__(self):
        self.timer = default_timer
        # measures wall clock time, not CPU time!
        # On Unix systems, it corresponds to time.time
        # On Windows systems, it corresponds to time.clock

    def __enter__(self):
        self.start = self.timer() # measure start time
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.end = self.timer() # measure end time
        self.elapsed_s = self.end - self.start # elapsed time, in seconds
        self.elapsed_ms = self.elapsed_s * 1000  # elapsed time, in milliseconds


def timed(method):
    @wraps(method)
    def timed(*args, **kwargs):
        with Timer() as timer:
            result = method(*args, **kwargs)
        klass = args[0].__class__.__name__
        fun = method.__name__

        msg = '[%s.%s] %0.5f' % (klass, fun, timer.elapsed_s)
        if timer.elapsed_s <= 10:
            logger.debug(green(msg))
        elif timer.elapsed_s <= 60:
            logger.debug(yellow(msg))
        else:
            logger.debug(red(msg))
        return result
    return timed

HOME = os.path.abspath(os.path.curdir)


def random_string(length=16):
    """
    Return a random string (upper and lowercase letters) of length `length`,
    defaults to 16.
    """
    return ''.join(random.choice(string.letters) for _ in range(length))


def random_tmp_path():
    """
    Return a random path, that is located under the system's tmp dir. This
    is just a path, nothing gets touched or created.
    """
    return os.path.join(tempfile.gettempdir(), 'tasktree-%s' % random_string())


class SplitMarc(luigi.Task):
    """
    Splits a MARC file.
    """

    filename = luigi.Parameter(default='test-tit.mrc')
    prefix = luigi.Parameter(default="test-tit-chunk.")

    @timed
    def run(self):
        cursor, i, offset, size, fileno = 0, 0, 0, 0, 0
        with open(self.filename) as handle:
            while True:
                if i % 1000000 == 0:
                    if i > 0:
                        outfile = os.path.join(HOME, '%s%08d' % (self.prefix, fileno))
                        with open(outfile, 'w') as output:
                            handle.seek(offset)
                            output.write(handle.read(size))
                            fileno += 1
                            offset += size
                            size = 0
                            print('wrote %s' % outfile)

                try:
                    first5 = handle.read(5)
                    if not first5:
                        raise StopIteration
                    if len(first5) < 5:
                        raise Exception('Invalid length: %s' % first5)
                    length = int(first5)
                    cursor += length
                    size += length
                    i += 1
                    handle.seek(cursor)
                except StopIteration:
                    break

            outfile = os.path.join(HOME, '%s%08d' % (self.prefix, fileno))
            with open(outfile, 'w') as output:
                handle.seek(offset)
                output.write(handle.read(size))
                print('wrote %s' % outfile)

        with self.output().open('w') as output:
            for fn in os.listdir('.'):
                if fnmatch.fnmatch(fn, '%s*' % self.prefix):
                    output.write('%s\n' % fn)


    def output(self):
        digest = hashlib.sha1(self.filename).hexdigest()
        return luigi.LocalTarget(os.path.join(HOME, 'splitfiles-%s' % digest))


# class Split(luigi.Task):

#     filename = luigi.Parameter(default='test-tit.mrc')

#     @timed
#     def run(self):
#         prefix = "test-tit-chunk."
#         chunksize = 1000000
#         command = """ yaz-marcdump -s %s -C %s %s > /dev/null """ % (
#             prefix, chunksize, self.filename)
#         print(command)
#         code = subprocess.call([command], shell=True)
#         if code == 0:
#             with self.output().open('w') as output:
#                 for filename in os.listdir('.'):
#                     if fnmatch.fnmatch(filename, '%s*' % prefix):
#                         output.write('%s\n' % filename)

#     def output(self):
#         digest = hashlib.sha1(self.filename).hexdigest()
#         return luigi.LocalTarget(os.path.join(HOME, 'splitfiles-%s' % digest))


class MarcToJSON(luigi.Task):
    """
    Convert a single Marc file to JSON.
    """
    filename = luigi.Parameter()

    @timed
    def run(self):
        stopover = random_tmp_path()
        command = "./marctojson %s > %s" % (self.filename, stopover)
        print(command)
        code = subprocess.call([command], shell=True)
        if code == 0:
            luigi.File(stopover).move(self.output().fn)

    def output(self):
        digest = hashlib.sha1(self.filename).hexdigest()
        return luigi.LocalTarget(os.path.join(HOME, '%s.json' % digest))


class MarcToJSONParallel(luigi.WrapperTask):
    """
    Take a file which contains a list of filenames and convert each of
    those in parallel.
    """
    filename = luigi.Parameter()

    def requires(self):
        task = SplitMarc(filename=self.filename)
        luigi.build([task], local_scheduler=True)
        with task.output().open() as handle:
            for line in handle:
                filename = line.strip()
                yield MarcToJSON(filename)

    def output(self):
        return self.input()


class MarcToJSONMerged(luigi.Task):
    """
    Merge a number of JSON files into one.
    """
    filename = luigi.Parameter()

    def requires(self):
        return MarcToJSONParallel(filename=self.filename)

    @timed
    def run(self):
        stopover = random_tmp_path()
        for target in self.input():
            command = """ cat %s >> %s """ % (target.fn, stopover)
            print(command)
            code = subprocess.call([command], shell=True)
            if not code == 0:
                raise RuntimeError('Could not concatenate files.')
        luigi.File(stopover).move(self.output().fn)

    def output(self):
        base, _ = os.path.splitext(self.filename)
        return luigi.LocalTarget(os.path.join(HOME, '%s.json' % base))


if __name__ == '__main__':
    luigi.run()