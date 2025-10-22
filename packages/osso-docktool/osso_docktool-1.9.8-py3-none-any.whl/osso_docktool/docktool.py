from __future__ import print_function

from datetime import datetime
from warnings import warn
from signal import SIGUSR1, signal
from socket import AF_INET, SOCK_STREAM, socket
import argparse
import os
from pathlib import Path
import traceback
import subprocess
import sys

from . import settings
from .disksampler import DiskSampler
from .hdddock import BaseStorageDevice
from .inventoryrestclient import InventoryRESTClient
from .labelprinterapiclient import get_labelprinter


S_UNSET = '(unset)'


class Inventory:
    def __init__(self, inventory_rest_client, hdd_id):
        self._client = inventory_rest_client
        self._hdd_id = hdd_id
        self.flush()

    def flush(self):
        self._data = self._client.get_hdd(self._hdd_id)[0]

    @property
    def id(self):
        return self._data['id']

    @property
    def tag_uid(self):
        return self._data['tag_uid']

    @property
    def bay(self):
        return self._data['bay']

    @property
    def current_owner(self):
        return (self._data.get('current_owner') or {}).get('name')

    @property
    def current_health_status(self):
        return (self._data.get('current_health') or {}).get('status')


class ActionInterrupt(Exception):
    pass


class SymlinkNotFound(Exception):
    pass


class DeviceManager(object):
    def __init__(self, hdd_dock, hdd_id, inventory_rest_client,
                 author, location):
        self._hdd_dock = hdd_dock
        self._hdd_id = hdd_id
        self._inventory_rest_client = inventory_rest_client
        self._author = author
        self._location = location

    def show_summary(self, print_data):
        do_print(print_data, self._hdd_dock)

    def show_commands(self):
        erase_methods = self._hdd_dock.get_erase_methods()
        next_erase_method = 0

        print('')
        print('Inventory-url: {}'.format(
            self._inventory_rest_client.get_hdd_url(self._hdd_id)))
        print('')
        print('Possible actions:')
        print('1. Change owner')
        print('2. Reprint label')
        print('3. Quick erase')
        if len(erase_methods) > 1:
            print('4. Secure erase ({})'.format(
                erase_methods[next_erase_method].name))
            next_erase_method += 1
        print('5. Change server bay')
        print('6. Change health status')
        print('7. Print health label')
        print('8. Secure erase ({})'.format(
            erase_methods[next_erase_method].name))
        print('D. Dispose HDD in security container')
        print('L. Enable the locate LED')
        print('P. Show current info/status (again)')

        print('')
        print('9. Quit + EJECT (^C to skip eject)')

    def _set_status(self, status, extra_info):
        self._inventory_rest_client.add_status(
            self._hdd_id, status=status, extra_info=extra_info)

    def _set_health(self, title):
        # title = 'SECURE ERASED' or ...
        health = (
            'OK' if self._hdd_dock.hwdata.wear_health_percent >= 100
            else '{}%'.format(self._hdd_dock.hwdata.wear_health_percent))
        health_status = f'health {health} - {title}'
        self.set_health(health_status)

    def set_health(self, health_status):
        self._inventory_rest_client.add_health_status(
            self._hdd_id, status=health_status,
            extra_info='--{}'.format(self._author))

    def set_health_with_wear(self, title):
        self._set_health(title)

    def quick_erase(self):
        print('Start quick wiping')
        self._hdd_dock.quick_erase()
        self._set_status('QUICK_WIPED', 'Quick wiped at {} --{}'.format(
            self._location, self._author))
        try:
            self._hdd_dock.flush()
        finally:
            self._set_health('QUICK WIPED')
        print('Disk/ssd quick wiped')

    def best_erase(self):
        erase_method = self._hdd_dock.get_erase_methods()[0]
        self._erase(erase_method)

    def second_best_erase(self):
        erase_methods = self._hdd_dock.get_erase_methods()
        if len(erase_methods) > 1:
            erase_methods.pop(0)
        self._erase(erase_methods[0])

    def _erase(self, erase_method):
        if erase_method.type == 'builtin':
            return self._erase_with_status(erase_method)
        if erase_method.type == 'manual':
            print('Secure disk wipe chosen. Please wait as this will '
                  'take a long time... - 1 pass lessrandom and 1 pass '
                  'zerofill\n')
            return self._erase_with_status(erase_method)
        raise NotImplementedError(erase_method)

    def _erase_with_status(self, erase_method):
        # Fetch vars.
        # XXX: better dynamic value for sample count based on disk size?
        sample_count = settings.POST_WIPE_SAMPLE_COUNT
        if self._hdd_dock.is_ssd():
            sample_count *= 10  # SSDs/NVMes are fast(er)
        sample_size = settings.POST_WIPE_SAMPLE_SIZE

        print('Attempting erase method {!r} on BLKDEV {!r}'.format(
            erase_method.name, self._hdd_dock.devname))

        # Running pre-sample.  This is not needed, but nice during dev.
        print(
            'DEBUG: Sampling block device to check if empty... '
            '(sample_count: {}, sample_size {})'.format(
                sample_count, sample_size))
        sampler = DiskSampler(
            self._hdd_dock.devname, sample_count, sample_size)
        # Write a fixed sample and read it back from disk.
        sampler.write_sample()
        if sampler.is_different():
            print('WARNING: written sample does not match read sample! '
                  '(possibly faulty disk)')

        print('Start secure wiping BLKDEV')
        success, error = erase_method()
        if not success:
            print('Error: {}'.format(error))
            self._set_status(
                'BLKDEV_SECURE_WIPED_ERROR', (
                    'Block device secure wipe error at {}: {} --{}'
                    .format(self._location, error, self._author)))
            self._set_health('ERASE ERROR')
            return

        print('Block device securely wiped')

        # Running post-sample. Should be all zero.
        print('DEBUG: Sampling block device afterwards...')
        sampler.sample()
        if sampler.is_zero():
            print('OK: All samples are empty')
        elif sampler.is_different():
            print(
                '(probably) OK: All samples are different '
                '(old school crypto disk?)')
        else:
            print('ERROR: Found not-wiped sample!')
            print('Please check {!r} manually!'.format(self._hdd_dock.devname))
            self._set_status(
                'BLKDEV_SECURE_WIPED_ERROR', (
                    'Block device secure wipe {!r} error at {}, non-empty '
                    'samples found --{}'
                    .format(erase_method.name, self._location, self._author)))
            self._set_health('ERASE ERROR')
            return

        # All good!
        self._set_status(
            'BLKDEV_SECURE_WIPED', (
                'Block device secure wiped using {!r} at {} and '
                'checked {}x{} --{}'
                .format(
                    erase_method.name, self._location, sample_count,
                    sample_size, self._author)))
        try:
            self._hdd_dock.flush()
        finally:
            self._set_health('SECURE ERASED')

    def led_failure(self):
        self._hdd_dock.led_failure()

    def led_locate(self):
        self._hdd_dock.led_locate()


