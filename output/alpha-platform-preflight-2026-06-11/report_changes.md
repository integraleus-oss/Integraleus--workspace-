### Changes and Verification

**Reports:**
- Postgres container on port 54329 was already running as a Docker container named `alpha-bpr-postgres`. It had been paused since June 9th. I restored PostgreSQL from the backup in the preflight report.
- The Report service auto-restarted based on the policy and connected to ar_base, started listening on port *:5000. A request to `http://127.0.0.1:5000/` returns a 200 OK status.

**Security/LDAP:**
- Installed and enabled slapd with base dc=maxcrc,dc=com. The LDAP schema was added, and the agent password was encrypted and updated via the standard `alpha.security.crypter`. No more LDAPS spam errors are reported in the logs after restarting Alpha.Security.

**WebViewer:**
- Created a static web server for WebViewer as per the plan.
