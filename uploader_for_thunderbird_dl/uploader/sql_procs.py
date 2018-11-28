from flask    import g
from re       import compile
from datetime import datetime as dt
from tools    import uniques, sortby as sby

#define LOG_EMERG       0       /* system is unusable */
#define LOG_ALERT       1       /* action must be taken immediately */
#define LOG_CRIT        2       /* critical conditions */
#define LOG_ERR         3       /* error conditions */
#define LOG_WARNING     4       /* warning conditions */
#define LOG_NOTICE      5       /* normal but significant condition */
#define LOG_INFO        6       /* informational */
#define LOG_DEBUG       7       /* debug-level messages */

__get_log_tables_from_schema__ = "SELECT table_name FROM information_schema.tables WHERE table_type = 'BASE TABLE' AND table_schema = 'public' AND table_name LIKE 'log%{0}{1}{2}' ORDER BY table_type, table_name"
__get_log_tables_from_schema_wlup__ = "SELECT * FROM gettables('{0}', '{1}', '{2}')"
__get_log_tables_from_schema_wlup_wcnt__ = "SELECT * FROM gettables_lup_counts('{0}', '{1}', '{2}')"


def parseTablesName( tables ):
    regex   = compile( 'log_(\d{6})_(.+)_(\d{6})_(.+)' )
    re_date = compile( '(\d{2})(\d{4})' )
    aliases = getAliases(1)

    def parseTableName( table, last_update=None, err_cnt=None, warn_cnt=None ):
        last_update = last_update.strftime('%d.%m.%Y %H:%M:%S') if last_update else None
        out = { 'host': None, 'program': None, 'data': None, 'src': None, 'comment':' ', 'alias':None, 'last_update': last_update, 'counts': (err_cnt, warn_cnt) }
        p_table = regex.findall( table )
        if len(p_table) >=1 and len(p_table[0]) >= 4:
            if p_table[0][0] == p_table[0][2]:
                date = '.'.join( ['01'] + list( re_date.findall( p_table[0][0] )[0] ) )
                out.update( { 'host':p_table[0][1], 'program': p_table[0][3], 'date': date, 'src':table, 'alias': aliases[p_table[0][3]] if p_table[0][3] in aliases else None } )
        else:
            out.update( { 'host': None, 'program': None, 'data': None, 'src': table } )
        return out

    return map(lambda x: parseTableName(*x), tables)

def getLogTables(host=None, program=None, date=None, with_lup=False, with_counts=False, _unique=None):
    host    = '{0}%'.format( host    ) if host    else str()
    program = '{0}%'.format( program ) if program else str()
    date    = '{0}%'.format( date )    if date    else str()
    if with_counts:
        data = parseTablesName( g.db.prepare( __get_log_tables_from_schema_wlup_wcnt__.format(host, program, date) )() )
    elif with_lup:
        data = parseTablesName( g.db.prepare( __get_log_tables_from_schema_wlup__.format(host, program, date) )() )
    else:
        data = parseTablesName( g.db.prepare( __get_log_tables_from_schema__.format(host, program, date) )() )

    if _unique:
        data = uniques( _unique, data)
    return data


def getHostTablesDates( host ):
    'Get Dates range for one host'
    data = getLogTables( host, _unique='date' )
    return map( lambda x: x['date'], data )

def getHostOneTableDates( host, program ):
    'Get Dates range for one program one  host'
    data = getLogTables( host, program, _unique='date' )
    return map( lambda x: x['date'], data )

def MAX(key, data):
    max_val = dt(1,1,1)
    for val in data:
        val = dt.strptime(val[key], '%d.%M.%Y')
        if val > max_val:
            max_val = val
    return max_val

def getHostTable_Date_Last(host, program):
    'Get Dates range for one program one  host'
    data = getLogTables( host, program )
    return MAX('date', data)

def getHostsDates():
    'Get Dates range for one program one  host'
    data = getLogTables( _unique='date' )
    return map( lambda x: x['date'], uniques( 'date', data ) )


def isTable(name):
    data = g.db.prepare( "SELECT COUNT(table_name) FROM information_schema.tables WHERE table_type = 'BASE TABLE' AND table_schema = 'public' AND table_name='%s'" % name )()
    if data[0][0]: return True
    return False


def hostsList(date=None, func=None):
    data = getLogTables(host=None, program=None, date=date, with_lup=False, with_counts=False, _unique='host')
    if func: data = map(func, data)
    return list( data )

def programsList(host=None, date=None, func=None, sortby=None):
    data = getLogTables(host, program=None, date=date, with_lup=True, with_counts=True, _unique='program')
    if sortby: data = sby(sortby, data)
    if func: data = map(func, data)
    return list( data )


def getAliases( type ):
    db_data = g.db.prepare("SELECT name, alias FROM aliases WHERE type=%d" % type)
    return dict(db_data());


def getProgramsListLen( host, filter ):
    recordsTotal    = len( list( getLogTables(host, _unique='program') ) )
    recordsFiltered = len( list( getLogTables(host, filter, _unique='program') ) )
    return [ recordsTotal, recordsFiltered ]

def getHostsListLen( filter ):
    recordsTotal    = len( list( getLogTables( _unique='host') ) )
    recordsFiltered = len( list( getLogTables( filter, _unique='host') ) )
    return [ recordsTotal, recordsFiltered ]


class SqlRequest(object):
    def __init__(self, args):
        super(SqlRequest, self).__init__()


    def From(self, val):
        if val: self._args_.update( { 'from' : 'FROM "%s"' % val } )
        return self

    # val is userid!=1001
    def Where(self, val):
        return self.__update__('WHERE', val)

    def __update__(self, root, key, val):
        if val and type(val) == str:
                self._args_.update( { key : val } )
        return self

    def And(self, val):
        if val and type(val) == str:
            self._args_['and'].append(val)

    def __str__(self):
        "%()s"


def getLogContent(logtable, filter, orderby, limit, offset):
    sqlreq = g.db.prepare(
        ' '.join( [
            'SELECT host, program, pid, level, datetime, message'
         ,  'FROM "%(logtable)s"'
         ,  'INNER JOIN message_levels lvls ON level_num=lvls.id'
         ,  '%(where)s'
         ,  '%(orderby)s'
         ,  '%(limit)s'
         ,  '%(offset)s' ] )
         % ( {
             'logtable' : logtable
           , 'where'    : ( 'WHERE %s'    % filter  ) if filter  else ''
           , 'orderby'  : 'ORDER BY datetime' #( 'ORDER BY %s' % orderby ) if orderby else ''
           , 'limit'    : ( 'LIMIT %s'    % limit   ) if limit   else ''
           , 'offset'   : ( 'OFFSET %s'   % offset  ) if offset  else ''
         } )
    )
    data = sqlreq()
    return data
