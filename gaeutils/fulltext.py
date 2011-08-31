import re
import logging

from google.appengine.ext import db

class FullTextSearchException( Exception ):
	pass

def combinations( list, max_size = None ):
	""" 
	All subcombinations of (size) elements from list. If size is not given 
	then it will counted as len( list ). For example 
	>> combinations( [ 'a', 'b', 'c' ] )
	[[], ['a'], ['b'], ['a', 'b'], ['c'], ['a', 'c'], ['b', 'c'], ['a', 'b', 'c']]
	>> combinations( [ 'a', 'b', 'c' ], 2 )
	[[], ['a'], ['b'], ['a', 'b'], ['c'], ['a', 'c'], ['b', 'c']]
	"""
	result = []
	if not list or max_size == 0:
		return result
	if not max_size:
		max_size = len( list )
	for i in range( 2 ** len( list ) ):
		temp = i
		combination = []
		for j in range( len( list ) ):
			modulo_2 = temp % 2
			temp = temp / 2
			if modulo_2:
				combination.append( list[ j ] )
		if len( combination ) <= max_size:
			result.append( combination )
	return result

def parse_words( string, min_word_len = 3 ):
	""" 
	parse words from string, returns lowercased words with at least 
	min_word_len chars 
	"""
	result = []
	if not string:
		return result
	words = re.findall( '([^\s\!"#$%&/\\(\)\\.,:;-_\+\*\?=<>]+)', string.lower() )
	if not words:
		return result
	return words

def build_gql( table_name, words, words_column = 'search_words' ):
	if not words:
		raise FullTextSearchException( 'Invalid words for full text search %s' % words )
	expressions = []
	n = 1
	for word in words:
		expressions.append( 'search_words = :%s' % n )
		n += 1
	return ( 'select * from %s where ' % table_name )+ ' and '.join( expressions )

def cmp_list_by_row_length( row1, row2 ):
	""" used for sorting (in list.sort( cmp_function )) a list of lists by row length """
	len1 = 0 if not row1 else len( row1 )
	len2 = 0 if not row2 else len( row2 )
	if len1 < len2:
		return -1
	elif len1 > len2:
		return 1
	return 0

def search( \
		table_name_or_class, \
		words, words_column = 'search_words', \
		min_words = 1, \
		limit = 100, \
		conditions = {} ):
	# TODO: doc
	result = []

	if not words:
		return result

	if isinstance( table_name_or_class, type ):
		table_name = table_name_or_class.__name__
	else:
		table_name = table_name_or_class

	word_combinations = combinations( words )
	word_combinations.sort( cmp_list_by_row_length )
	while len( word_combinations ) > 0:
		logging.debug( word_combinations )
		
		words = word_combinations.pop()
		if len( words ) > 0 and len( words ) >= min_words:
			logging.debug( 1 )
			gql = build_gql( table_name, words )

			args = words

			if conditions:
				for key, value in conditions.items():
					gql += ' and %s = :%s' % ( key, 1 + len( args ) )
					args.append( conditions[ key ] )

			logging.debug( gql )

			results = db.GqlQuery( gql, *words )
			for row in results:
				result.append( row )
				if len( result ) >= limit:
					return result
	return result

if __name__ == '__main__':
	c1 = combinations( [ 'a', 'b', 'c' ] )
	print len( c1 )
	assert( len( c1 ) == 2 ** 3 )
	assert( [ 'a', 'b', 'c' ] in c1 )
	assert( [ 'b', 'c' ] in c1 )
	assert( [ 'c' ] in c1 )
	assert( [] in c1 )

	c2 = combinations( [ 'a', 'b', 'c' ], 2 )
	assert( not [ 'a', 'b', 'c' ] in c2 )
	assert( [ 'b', 'c' ] in c2 )
	assert( [ 'c' ] in c2 )
	assert( [] in c2 )

	sorted = combinations( [ 'a', 'b', 'c' ] )
	sorted.sort( cmp_list_by_row_length )
	assert sorted[ 0 ] == []
	assert sorted[ -1 ] == [ 'a', 'b', 'c' ]

	words = parse_words( 'dsajkld we/2jk213jkl3(jdsalkdjk)dsajkldkjsal$%"!dskjld%%&/576567567 aa	bbbbb' )
	assert words == ['dsajkld', 'we', '2jk213jkl3', 'jdsalkdjk', 'dsajkldkjsal', 'dskjld', '576567567', 'aa', 'bbbbb']
	assert parse_words( '' ) == []
	assert parse_words( None ) == []

	try:
		build_gql( 'table', None )
		assert None
	except FullTextSearchException, e:
		assert True

	assert build_gql( 'Advertisment', [ 'a', 'b', 'c' ] ) == 'select * from table_name where search_words = :1 and search_words = :2 and search_words = :3'

	print search( 'table', [ 'aaaaa', 'bbb', 'xxx' ] )

	print 'OK'
