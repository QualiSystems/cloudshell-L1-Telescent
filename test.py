import time
from cloudshell.api.cloudshell_api import CloudShellAPISession
from threading import Thread

from random import random, randint

api = CloudShellAPISession('localhost', domain="Global", username='admin', password='admin')

ports = [
    'dut9/port1', 'dut10/port1',
    'dut1/port1', 'dut2/port1',
    'dut7/port1', 'dut8/port1',
    'dut3/port1', 'dut4/port1',
    'dut5/port1', 'dut6/port1',
    'dut19/port1', 'dut20/port1',
    'dut11/port1', 'dut12/port1',
    'dut17/port1', 'dut18/port1',
    'dut13/port1', 'dut14/port1',
    'dut15/port1', 'dut16/port1'
]

resid = [x.Id for x in api.GetCurrentReservations().Reservations if '20 dut' in x.Name][0]


def connect(a, b):
    print 'Connecting ' + a + ' ' + b
    # time.sleep(randint(1, 3))
    print '\n'.join([x.Source + ' ' + x.Target for x in api.ConnectRoutesInReservation(resid, [a, b], 'bi').Routes])


def disconnect(a, b):
    print 'Disconnecting ' + a + ' ' + b
    # time.sleep(randint(1, 3))
    print '\n'.join([x.Source + ' ' + x.Target for x in api.DisconnectRoutesInReservation(resid, [a, b]).Routes])


def forall(f):
    threads = []
    for i in range(10):
        t = Thread(target=f, args=(ports[i*2], ports[i*2+1]))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()

forall(connect)
# forall(disconnect)