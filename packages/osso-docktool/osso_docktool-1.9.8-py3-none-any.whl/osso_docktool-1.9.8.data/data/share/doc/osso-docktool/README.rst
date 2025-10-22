osso-docktool :: HDD administration and maintenance
===================================================

*osso-docktool* provides tools to register disks to the OSSO dashboard, to
print labels and wipe disks.

Requirements (``apt install --no-install-recommends``)::

    tmux            # auto cli mode
    coreutils       # dd
    pwgen           # pwgen
    smartmontools   # smartctl
    nvme-cli        # nvme
    hdparm          # hdparm
    sdparm          # sdparm
    ledmon          # LED control

    # FIXME: /usr/local/bin/run-lessrandom
    # FIXME: /usr/local/bin/run-zero-disk

Example usage (as root)::

    osso-docktool /dev/sdb

Example setup (as root)::

    pip3 install osso-docktool

    install -dm0700 /etc/osso-docktool
    install /usr/local/share/doc/osso-docktool/local_settings.py.template \
            /etc/osso-docktool/local_settings.py

    ${EDITOR:-vi} /etc/osso-docktool/local_settings.py
    # ^-- fix hostnames, fix tokens
    #     get 1 shared token from:
    #     https://account.example.com/admin/usertoken/token/
    #     If you wish to use the auto process you will want to add the
    #     root disk to the IGNORE_DEVICES list.

Automation
----------

``/etc/udev/rules.d/10-osso-docktool.rules``::

    # Match the block device but not the partitions.
    KERNEL=="sd[a-z]", SUBSYSTEM=="block", ACTION=="add", ENV{SYSTEMD_WANTS}+="osso-docktool@%k.service", TAG+="systemd"


``/etc/systemd/system/osso-docktool@.service``::

    [Unit]
    Description=Notify osso-docktool about disk %i
    StopWhenUnneeded=yes

    [Service]
    Type=oneshot
    RemainAfterExit=yes
    ExecStart=/usr/local/bin/osso-docktool auto-notify --add /dev/%i
    ExecStop=/usr/local/bin/osso-docktool auto-notify --remove /dev/%i

When a disk is inserted this will start the
`osso-docktool@<disk>.service` which will notify the osso-docktool
auto process. The service is needed because udev starts RUN commands in
a restricted container without network access and the systemd process is
started outside the restricted container.

When the disk is removed systemd will stop the
`osso-docktool@<disk>.service`.

There are several auto commands
Beware that both erase commands will erase all inserted disks that do
not match the ignore list without confirmation!

``EMAIL=me@example.com osso-docktool auto``

By default this uses a tmux session to spawn osso-docktool commands but
there is a `-g|--gui` toggle to switch to a graphical terminal. You can
change the default graphical terminal with the command::

    update-alternatives --config x-terminal-emulator


Other tools
-----------

``/usr/local/bin/run-zero-disk`` (0700)::

    #!/bin/bash

    path=$1
    if test -z $path; then
        echo "please supply path as argument"
        exit 1
    fi
    output=$(dd if=/dev/zero \
       of=$path \
       bs=32M \
       conv=fsync 2>&1)
    ret=$?

    # Checking output as DD does not exit clean even if whole disk is wiped

    if [[ $ret -eq 0 ]]; then
        exit 0
    else
        if [[ $output == *'No space left on device'* ]]; then
            echo "Disk $path has been zeroed"
            exit 0
        else
            echo "Something went wrong while writing to $path"
            echo $output
            exit 1
        fi
    fi

Compile lessrandom.c and move lessrandom to ``/usr/local/bin/lessrandom`` (0700)::

    lessrandom.c:

    #include <stdio.h>
    #include <time.h>
    #define BUF 4096
    int main() {
        FILE *f;
        char buf[BUF];
        f = fopen("/dev/urandom", "rb");
        while (1) {
            if (fread(buf, 1, BUF, f) == BUF) {
                int i;
                for (i = 0; i <= buf[0]; ++i) {
                    fwrite(buf, 1, BUF - 1, stdout);
                }
            }
        }
        fclose(f);
        return 0;
    }


    gcc -Wall lessrandom.c -o lessrandom


``/usr/local/bin/run-lessrandom`` (0700)::

    #!/bin/bash

    path=$1
    if test -z $path; then
        echo "please supply path as argument"
        exit 1
    fi
    output=$(dd if=<(/usr/local/bin/lessrandom) \
       of=$path \
       bs=32M \
       conv=fsync 2>&1)
    ret=$?

    # Checking output as DD does not exit clean even if whole disk is wiped

    if [[ $ret -eq 0 ]]; then
        exit 0
    else
        if [[ $output == *'No space left on device'* ]]; then
            echo "Disk $path has been wiped"
            exit 0
        else
            echo "Something went wrong while writing to $path"
            echo $output
            exit 1
        fi
    fi
