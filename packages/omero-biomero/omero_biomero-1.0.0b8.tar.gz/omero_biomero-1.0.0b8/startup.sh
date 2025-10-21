#!/bin/bash
# Startup script for OMERO.web with OMERO.biomero. Prevents the container from exiting immediately after omero server restart.

set -eu

# Ensure UTF-8 locale so Click can print without errors
export LANG=C.UTF-8
export LC_ALL=C.UTF-8

export PATH="/opt/omero/web/venv3/bin:$PATH"
python=/opt/omero/web/venv3/bin/python
omero=/opt/omero/web/venv3/bin/omero

$python /startup/44-create_forms_user.py
bash /startup/45-fix-forms-config.sh
$python /startup/50-config.py
bash /startup/60-default-web-config.sh
bash /startup/98-cleanprevious.sh

# Also remove any stale pid just before start
rm -f /opt/omero/web/OMERO.web/var/django.pid || true

cd /opt/omero/web
echo "Starting OMERO.web in the background"
# Call CLI directly
exec "$omero" web start