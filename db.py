import sqlite3


db =  sqlite3.connect('scrape.db')


def createTables():
    videos = '''CREATE TABLE IF NOT EXISTS videos (
        id INTEGER PRIMARY KEY AUTOINCREMENT ,
        thread_id INTEGER NOT NULL,
        post_id INTEGER NOT NULL,
        video_id TEXT NOT NULL,
        date TEXT NOT NULL
    )
    '''
    db.execute(videos)

    playlists = '''CREATE TABLE IF NOT EXISTS playlists(
        id TEXT PRIMARY KEY,
        name TEXT,
        item_count INT
    )
    '''
    db.execute(playlists)

def playlistEntryKnown(playlist_id):
    sql = "SELECT * FROM playlists WHERE id=?"
    c = db.execute(sql, (playlist_id,))
    rows = c.fetchall()
    return len(rows)

def insertPlaylist(playlist):

    if(playlistEntryKnown(playlist['id'])):
        sql = "UPDATE playlists SET name=?, item_count=? WHERE id=?"
        db.execute(sql, (playlist['snippet']['title'], playlist['contentDetails']['itemCount'],playlist['id'],))
        db.commit()
        return False

    sql = "INSERT INTO playlists (id,name,item_count) VALUES(?,?,?)"
    db.execute(sql, (playlist['id'], playlist['snippet']['title'], playlist['contentDetails']['itemCount'],))
    db.commit()
    return True

def getPlaylistLessThan(count):
    sql = "SELECT id FROM playlists WHERE item_count < ?"
    c = db.execute(sql, (count,))
    rows = c.fetch()
    if(len(rows)==0):
        return False
    return rows[0]

def videoEntryKnown(video):
    sql = "SELECT id FROM videos WHERE thread_id=? AND post_id=? AND video_id=?"
    c = db.execute(sql, (video['tid'], video['pid'], video['yt'],))
    rows = c.fetchall()
    return len(rows)

def videoHasBeenPostedRecently(video):
    sql = "SELECT * FROM videos WHERE video_id=? AND id IN (SELECT id FROM videos ORDER BY id DESC LIMIT 25)"
    c = db.execute(sql, (video['yt'],))
    rows = c.fetchall()
    return len(rows)

def tooManyVidsPerPost(video):
    sql = "SELECT id FROM videos WHERE post_id=?"
    c = db.execute(sql, (video['pid'],))
    rows = c.fetchall()
    return len(rows)

def insertVideo(video):

    if(videoEntryKnown(video)>0):
        print("skipped", video)
        return False

    sql = "INSERT INTO videos (thread_id,post_id,video_id,date) VALUES(?,?,?,?)"
    db.execute(sql, (video['tid'], video['pid'], video['yt'], video['date'],))
    db.commit()

    
    if(videoHasBeenPostedRecently(video)>1):
        print("recent video_id", video, rows)
        return False

    if(tooManyVidsPerPost(video)>3):
        print("too many vids in post", video)
        return False

    return True
