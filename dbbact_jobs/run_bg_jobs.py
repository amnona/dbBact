#!/usr/bin/env python

import argparse
import sys
import os
import time
from datetime import datetime
from pathlib import Path
import subprocess

from dbbact_server.utils import debug, SetDebugLevel

__version__ = "0.1"


commands = {'update_seq_taxonomy': './update_seq_taxonomy.py',
			'update_seq_hash': './update_seq_hash.py',
			'update_silva': './update_whole_seq_db.py -w SILVA -f silva-small.fa',
			'update_gg': './update_whole_seq_db.py -w greengenes -f greengenes-small.fa',
			'update_seq_counts': './update_seq_counts.py',}


def get_time_to_tomorrow(hour, minute=0):
	x = datetime.today()
	y = x.replace(day=x.day + 1, hour=hour, minute=minute, second=0, microsecond=0)
	delta_t = y - x
	secs = delta_t.seconds + 1
	debug(1, '%d seconds until tomorrow %d:%d:00' % (secs, hour, minute))
	return secs


def isFileExist(fileName):
	my_file = Path(fileName)
	if my_file.is_file():
		# file exists
		return True
	return False


def removeFile(file_name):
	try:
		os.remove(file_name)
	except OSError:
		pass


def run_bg_jobs(port, host, database, user, password, single_update=False, command_params=None):
	debug(3, 'run_bg_jobs started')
	if single_update:
		debug(2, 'running single_update and quitting')
	stop_file = "stop.run_bg_jobs"
	removeFile(stop_file)
	while not isFileExist(stop_file):
		for idx, (ccommand, cbash) in enumerate(commands.items()):
			if command_params is not None:
				for cpar in command_params:
					cpar_split = cpar.split(':')
					if len(cpar_split) != 3:
						debug(5, 'command parameters %s should be command:param_name:value' % cpar)
						continue
					if ccommand == cpar_split[0]:
						cbash += ' --%s %s' % (cpar_split[1], cpar_split[2])
			cbash += ' --port %s --database %s --user %s --password %s' % (port, database, user, password)
			if host is not None:
				cbash += ' --host %s' % host
			debug(2, 'running command %s (%d / %d)' % (ccommand, idx + 1, len(commands)))
			debug(1, cbash)
			with open('log-%s.txt' % ccommand, 'a') as logfile:
				start_time = time.time()
				res = subprocess.call(cbash, shell=True, stderr=logfile, stdout=logfile)
				end_time = time.time()
				if res != 0:
					debug(5, 'command %s failed. error code: %s' % (ccommand, res))
				else:
					debug(2, 'command exited ok. running time: %r sec' % (end_time - start_time))
		if single_update:
			debug(3, 'single_update - finished')
			break
		debug(2, 'sleeping until tomorrow')
		time.sleep(get_time_to_tomorrow(23, 0))
		debug(2, 'good morning')
	debug(3, 'run_bg_jobs finished')


def main(argv):
	parser = argparse.ArgumentParser(description='run_bg_jobs version %s.' % __version__, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	parser.add_argument('--port', help='postgres port', default=5432, type=int)
	parser.add_argument('--host', help='postgres host', default=None)
	parser.add_argument('--database', help='postgres database', default='dbbact')
	parser.add_argument('--user', help='postgres user', default='dbbact')
	parser.add_argument('--password', help='postgres password', default='magNiv')
	parser.add_argument('--debug-level', help='debug level (1 for debug ... 9 for critical)', default=2, type=int)
	parser.add_argument('--single-update', help='update once and quit', action='store_true')
	parser.add_argument('-p', '--command-params', help='specific command parameters. command and parameter name separated by : (i.e. update_silva:wholeseq-file:SILVA.fa). can use flag more than once', action='append')
	args = parser.parse_args(argv)

	SetDebugLevel(args.debug_level)
	run_bg_jobs(port=args.port, host=args.host, database=args.database, user=args.user, password=args.password, single_update=args.single_update, command_params=args.command_params)


if __name__ == "__main__":
	SetDebugLevel(1)
	main(sys.argv[1:])
