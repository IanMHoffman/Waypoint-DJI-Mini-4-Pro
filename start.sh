#!/bin/bash
source /opt/render/project/.venv/bin/activate
exec gunicorn app:app