def register_disk(**kwargs):
    # Python2-compatible forced kwargs. Temporary fix until we clean up this
    # code.
    hdd_dock = kwargs.pop('hdd_dock')
    inventory_rest_client = kwargs.pop('inventory_rest_client')
    author = kwargs.pop('author')
    location = kwargs.pop('location')
    assert not kwargs, None

    print('')
    print('Disk is not registered yet, please specify the following fields:')
    owner = input('Owner [OSSO]: ')

    # Default to OSSO
    if owner in (None, ''):
        owner = 'OSSO'

    bay = input('bay ['']: ')

    if bay in (None, ''):
        bay = ''

    erase = None
    while erase not in ('y', 'n', 'Y', 'N', ''):
        erase = input('Quick erase? (y/N): ')

    result = inventory_rest_client.add_hdd(hdd_dock, bay)
    tag_uid = result['tag_uid']
    hdd_id = result['id']

    inventory_rest_client.add_smart_data(
        hdd_id, rawdata=hdd_dock.hwdata.rawdata)
    inventory_rest_client.add_status(
        hdd_id, status='REGISTERED',
        extra_info='Registered at {} --{}'.format(location, author))
    inventory_rest_client.add_owner(  # XXX: author-of-owner, not owner-eml
        hdd_id, name=owner, email=author)
    inventory_rest_client.add_location(
        hdd_id, location=location)

    if erase == 'y' or erase == 'Y':
        manager = DeviceManager(
            hdd_dock, hdd_id, inventory_rest_client, author, location)
        manager.quick_erase()

    # Print label, unless the disk is in a remote machine
    if location != 'remote':
        labelprinter_rest_client = get_labelprinter()
        labelprinter_rest_client.print_hdd_label(
            tag_uid, hdd_dock.get_serial_number(), owner)

    input('Registration complete, press enter')


