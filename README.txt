This module consists of 3 submodules:
- fulltext -- for fulltext search (deprecated because Google announced its own fulltext API)
- geo -- for queries on geocoded data
- prefetch -- pereftching 1:n relations

geo module
==========

TODO

prefetch module
===============

Example code:

import gaeutils.prefetch as mod_prefetch

class User:
	...

class Track:
	...
	user = mod_db.ReferenceProperty( User )
	...

# a list of n tracks
tracks = ...

# Now, if you need to query all users for tracks -- without prefetching you'll
# need n queries on datastore. With prefetching:

tracks = mod_prefetch.prefetch_references( tracks, Track.user )

for track in tracks:
	# DO NOT user track.user to retrieve the user, this would result in
	# another datastore query, use this one:
	user = track.user_preftched
	...
