current_reading_times = header.table('I_monitor')['time']
current_reading_times.diff().mean()  # average spacing
