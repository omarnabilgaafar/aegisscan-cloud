import sqlite3
import secrets
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / 'scanner.db'

def run():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("INSERT OR IGNORE INTO organizations (name, plan) VALUES (?,?)", ('Aegis Demo Labs', 'Professional'))
    org_id = cur.execute("SELECT id FROM organizations WHERE name=?", ('Aegis Demo Labs',)).fetchone()[0]
    cur.execute(
        "INSERT OR IGNORE INTO users (username,email,password_hash,role,plan,organization_id) VALUES (?,?,?,?,?,?)",
        ('demo_admin', 'demo@aegisscan.local', 'demo-hash', 'admin', 'Professional', org_id),
    )
    user_id = cur.execute("SELECT id FROM users WHERE username=?", ('demo_admin',)).fetchone()[0]
    key = 'ag_demo_' + secrets.token_hex(12)
    cur.execute("INSERT OR IGNORE INTO api_keys (api_key,user_id,organization_id,label) VALUES (?,?,?,?)", (key, user_id, org_id, 'Seeded Demo Key'))

    seeds = [
        ('https://demo.aegisscan.local/portal', [
            ('Potential SQL Injection Surface','Critical','https://demo.aegisscan.local/portal/login','Dynamic query parameters appear to reach authentication logic without strong parameterization.'),
            ('Possible Database Error Disclosure','Medium','https://demo.aegisscan.local/portal/login','Verbose SQL error fragments were observed during invalid credential submission flows.'),
            ('Missing Security Header','Low','https://demo.aegisscan.local/portal','Content-Security-Policy header is missing from authenticated responses.'),
            ('Missing CSRF Protection','High','https://demo.aegisscan.local/portal/profile/update','State-changing profile update form does not show anti-CSRF token validation.'),
        ]),
        ('https://shop.aegis-demo.local', [
            ('Potential Stored/Reflected XSS Surface','High','https://shop.aegis-demo.local/reviews/new','User-supplied review content is reflected back into the page without clear output encoding.'),
            ('Potential Reflected XSS Surface','Medium','https://shop.aegis-demo.local/search?q=test','Search results reflect query parameters into HTML context.'),
            ('Missing Security Header','Medium','https://shop.aegis-demo.local/checkout','X-Frame-Options header missing on checkout route.'),
            ('Missing Security Header','Low','https://shop.aegis-demo.local','Referrer-Policy header missing on the main storefront.'),
        ]),
        ('https://files.aegis-demo.local', [
            ('Potential Directory Traversal Surface','High','https://files.aegis-demo.local/download?file=report.pdf','Download endpoint accepts file path values that may allow traversal sequences.'),
            ('Missing Security Header','Medium','https://files.aegis-demo.local/download','X-Content-Type-Options header missing on file-serving responses.'),
            ('Possible Database Error Disclosure','Low','https://files.aegis-demo.local/audit','Unhandled exceptions appear to leak backend implementation details in logs and responses.'),
        ]),
        ('https://api.aegis-demo.local/v1', [
            ('Potential SQL Injection Surface','High','https://api.aegis-demo.local/v1/reports?id=12','Query-style identifier handling suggests unsanitized backend database access.'),
            ('Missing CSRF Protection','Medium','https://api.aegis-demo.local/v1/account/email','Authenticated email change workflow lacks anti-forgery controls in web context.'),
            ('Missing Security Header','Low','https://api.aegis-demo.local/v1/docs','Strict-Transport-Security header missing from API documentation endpoint.'),
        ]),
        ('https://admin.aegis-demo.local', [
            ('Potential Stored/Reflected XSS Surface','Critical','https://admin.aegis-demo.local/announcements','Administrative announcement editor may store unsafe HTML that renders to privileged users.'),
            ('Potential Directory Traversal Surface','Medium','https://admin.aegis-demo.local/logs/view?name=app.log','Log viewer path handling appears insufficiently normalized.'),
            ('Possible Database Error Disclosure','Medium','https://admin.aegis-demo.local/users/import','Import validation exposes backend table names during malformed upload tests.'),
            ('Missing Security Header','Low','https://admin.aegis-demo.local','Permissions-Policy header not present on administrative interface.'),
        ]),
    ]

    inserted_scans = 0
    inserted_findings = 0
    for target, findings in seeds:
        if cur.execute('SELECT 1 FROM scans WHERE target_url=? LIMIT 1', (target,)).fetchone():
            continue
        cur.execute('INSERT INTO scans (target_url,total_findings,error_message,user_id,organization_id) VALUES (?,?,?,?,?)', (target, len(findings), None, user_id, org_id))
        scan_id = cur.lastrowid
        inserted_scans += 1
        for vuln_type, severity, url, description in findings:
            cur.execute('INSERT INTO vulnerabilities (scan_id,vuln_type,severity,url,description) VALUES (?,?,?,?,?)', (scan_id, vuln_type, severity, url, description))
            inserted_findings += 1

    conn.commit()
    conn.close()
    print(f'Seed complete: {inserted_scans} scans, {inserted_findings} vulnerabilities added.')

if __name__ == '__main__':
    run()
