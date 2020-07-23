
import re


result = ' * 66 vty 11  test     dile     00:00:00 '
vty_id = re.search(r'vty (.*) test', result).group(1).strip()
print(vty_id)