def registered_disk_actions(auto_action=None, owner='', **kwargs):
    # Python2-compatible forced kwargs. Temporary fix until we clean up this
    # code.
    hdd_dock = kwargs.pop('hdd_dock')
    hdd_id = kwargs.pop('hdd_id')
    inventory_rest_client = kwargs.pop('inventory_rest_client')
    static_data = kwargs.pop('static_data')
    del static_data
    dynamic_data = kwargs.pop('dynamic_data')
    author = kwargs.pop('author')
    location = kwargs.pop('location')
    assert not kwargs, None

    if not settings.DEBUG:
        # Always add smart data, even when disk is registered
        inventory_rest_client.add_smart_data(
            hdd_id, rawdata=hdd_dock.hwdata.rawdata)
        # Always add a status & location
        # of the disk being seen at OSSO HQ
        if location != 'remote':
            inventory_rest_client.add_status(
                hdd_id, status='CHECKED_IN',
                extra_info='Checked in at {} --{}'.format(location, author))
            inventory_rest_client.add_location(
                hdd_id, location=location)

    inventory = Inventory(inventory_rest_client, hdd_id)

    def _build_print_data():
        static_data, dynamic_data = build_hdd_info(hdd_dock)
        print_data = static_data + dynamic_data
        print_data.append(['', None])
        print_data.append(['REGISTRATION INFORMATION', None])
        print_data.append(['=', None])
        print_data.append(['Disk is already registered as', inventory.id])
        print_data.append(['Last owner', inventory.current_owner or S_UNSET])
        print_data.append([
            'Last health status', inventory.current_health_status or S_UNSET])
        print_data.append(['Server bay', inventory.bay or S_UNSET])
        return print_data

    manager = DeviceManager(
        hdd_dock, hdd_id, inventory_rest_client, author, location)
    manager.show_summary(_build_print_data())

    # Setup signal handler for remove actions.
    remove_actions = [i[1:] for i in auto_action if i.startswith('/')]
    if remove_actions:
        auto_action = [i for i in auto_action if not i.startswith('/')]

        def remove_disk_interrupt(signum, frame):
            raise ActionInterrupt(remove_actions)
        signal(SIGUSR1, remove_disk_interrupt)

    is_auto = bool(auto_action)
    show_commands = bool(not is_auto)

    while True:
        if not is_auto and show_commands:
            manager.show_commands()
            show_commands = False

        if auto_action:
            action = auto_action.pop(0)
            print(f'\x1b[1mAUTOMATIC ACTION:\x1b[0m {action}')
        else:
            if is_auto:
                manager.show_commands()
                is_auto = False
            try:
                action = input('\nAction: ').upper()
            except ActionInterrupt as interrupt:
                print('\n\n\x1b[1mDISK REMOVED\x1b[0m')
                auto_action = interrupt.args[0]
                is_auto = True
                continue

        if action in ('1', 'set-owner'):
            while len(owner) == 0:
                owner = input('New owner: ')
            inventory_rest_client.add_owner(  # XXX: not email-of-owner
                hdd_id, name=owner, email=author)
            inventory.flush()

        elif action in ('2', 'print-label'):
            # Print label
            labelprinter_rest_client = get_labelprinter()
            labelprinter_rest_client.print_hdd_label(
                inventory.tag_uid, hdd_dock.get_serial_number(),
                inventory.current_owner)

        elif action in ('3', 'quick-erase'):
            manager.quick_erase()
            inventory.flush()

        elif action in ('4', 'secure-erase'):
            manager.best_erase()
            inventory.flush()

        elif action == '5':
            bay = ''
            while len(bay) == 0:
                bay = input('New server bay: ')
            inventory_rest_client.change_bay(hdd_id, bay)
            inventory.flush()
            print('Server bay changed to: {}'.format(inventory.bay))

        elif action == '6':
            health_status = (
                input('Manual health status [ONLINE]: ') or 'ONLINE')
            manager.set_health_with_wear(health_status)
            inventory.flush()

        elif action in ('7', 'print-health-label'):
            # Print label
            print_health_label(hdd_dock, inventory, author, dynamic_data)

        elif action == '8':
            manager.second_best_erase()
            inventory.flush()

        elif action in ('9', 'eject'):
            break  # Quit + EJECT

        elif action in ('D', 'dispose'):
            assert location != 'remote', 'Cannot remote-dispose..'
            inventory_rest_client.add_status(
                hdd_id, status='HDD_DISPOSED',
                extra_info='Disposed in security container at {} --{}'.format(
                    location, author))
            inventory_rest_client.add_location(
                hdd_id, location='OSSO HQ: HDD security container')
            inventory.flush()
            break

        elif action in ('L', 'locate'):
            manager.led_locate()

        elif action == 'P':
            manager.show_summary(_build_print_data())
            show_commands = True

        else:
            print('Notice: {!r} action unknown'.format(action))

    hdd_dock.shutdown_disk()
    sys.exit(0)


