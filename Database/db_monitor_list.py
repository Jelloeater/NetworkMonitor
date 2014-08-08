import logging

import db_helpers


__author__ = 'Jesse'


def check_for_valid_service_type():
    # TODO Should query valid_types table
    pass

    # TODO Make sure web addresses are complete ex http://www.google.com


def get_print_server_list():
    x = db_helpers.monitor_list.get_server_list()
    print("Servers:")
    print("{0}{1}{2}{3}{4}".format("Index".ljust(8), "Hostname".ljust(50), "Port".ljust(8),
                                   "Service".ljust(10), "Note".ljust(0)))

    # TODO There's got to be a better way of doing this
    for i in x:
        if i[2] is None and i[4] is None:
            print "{0}{1}{2}{3}{4}".format(str(i[0]).ljust(8), i[1].ljust(50), str("").ljust(8),
                                           i[3].ljust(10), str("").ljust(0))
        if i[2] is not None and i[4] is None:
            print "{0}{1}{2}{3}{4}".format(str(i[0]).ljust(8), i[1].ljust(50), str(i[2]).ljust(8),
                                           i[3].ljust(10), str("").ljust(0))
        if i[2] is None and i[4] is not None:
            print "{0}{1}{2}{3}{4}".format(str(i[0]).ljust(8), i[1].ljust(50), str("").ljust(8),
                                           i[3].ljust(10), str(i[4]).ljust(0))
        if i[2] is not None and i[4] is not None:
            print "{0}{1}{2}{3}{4}".format(str(i[0]).ljust(8), i[1].ljust(50), str(i[2]).ljust(8),
                                           i[3].ljust(10), str(i[4]).ljust(0))

    return x  # Return the list, should come in handy


def config_monitor_list():
    while True:
        server_list = get_print_server_list()
        print("")
        print('Menu Options')
        print("1\t Add Server")
        print("2\t Remove Server")
        print("3\t Exit")
        print("")

        menu_choice = raw_input('({0})>'.format('Menu Choice'))

        if menu_choice == "1":
            print("Choose Service Type to Monitor:")
            print("1\t Host")
            print("2\t URL")
            print("3\t TCP")

            type_choice = raw_input('({0})>'.format('Service Type'))

            if type_choice == '1':
                print("Enter Hostname (ex 127.0.0.1):")
                hostname = raw_input('({0})>'.format(''))
                print("Enter Note (ex Web Server):")
                note = raw_input('({0})>'.format(''))
                if note.isspace() or note == "":
                    db_helpers.monitor_list.host.create_server(hostname)
                else:
                    db_helpers.monitor_list.host.create_server(hostname, note)

            if type_choice == '2':
                print("Enter URL (ex http://www.google.com):")
                url = raw_input('({0})>'.format(''))
                print("Enter Note (ex Web Server):")
                note = raw_input('({0})>'.format(''))

                if note.isspace() or note == "":
                    db_helpers.monitor_list.url.create_server(url)
                else:
                    db_helpers.monitor_list.url.create_server(url, note)

            if type_choice == '3':
                print("Enter Hostname (ex 127.0.0.1):")
                hostname = raw_input('({0})>'.format(''))
                print("Enter Port (ex 22):")
                port = raw_input('({0})>'.format(''))
                print("Enter Note (ex Web Server):")
                note = raw_input('({0})>'.format(''))

                logging.debug(note.isspace())
                if note.isspace() or note == "":
                    db_helpers.monitor_list.tcp.create_server(hostname, port)
                else:
                    db_helpers.monitor_list.tcp.create_server(hostname, port, note)

        if menu_choice == "2":
            menu_choice = raw_input('({0})>'.format('Remove: '))
            db_helpers.monitor_list.remove_server_from_monitor_list(menu_choice)

        if menu_choice == "3":
            break