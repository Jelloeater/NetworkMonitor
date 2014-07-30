__author__ = 'Jesse'

from Database import db_controller


class monitor_list(object):

    @staticmethod
    def get_server_list():
        # FIXME write getter for server list
        conn, cur = db_controller.db_access().open_connection()
        get_all_query = '''SELECT * FROM monitor_list'''
        cur.execute(get_all_query)
        db_fetch = cur.fetchall()
        db_controller.db_access.close_connection(conn,cur)
        return db_fetch


class tcp(monitor_list):
    def __init__(self):
        pass

    @staticmethod
    def create_server(ip_address, port):
        # TODO Update function
        conn, cur = db_controller.db_access().open_connection()
        get_all_query = '''SELECT * FROM monitor_list'''
        cur.execute(get_all_query)
        db_controller.db_access.close_connection(conn,cur)


    @staticmethod
    def update_server(ip_address, port):
        # TODO Update function
        conn, cur = db_controller.db_access().open_connection()
        get_all_query = '''SELECT * FROM monitor_list'''
        cur.execute(get_all_query)
        db_controller.db_access.close_connection(conn,cur)

    @staticmethod
    def remove_server(ip_address):
        # TODO Update function
        conn, cur = db_controller.db_access().open_connection()
        get_all_query = '''SELECT * FROM monitor_list'''
        cur.execute(get_all_query)
        db_controller.db_access.close_connection(conn,cur)


class host(monitor_list):
    def __init__(self):
        pass

    @staticmethod
    def create_server(ip_address):
        # TODO Update function
        conn, cur = db_controller.db_access().open_connection()
        get_all_query = '''SELECT * FROM monitor_list'''
        cur.execute(get_all_query)
        db_controller.db_access.close_connection(conn,cur)

    @staticmethod
    def update_server(ip_address):
        # TODO Update function
        conn, cur = db_controller.db_access().open_connection()
        get_all_query = '''SELECT * FROM monitor_list'''
        cur.execute(get_all_query)
        db_controller.db_access.close_connection(conn,cur)

    @staticmethod
    def remove_server(ip_address):
        # TODO Update function
        conn, cur = db_controller.db_access().open_connection()
        get_all_query = '''SELECT * FROM monitor_list'''
        cur.execute(get_all_query)
        db_controller.db_access.close_connection(conn,cur)


class url(monitor_list):
    def __init__(self):
        pass

    @staticmethod
    def create_server(web_url):
        # TODO Update function
        conn, cur = db_controller.db_access().open_connection()
        get_all_query = '''SELECT * FROM monitor_list'''
        cur.execute(get_all_query)
        db_controller.db_access.close_connection(conn,cur)

    @staticmethod
    def update_server(web_url):
        # TODO Update function
        conn, cur = db_controller.db_access().open_connection()
        get_all_query = '''SELECT * FROM monitor_list'''
        cur.execute(get_all_query)
        db_controller.db_access.close_connection(conn,cur)

    @staticmethod
    def remove_server(web_url):
        # TODO Update function
        conn, cur = db_controller.db_access().open_connection()
        get_all_query = '''SELECT * FROM monitor_list'''
        cur.execute(get_all_query)
        db_controller.db_access.close_connection(conn,cur)