def human_readable_bytes(byte_count):
    options = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB']

    counter = 0
    while byte_count // 1024 > 0:
        byte_count = byte_count / 1024.0
        counter += 1
        if counter == len(options) - 1:
            break

    return '{} {}'.format(round(byte_count, 2), options[counter])


def do_print(data, hdd_dock):
    key_length = 0
    item_length = 0

    for key, item in data:
        key_length = max(key_length, len(key))
        item_length = max(item_length, len(item or ''))
    heading = '=' * (key_length + item_length + 3)
    fmt = '{:%d} : {}' % (key_length,)

    print('DISK INFORMATION [BAY NR: {}]'.format(
        hdd_dock.docktool_bay_nr))
    print(heading)

    for key, item in data:
        if item is None and key == '=':
            print(heading)
        elif item is None:
            print(key)
        else:
            print(fmt.format(key, item))


def print_health_label(hdd_dock, inventory, author, dynamic_data):
    """
    Print health status on a label. See also print_health_label_from_db.
    Both would like some refactoring.
    """
    today = datetime.now().strftime('%Y-%m-%d')
    # XXX: don't use dynamic_data please :(
    total_bytes_written = [
        x for x in dynamic_data
        if 'Total bytes written' in x[0]][0]
    total_bytes_read = [
        x for x in dynamic_data
        if 'Total bytes read' in x[0]][0]

    lines = [
        'Health status : {}'.format(
            inventory.current_health_status.upper()),
        '',
        'Serial : {}'.format(hdd_dock.get_serial_number()),
        'Total bytes written/read : {}/{}'.format(
            total_bytes_written[1], total_bytes_read[1]),
        'Power on hours : {} hours'.format(
            hdd_dock.hwdata.power_on_hours or S_UNSET),
        f'--{author} @ {today}',
    ]
    try:
        labelprinter_rest_client = get_labelprinter()
        labelprinter_rest_client.print_generic_label(lines)
    except Exception:
        print('Would have printed:')
        print('\n'.join('- {}'.format(line) for line in lines))
        print()
        raise


def print_health_label_from_db(hdd_data):
    """
    A shabby version of print_health_label() using all info we have
    available in the DB.
    """
    print(
        'WARNING: total bytes read/written and total power hours '
        'not known when printing; you should have printed a health label '
        'in "dev" mode', file=sys.stderr)
    print('... but printing a partial label for you anyway.', file=sys.stderr)

    health = hdd_data['current_health']['status'].upper()
    author_of_health = hdd_data['current_health']['extra_info'].strip()
    if '--' in author_of_health:
        author_of_health = author_of_health.rsplit('--', 1)[-1]
    else:
        author_of_health = 'unknown'
    serial = hdd_data['serial_number']
    date_of_health = hdd_data['current_health']['timestamp'].split('T')[0]

    lines = [
        f'Health status : {health} @ {date_of_health}',
        '',
        f'Serial : {serial}',
        'Total bytes written/read : (not known in db)',
        'Power on hours : (not known in db)',
        f'--{author_of_health} @ {date_of_health}',
    ]
    try:
        labelprinter_rest_client = get_labelprinter()
        labelprinter_rest_client.print_generic_label(lines)
    except Exception:
        print('Would have printed:')
        print('\n'.join('- {}'.format(line) for line in lines))
        print()
        raise


