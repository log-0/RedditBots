import praw # simple interface to the reddit API, also handles rate limiting of requests
import time
import sqlite3
import re
 
SUMMONTEXT = "(\w+)-+ass\s+(\w+)" # MAKE A REGEX TO FIND A SUMMON TEXT
 
#  Import Settings from Config.py
try:
    import Config
    USERNAME = Config.USERNAME
    PASSWORD = Config.PASSWORD
    USERAGENT = Config.USERAGENT
    MAXPOSTS = Config.MAXPOSTS
    SUBREDDIT = 'all'
    print("Loaded Config")
except ImportError:
    print("Error Importing Config.py")
    
WAIT = 2
 
banned_words = ['fat', 'than', 'it', 'half', 'that']
 
r = praw.Reddit(USERAGENT)
r.login(USERNAME, PASSWORD)
 
sql = sqlite3.connect('comments.db')
cur = sql.cursor()
cur.execute('CREATE TABLE IF NOT EXISTS posts(CID TEXT)')
print('Loaded SQL Database')
sql.commit()
 
def scan():
    stream = praw.helpers.comment_stream(r, 'all')
    for comment in stream:
    
        cbody = comment.body
        cid = comment.id
        
        cauthor = comment.author
        if cauthor is USERNAME:
            continue
        
        if len(cbody) > 25:
            continue
 
        match = re.search(SUMMONTEXT, cbody)
        if not match:
            continue
                
        cur.execute('SELECT * FROM posts WHERE CID=?', [cid])
        if not cur.fetchone():
            print("Found a summon comment")
            
            #DO STUFF HERE    
            if match:
                word1 = match.group(1)
                
                if word1 in banned_words:
                    continue
                
                word2 = match.group(2)
                
                if word2 in banned_words:
                    continue
                    
                print(match.group())
                print(cbody)
                cbody = cbody.replace(match.group() ,"**"+word1+" ass-"+word2+"**")
                print(cbody)
            else:
                continue
                
            print('Replying to ' + cid)
            comment.reply(cbody +  "\n \n \n ^[Reference](http://xkcd.com/37/)")
            
            cur.execute('INSERT INTO posts VALUES(?)', [cid])
            sql.commit()
        else:
            print("Already replied to that comment")
                
    
while True:
    try:
        scan()
    except Exception as e:
        print("ERR", e)
        print('Sleeping ' + str(WAIT))
    time.sleep(WAIT)
