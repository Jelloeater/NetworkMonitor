__author__ = 'Jesse'

from Database import db_controller


def get_server_list():
    # FIXME write getter for server list
    conn, cur = db_controller.db_access().open_connection()
    get_all_query = '''SELECT * FROM monitor_list'''
    cur.execute(get_all_query)
    db_fetch = cur.fetchall()
    db_controller.db_access.close_connection(conn,cur)
    return db_fetch