def build_hdd_info(hdd_dock):
    hwdata = hdd_dock.hwdata

    static_data = []

    static_data.append(['Device model', hdd_dock.get_device_model()])
    static_data.append(['Serial', hdd_dock.get_serial_number()])
    static_data.append(
        ['Device (port)', '{} ({})'.format(
            hdd_dock.devname, hdd_dock.port if hdd_dock.port else 'Unknown')])
    static_data.append(['SSD', ('yes' if hdd_dock.is_ssd() else 'no')])
    static_data.append(
        ['SAS (detected)', ('yes' if hdd_dock.is_sas() else 'no')])
    static_data.append(['User Capacity', hdd_dock.get_user_capacity()])

    dynamic_data = []

    total_bytes_written = S_UNSET
    total_bytes_read = S_UNSET
    if hwdata.sector_size is not None:
        if hwdata.lbas_written is not None:
            total_bytes_written = human_readable_bytes(
                hwdata.sector_size * hwdata.lbas_written)
        if hwdata.lbas_read is not None:
            total_bytes_read = human_readable_bytes(
                hwdata.sector_size * hwdata.lbas_read)
    dynamic_data.append(['Total bytes written', total_bytes_written])
    dynamic_data.append(['Total bytes read', total_bytes_read])

    def _NS(value):
        if value is None:
            return S_UNSET
        return str(value)

    dynamic_data.append([
        'Power on hours',
        '{} hours'.format(_NS(hwdata.power_on_hours))])
    dynamic_data.append([
        'Wear health percent', '{}% (smart: {})'.format(
            _NS(hwdata.wear_health_percent), hwdata.smart_status)])
    dynamic_data.append([
        'Reallocated sector count',
        _NS(hwdata.reallocated_sector_ct)])
    dynamic_data.append([
        'Reallocated event count',
        _NS(hwdata.reallocated_event_count)])
    dynamic_data.append([
        'Current pending sector',
        _NS(hwdata.current_pending_sector)])
    dynamic_data.append([
        'Offline uncorrectable',
        _NS(hwdata.offline_uncorrectable)])

    return static_data, dynamic_data


def get_author_and_location():
    author = os.environ.get('EMAIL', '')
    if '@' not in author:
        print('ERROR: Please set the EMAIL envvar to specify who you are!')
        sys.exit(1)
    location = os.environ.get('LOCATION', 'remote')
    if not location:
        print('ERROR: Please (un)set the LOCATION envvar to specify where!')
        sys.exit(1)
    return author, location


def dev_menu(devname, action, owner):
    if os.getuid() != 0:
        warn('Expected UID 0 (root) for access')
    hdd_dock = BaseStorageDevice.from_devname(devname)
    try:
        hdd_dock.led_normal()  # Clear existing LED pattern.
        hdd_dock_dev_menu(hdd_dock, action, owner)
    except Exception:
        hdd_dock.led_failure()
        raise


def hdd_dock_dev_menu(hdd_dock, action, owner):
    author, location = get_author_and_location()
    sys.stdout.write('\x1b]2;DOCKTOOL DISK BAY: {}\x07'.format(
        hdd_dock.docktool_bay_nr))

    # XXX: build_hdd_info() is a quick hack..
    static_data, dynamic_data = build_hdd_info(hdd_dock)

    inventory_rest_client = InventoryRESTClient(
        settings.DASHBOARD_BASE_URL)

    # HDD is an asset so asset_id = hdd_id
    try:
        hdd_id = inventory_rest_client.get_hdd_id(
            hdd_dock.get_device_model(),
            hdd_dock.get_serial_number())
    except ValueError as e:
        warn(str(e))
        do_print(static_data + dynamic_data, hdd_dock)
        raise

    print(
        '\n\x1b[1mBEWARE:\x1b[0m All your actions will be recorded '
        'as performed by: \x1b[1;32m{}\x1b[0m\n'
        'Change EMAIL envvar if it is incorrect!'.format(author))
    print(
        '\x1b[1mBEWARE:\x1b[0m LOCATION is set to: \x1b[1;32m{}\x1b[0m\n'
        'Change to "OSSO HQ: HDD docktool" if in the office.\n'
        .format(location))

    if hdd_id is None:
        do_print(static_data + dynamic_data, hdd_dock)
        register_disk(
            hdd_dock=hdd_dock,
            inventory_rest_client=inventory_rest_client,
            author=author, location=location)
        hdd_id = inventory_rest_client.get_hdd_id(
            hdd_dock.get_device_model(),
            hdd_dock.get_serial_number())
        assert hdd_id, 'HDD id not set after registration?'
        # If one action is to print a health label also print a normal label
        # for new registered disks.
        if 'print-health-label' in action and 'print-label' not in action:
            action.insert(0, 'print-label')

    registered_disk_actions(
        hdd_dock=hdd_dock, hdd_id=hdd_id,
        inventory_rest_client=inventory_rest_client,
        static_data=static_data, dynamic_data=dynamic_data,
        author=author, location=location, auto_action=action, owner=owner)


