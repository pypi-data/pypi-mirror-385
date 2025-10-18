sample_query = """
SELECT org_id, usr_id_tkn as user_id, null as server_id, map('dummy',null
, CASE WHEN SUBSTR(LPAD(CONV(permissions1,10,2),32,'0'),32-0,1) = 1 THEN 'EmailSingle_Permission' ELSE 'dummy' END , CASE WHEN SUBSTR(LPAD(CONV(permissions1,10,2),32,'0'),32-0,1) = 1 THEN 'Y' END
, CASE WHEN SUBSTR(LPAD(CONV(permissions1,10,2),32,'0'),32-1,1) = 1 THEN 'EmailMass_Permission' ELSE 'dummy' END , CASE WHEN SUBSTR(LPAD(CONV(permissions1,10,2),32,'0'),32-1,1) = 1 THEN 'Y' END
, CASE WHEN SUBSTR(LPAD(CONV(permissions1,10,2),32,'0'),32-2,1) = 1 THEN 'My Permission' ELSE 'dummy' END , CASE WHEN SUBSTR(LPAD(CONV(permissions1,10,2),32,'0'),32-2,1) = 1 THEN 'Y' END
"""

import re

pattern = r"SUBSTR\(LPAD\(CONV\((\w+),10,2\),32,'0'\),32-(\d+),1\) = 1"
replacement = r"BITAND(\1, BITSHIFTLEFT(1, \2)) > 0"
converted_query = ((re.sub(pattern, replacement, sample_query)
                   .replace("server_id, map(", "server_id, object_construct_keep_null("))
                   .replace("ELSE 'dummy' END", "END"))

print(converted_query)