import datetime
date_string = '2026-11-8'
date = datetime.datetime.strptime(date_string, "%Y-%m-%d")
print(date)


date = datetime.datetime.strptime(date_string, "%Y-%m-%d")
furl = f'{date.strftime("%Y-%m-%dT%H:%M:%S%Z")} '
print(furl)