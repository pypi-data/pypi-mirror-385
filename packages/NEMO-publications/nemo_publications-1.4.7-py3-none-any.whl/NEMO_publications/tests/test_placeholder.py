# Potential tests to write
# Cannot overwrite metadata (using same DOI with different case)
# Searching DOI
# 	If DOI exists in DB use the one in DB
# 	If DOI doesn't exist in DB query doi.org
# 	If DOI doesn't exist in doi.org or incomplete metadata, return the metadata edit form
# Publication data
# 	Cannot add an empty entry
# 	Cannot add a project that the user is not a part of
# 	Cannot edit entry that does not belong to user
# 	Cannot delete entry that does not belong to user
# API
# Publication ViewSet
# 	Check that all params work together to return the right elements from the db
# Publication metadata (POST)
# 	If DOI exists in DB use the one in DB
# 	If DOI doesn't exist in DB query doi.org
# 	If DOI doesn't exist in doi.org or incomplete metadata, use the rest of the data in the query
# Publication metadata Update (POST)
# 	Check Operation unsupported
