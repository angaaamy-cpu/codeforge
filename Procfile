# Procfile - For Heroku/Dokku/Railway
# ===================================
# Web process for CodeForge

web: gunicorn src.app:app --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 120 --access-logfile - --error-logfile -