def db_menu(serial):
    inventory_rest_client = InventoryRESTClient(
        settings.DASHBOARD_BASE_URL)

    # HDD is an asset so asset_id = hdd_id
    hdd_id = inventory_rest_client.get_hdd_id(None, serial)  # serial?
    if hdd_id is not None:
        hdd = inventory_rest_client.get_hdd(hdd_id)[0]
    else:
        hdd = inventory_rest_client.get_hdd(serial)[0]  # hdd_id as "serial"
    if hdd is None:
        raise ValueError('serial/asset not found in remote DB')

    # Ok, we have an ID. Get info from remote?
    do_print_health_label = None
    while do_print_health_label not in ('y', 'n', ''):
        do_print_health_label = input('Print health label? (y/N): ').lower()

    if do_print_health_label == 'y':
        print_health_label_from_db(hdd)
        print('done.')
    else:
        from pprint import pprint
        pprint(hdd)


class AutoServer:
    def __init__(self, action, gui, ignore_devices, owner):
        self.action = action
        self.gui = gui
        self.ignore_devices = [i.resolve() for i in ignore_devices]
        self.owner = owner
        # Make sure the environment is valid to start osso-docktool.
        self.author, self.location = get_author_and_location()
        # It's possible a device does not eject/spin down properly and triggers
        # the udev rules again. Keep a list of disk serials which have been
        # started and ignore subsequent notifications about that disk.
        self.seen_devices = {}
        if not gui:
            if not os.environ.get('TMUX'):
                args = [
                    'tmux', 'new', '-s', 'docktool', '-n', 'main',
                    self.docktool_exec, 'auto']
                if self.owner:
                    args += ['--owner', self.owner]
                if self.action:
                    args.extend(self.action)
                os.execvp('tmux', args)
            else:
                # Add the environment to the tmux session.
                subprocess.check_call(
                    ['tmux', 'set', 'remain-on-exit', 'on'])
                subprocess.check_call(
                    ['tmux', 'setenv', 'EMAIL', self.author])
                subprocess.check_call(
                    ['tmux', 'setenv', 'LOCATION', self.location])

    def start(self):
        try:
            self.listen()
        except KeyboardInterrupt:
            raise SystemExit()

    def listen(self):
        if os.getuid() != 0:
            warn('Expected UID 0 (root) for access')
        with socket(AF_INET, SOCK_STREAM) as sock:
            sock.bind(('127.0.0.1', 1451))
            sock.listen(4)
            sock.setblocking(True)
            print('osso-docktool automatic™')
            print(
                '\x1b[1mBEWARE:\x1b[0m All your actions will be recorded '
                f'as performed by: \x1b[1;32m{self.author}\x1b[0m\n'
                'Change EMAIL envvar if it is incorrect!')
            print(
                '\x1b[1mBEWARE:\x1b[0m LOCATION is set to: \x1b[1;32m'
                f'{self.location}\x1b[0m\n'
                'Change to "OSSO HQ: HDD docktool" if in the office.')
            print('Actions:', ', '.join(self.action))
            if any(i in self.action for i in ('quick-erase', 'secure-erase')):
                print('\x1b[1mBEWARE:\x1b[0m this will destroy the data on '
                      'newly connected disks without confirmation !')
            if self.ignore_devices:
                print(
                    'Ignoring devices:',
                    ','.join([str(i) for i in self.ignore_devices]))
            print('Waiting for disk notifications...')
            while True:
                connection, address = sock.accept()
                self.handle_client(connection)

    def handle_client(self, connection):
        client_data = b''
        with connection:
            while True:
                data = connection.recv(1024)
                if not data:
                    break
                client_data += data

        if client_data:
            notification = client_data.decode()
            try:
                cmd, device = notification.split(':', 1)
            except ValueError:
                print(f'Received malformed notification: {notification!r}')
                return

            device = Path(device)
            if device.is_block_device():
                hdd_dock = BaseStorageDevice.from_devname(device)
                serial = hdd_dock.get_serial_number()
                if self.is_ignored(
                        device, serial, force=bool(cmd.endswith('-force'))):
                    print(f'Ignoring notification for {device}:{serial}')
                elif cmd.startswith('device-add'):
                    self.start_docktool(device, serial)
            elif cmd.startswith('device-remove'):
                # Block device no longer exists but if we have seen it before
                # we will send the remove signal to the last osso-docktool
                # for that device.
                if device in self.seen_devices:
                    self.seen_devices.pop(device)
                    self.signal_docktool(device)
            else:
                print(f'Path {device} is not a block device')

    @property
    def docktool_exec(self):
        return Path(sys.argv[0]).resolve()

    def is_ignored(self, device, serial, force):
        if device.resolve() in self.ignore_devices:
            return True

        if not force and serial in self.seen_devices.values():
            print(f'Skipped repeat Device {device} with serial {serial}')
            print(
                f'Use "osso-docktool auto-notify {device} --force" to start')
            return True
        self.seen_devices[device] = serial
        return False

    def start_docktool(self, device, serial):
        if self.gui:
            self.start_gui(device, serial)
        else:
            self.start_cli(device, serial)

    def start_gui(self, device, serial):
        print(f'Starting GUI terminal for {device}:{serial}')
        pid = os.fork()
        if pid > 0:
            os.waitid(os.P_PID, pid, os.WEXITED)
            return

        # Double fork to detach X terminal from pid group.
        if os.fork() == 0:
            args = [f'osso-docktool-terminal [{device}:{serial}]', '-e']
            args += self.get_docktool_cmd(device)
            os.setsid()
            os.execvp('x-terminal-emulator', args)
        else:
            os._exit(0)

    def start_cli(self, device, serial):
        print(f'Creating new tmux window for {device}:{serial}')
        if not os.environ.get('TMUX'):
            print('Error: TMUX environment variable is empty', file=sys.stderr)
        else:
            args = ['tmux', 'new-window', '-n', device]
            args += self.get_docktool_cmd(device)
            subprocess.check_call(args)

    def get_docktool_cmd(self, device):
        cmd = ['sudo', '-E', self.docktool_exec, 'dev', device, '--wait']
        for action in self.action:
            cmd += ['--action', action]
        if self.owner:
            cmd += ['--owner', self.owner]
        return cmd

    def signal_docktool(self, device):
        # Perform on remove actions with the last active osso-docktool for the
        # given device.
        pid = subprocess.check_output(
            ['pgrep', '-nf', f'osso-docktool dev {device}'], text=True).strip()
        if pid.isdigit():
            os.kill(int(pid), SIGUSR1)


