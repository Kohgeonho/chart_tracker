import mysql.connector
from attributes import *

chartdb = mysql.connector.connect(
    host = "songdb.ck45skw5jvl2.ap-northeast-2.rds.amazonaws.com",
    user = "geonho_sojeong",
    password = "geonho&sojeong",
    database = "chart"
)

cursor = chartdb.cursor()

def truncate_all():
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
    
    cursor.execute("TRUNCATE TABLE Time;")
    cursor.execute("TRUNCATE TABLE Song;")
    cursor.execute("TRUNCATE TABLE Artist;")
    cursor.execute("TRUNCATE TABLE Musician;")
    cursor.execute("TRUNCATE TABLE Album;")
    
    cursor.execute("TRUNCATE TABLE Sing;")
    cursor.execute("TRUNCATE TABLE WrittenBy;")
    cursor.execute("TRUNCATE TABLE ComposedBy;")
    cursor.execute("TRUNCATE TABLE ArrangedBy;")
    cursor.execute("TRUNCATE TABLE Contain;")
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
    
    cursor.execute("SELECT * FROM Time;")
    cursor.fetchall()
    
def exist(relation, attribute, key):
    
    fetch = f'''
        SELECT  *
        FROM    {relation} 
        WHERE   {attribute} = '{key}';
    '''
    
    cursor.execute(fetch)
    
    if cursor.fetchall() == []:
        return False
    
    return True

def insert(relation, values):
    sql = f'INSERT INTO {relation} VALUES '
    val = str(values)
    
    cursor.execute(sql + val)
    
def saveArtist(sid, mid):
    if not exist('Artist', 'mid', mid):
        artist = musician_page(mid)
        artist.set_attributes()
        
        insert('Artist', artist.get_attributes())
                
    insert('Sing', (mid, sid))
    
def saveMusician(sid, mid, cls):
    if not exist('Musician', 'mid', mid):
        musician = musician_page(mid)
        musician.set_attributes()
                
        insert('Musician', musician.get_attributes()[:4])   
        
    related_attrs = {'Lyricist' : 'WrittenBy',
                     'Composer' : 'ComposedBy',
                     'Arranger' : 'ArrangedBy'}
    
    insert(related_attrs[cls], (sid, mid))

def saveAlbum(sid, aid):
    if not exist('Album', 'aid', aid):
        album = album_page(aid)
        album.set_attributes()
        
        insert('Album', album.get_attributes())
        for track, title in album.tracks:
            istitle = True if title == 'Title' else False
            insert('Contain', (aid, track, istitle))
            
def saveSong(sid, rank):
    song = song_page(sid, rank + 1)
    song.set_attributes()
    
    insert('Time', song.time_attributes())
    
    if not exist('Song', 'sid', sid):
        insert('Song', song.get_attributes())
                
        saveArtist(sid, song.artist)
        saveAlbum(sid, song.album)
        
        if not song.lyricists == 'NULL':
            for mid in song.lyricists:
                saveMusician(sid, mid, cls='Lyricist')
        if not song.composers == 'NULL':
            for mid in song.composers:
                saveMusician(sid, mid, cls='Composer')
        if not song.arrangers == 'NULL':
            for mid in song.arrangers:
                saveMusician(sid, mid, cls='Arranger')
                        
def crawl():
    
    print("crawling started at ", datetime.datetime.now())
    driver_init()

    song_ids = get_table()
    
    for rank, sid in enumerate(song_ids):
        saveSong(sid, rank)
        chartdb.commit()
        
    driver_quit()
    print("crawling ended at ", datetime.datetime.now(), end='\n\n')