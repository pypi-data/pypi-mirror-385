def slowly_print(text, delay):
    import sys
    import time
    for char in text:
        sys.stdout.write(char)
        sys.stduot.flush()
        time.sleep(delay)