def auto_notify(device, notification, force):
    if force:
        notification = f'{notification}-force:{device}'
    else:
        notification = f'{notification}:{device}'

    with socket(AF_INET, SOCK_STREAM) as sock:
        sock.settimeout(3)
        try:
            sock.connect(('127.0.0.1', 1451))
            sock.sendall(notification.encode())
        except ConnectionError as e:
            print(f'Error notifying auto process: {e}', file=sys.stderr)


class DocktoolArgumentParser(argparse.ArgumentParser):
    def __init__(self):
        super().__init__(
            prog='osso-docktool',
            description='Docktool for processing disks')  # exit_on_error=False
        self.message2 = None

        actions = [
            'dispose', 'eject', 'print-label', 'print-health-label',
            'locate', 'set-owner', 'quick-erase', 'secure-erase',
            # Prefix with / to use as remove action.
            '/print-health-label',
        ]

        self.subparsers = self.add_subparsers(
            title='subcommands', dest='command', required=True,
            help='subcommand help',
            parser_class=argparse.ArgumentParser)

        devparser = self.subparsers.add_parser(
            'dev',
            help='(implied!) process hardware device (original behaviour)')
        devparser.add_argument(
            'device', metavar='DISK', type=self.block_device,
            help='Device to use for example: /dev/sda')
        devparser.add_argument(
            '-a', '--action', choices=actions, action='append', default=[],
            help='Automatically execute the actions in order.')
        devparser.add_argument(
            '-o', '--owner', metavar='OWNER', default='',
            help='The owner to set for the set-owner action.')
        devparser.add_argument(
            '-w', '--wait', action='store_true',
            help='Wait for user confirmation before exit.')

        dbparser = self.subparsers.add_parser(
            'db', help='process devices device info without hardware access')
        dbparser.add_argument(
            'serial', metavar='SERIAL',
            help='Serial number (or GoCollect asset UID')

        autoparser = self.subparsers.add_parser(
            'auto',
            help='Automatically perform action on newly inserted disks')
        autoparser.add_argument(
            '-g', '--gui', action='store_true',
            help='Start docktool processes in a GUI instead of tmux session. '
                 'Use `update-alternatives --config x-terminal-emulator` to '
                 'configure the terminal.')

        try:
            ignore_default = [
                self.block_device(i) for i in settings.IGNORE_DEVICES]
        except argparse.ArgumentTypeError:
            self.exit(
                status=1,
                message=f'{self.prog}: The IGNORE_DEVICES setting is '
                        'invalid\n')

        autoparser.add_argument(
            '-i', '--ignore', action='append', metavar='DISK',
            default=ignore_default, type=self.block_device,
            help='Ignore the device for auto commands.')
        autoparser.add_argument(
            '-o', '--owner', metavar='OWNER',
            help='The owner to set for the set-owner action.')
        autoparser.add_argument(
            # https://bugs.python.org/issue27227
            # Add [] to choices to make actions optional.
            'action', nargs='*', choices=actions + [[]],
            help='Start docktool and perform these actions in order '
                 '(default: start osso-docktool, no extra action).')

        notifyparser = self.subparsers.add_parser(
            'auto-notify',
            help='Notify the auto server of the device')
        notifyparser.add_argument(
            '-a', '--add', action='store_const', const='device-add',
            dest='notification', help='Send a device add notification.')
        notifyparser.add_argument(
            '-r', '--remove', action='store_const', const='device-remove',
            dest='notification', help='Send a device remove notification.')
        notifyparser.add_argument(
            '-f', '--force', action='store_true',
            help='Force the auto server to process the device.')
        # Notify can be used on removed disks which cannot validate
        # as a block device type.
        notifyparser.add_argument(
            'device', metavar='DISK',
            help='Device to use for example: /dev/sda')
        notifyparser.set_defaults(notification='device-add')

    def parse_args(self):
        if len(sys.argv) == 2 and not (
                sys.argv[1].startswith('-')
                or sys.argv[1] in self.subparsers.choices):
            sys.argv[1:1] = ['dev']  # imply "dev"
        return super().parse_args()

    def exit(self, status=0, message=None):
        if self.message2:
            print('{prog}: {message}'.format(
                prog=self.prog, message=self.message2),
                file=sys.stderr)
            self.message2 = None
        elif len(sys.argv) == 1:
            try:
                candidates = sorted(set([
                    os.path.realpath(os.path.join('/dev/disk/by-id', i))
                    for i in os.listdir('/dev/disk/by-id')]))
            except FileNotFoundError:
                # ??? no /dev/disk/by-id?
                candidates = ['(no disks found?)']
            message2 = 'suggesting disks:{}'.format(
                '\n  '.join([''] + candidates))
            print('{prog}: {message}'.format(
                prog=self.prog, message=message2),
                file=sys.stderr)

        super().exit(status=status, message=message)

    def block_device(self, name):
        device = Path(name)
        if not device.is_absolute():
            warn('Prepended /dev/ to the block device name')
            return self.block_device('/dev' / device)
        if not device.exists():
            self.message2 = f'{device}: not found'
            raise argparse.ArgumentTypeError(f'{device}: not found')
        if not device.is_block_device():
            self.message2 = f'{device}: not a block device'
            raise argparse.ArgumentTypeError(f'{device}: not a block device')
        return device


def main():
    parser = DocktoolArgumentParser()
    args = parser.parse_args()

    try:
        if args.command == 'dev':
            dev_menu(args.device, args.action, args.owner)
        elif args.command == 'serial':
            db_menu(args.serial)
        elif args.command == 'auto':
            AutoServer(args.action, args.gui, args.ignore, args.owner).start()
        elif args.command == 'auto-notify':
            auto_notify(args.device, args.notification, args.force)
    except KeyboardInterrupt:
        sys.exit(0)
    except SystemExit:
        if args.wait:
            input('Press enter to exit')
    except Exception as e:
        print('ERROR: {}\n'.format(e), file=sys.stderr)
        print()
        print(traceback.format_exc(), file=sys.stderr)
        input('Error found, please inform developer. Press enter')
        # #raise e  # (a bit duplicate, no?)
        sys.exit(1)


if __name__ == '__main__':
    main()
