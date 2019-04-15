def summarize_runs(headers):
    print("HH:MM:SS  plan_name  detectors      motors         exit_status")
    for h in headers:
        md = h.start
        print(f"{datetime.fromtimestamp(md['time']):%H:%M:%S}  "
              f"{md['plan_name']:11}"
              f"{','.join(md.get('detectors', [])):15}"
              f"{','.join(md.get('motors', [])):15}"
              f"{h.stop['exit_status']:15}")

# example usage:
summarize_runs(db(since=an_hour_ago))
