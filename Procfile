
# Web
web: gunicorn web_main:app

# Scheduled Tasks
send_daily:     bin/send_daily.py --prod
scale_web_up:   bin/scale_dynos.py -n 1 -t web
scale_web_down: bin/scale_dynos.py -n 0 -t web


