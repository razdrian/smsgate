from time import *
import threading


def general_setup():
    print 'General Setup has completed'


def general_quit():
    print 'General Quit has compelted'


def email_worker(email_event):
    # while not email_quit.isSet():
    while getattr(email_thread, "do_run", True):
        print 'email in working...'
        email_event.set()
        sleep(1)
        email_event.clear()


def sms_worker(sms_event):
    # while not sms_quit.isSet():
    while getattr(sms_thread, "do_run", True):
        print 'sms is working ...'
        sms_event.set()
        sleep(0.5)
        sms_event.clear()


def fs_worker(fs_event):
    # while not fs_quit.isSet():
    while getattr(fs_thread, "do_run", True):
        print 'fs in working...'
        fs_event.set()
        sleep(0.2)
        fs_event.clear()


email_event = threading.Event()
sms_event = threading.Event()
fs_event = threading.Event()

email_kill = threading.Event()
sms_kill = threading.Event()
fs_kill = threading.Event()

email_thread = threading.Thread(name='email_thread', target=email_worker, args=(email_event,))
# email_thread.setDaemon(True)
sms_thread = threading.Thread(name='sms_thread', target=sms_worker, args=(sms_event,))
# sms_thread.setDaemon(True)
fs_thread = threading.Thread(name='fs_thread', target=fs_worker, args=(fs_event,))
# fs_thread.setDaemon(True)





if __name__ == "__main__":
    # start here
    general_setup()

    email_thread.start()
    sms_thread.start()
    fs_thread.start()

    # dummy here
    sleep(2)

    email_event.set()
    email_event.wait()
    email_thread.join(0)

    sms_event.set()
    sms_event.wait()
    sms_thread.join(0)

    fs_event.set()
    fs_event.wait()
    fs_thread.join(0)

    email_event.clear()
    sms_event.clear()
    fs_event.clear()

    # problema e ca threadurile ramai alive
    print(sms_thread.isAlive())
    print(email_thread.isAlive())
    print(fs_thread.isAlive())

    general_quit()
