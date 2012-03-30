

# enable set_trace()
# Hack from http://www.morethanseven.net/2009/02/07/pdb-and-appengine.html

import sys
import pdb

def set_trace():
	for attr in ('stdin', 'stdout', 'stderr'):
		setattr(sys, attr, getattr(sys, '__%s__' % attr))
	pdb.set_trace()
