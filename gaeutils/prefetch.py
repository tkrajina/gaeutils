from google.appengine.ext import db

def prefetch_references( entities, *properties ):
	""" 
	Will prefetch references to other objects for n:1 relation. Prefetched references
	may be retrieved with _prefetched sufix. 

	See README.txt for code examples.
	"""
	if not entities:
		return []
	
	result = []
	for entity in entities:
		result.append(entity)

	if not properties:
		return result

	count = 0

	for property in properties:
		count += 1
		if count > 100:
			logging.warn( 'Prefetched more than 100 items!' )
		property_name = "%s_prefetched" % property.name
		property_key_name = "%s_prefetched_key" % property.name
	
		keys = []
		for entity in result:
			property_key = property.get_value_for_datastore( entity )
			if property_key:
				keys.append( str( property_key ) )
				setattr( entity, property_key_name, str( property_key ) )
			else:
				setattr( entity, property_key_name, None )
	
		_properties = db.get( set( keys ) )
		properties = {}
		for property in _properties:
			properties[ str( property.key() ) ] = property
	
		for entity in result:
			key = getattr( entity, property_key_name )
			setattr( entity, property_name, None )
			if properties.has_key( key ):
				setattr( entity, property_name, properties[ key ] )

	return result
