from pathlib import Path
import re

env_path = Path(__file__).parent / '.env'
text = env_path.read_text()
m = re.search(r'DEMO_MODE=(.*)', text)
current = m.group(1).strip().lower() if m else 'true'
new = 'false' if current in {'1', 'true', 'yes', 'on'} else 'true'
if m:
    text = re.sub(r'DEMO_MODE=.*', f'DEMO_MODE={new}', text)
else:
    text += '\nDEMO_MODE=' + new + '\n'
env_path.write_text(text)
print(f'DEMO_MODE set to {new}')
