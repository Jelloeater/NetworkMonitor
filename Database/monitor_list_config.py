import db_helpers

__author__ = 'Jesse'


def check_for_valid_service_type():
    # TODO Should query valid_types table
    pass

    # TODO Make sure web addresses are complete ex http://www.google.com


def list_servers():
    x = db_helpers.monitor_list.get_server_list()
    print("Servers:")
    print("{0}{1}{2}{3}".format("Index".ljust(8), "Hostname".ljust(50), "Port".ljust(8), "Service Type".ljust(0)))

    for i in x:
        print "{0}{1}{2}{3}".format(str(i[0]).ljust(8), i[1].ljust(50), str(i[2]).ljust(8), i[3].ljust(0))

    return x  # Return the list, should come in handy


def main():
    # TODO Write TUI for configuring servers (should use db_helpers.monitor_list.tcp/host/url.create/etc)
    while True:
        server_list = list_servers()
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
                db_helpers.monitor_list.host.create_server(hostname)

            if type_choice == '2':
                print("Enter URL (ex http://www.google.com):")
                url = raw_input('({0})>'.format(''))
                db_helpers.monitor_list.url.create_server(url)

            if type_choice == '3':
                print("Enter Hostname (ex 127.0.0.1):")
                hostname = raw_input('({0})>'.format(''))
                print("Enter Port (ex 22):")
                port = raw_input('({0})>'.format(''))
                db_helpers.monitor_list.tcp.create_server(hostname, port)

        if menu_choice == "2":
            menu_choice = raw_input('({0})>'.format('Remove: '))
            db_helpers.monitor_list.remove_server_from_monitor_list(menu_choice)

        if menu_choice == "3":
            break