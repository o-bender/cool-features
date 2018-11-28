import postgresql.driver as pg

class SQL(pg):
    def __init__(self, **args):
        super(SQL, self).__init__()


    def getTables():
        database = self.database
        p = self.prepare("SELECT table_name FROM information_schema.tables WHERE table_catalog='%s' AND table_schema='publick'" % database)
        return [ table[0] for table in p ] # if len(table) > 0 ?
