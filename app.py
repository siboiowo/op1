from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)
db_path = 'music_streaming_platform_final.db'

# Helper function to connect to the database
def get_db_connection():
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Allows access by column name
    return conn

# Home Page
@app.route('/')
def index():
    return render_template('index.html')

# Register User
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO Users (username) VALUES (?)", (username,))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))
        except sqlite3.IntegrityError:
            return "Username already exists."
    return render_template('register.html')

# Create Playlist
@app.route('/create_playlist', methods=['GET', 'POST'])
def create_playlist():
    if request.method == 'POST':
        playlist_name = request.form['playlist_name']
        username = request.form['username']
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if user exists
        cursor.execute("SELECT id FROM Users WHERE username = ?", (username,))
        user = cursor.fetchone()
        if user:
            cursor.execute("INSERT INTO playlists (name) VALUES (?)", (playlist_name,))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))
        else:
            conn.close()
            return "User does not exist."
    return render_template('create_playlist.html')

# Add Track to Playlist
@app.route('/add_track', methods=['GET', 'POST'])
def add_track():
    if request.method == 'POST':
        playlist_name = request.form['playlist_name']
        track_name = request.form['track_name']
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get playlist and track IDs
        cursor.execute("SELECT id FROM playlists WHERE name = ?", (playlist_name,))
        playlist = cursor.fetchone()
        cursor.execute("SELECT id FROM tracks WHERE name = ?", (track_name,))
        track = cursor.fetchone()
        
        if playlist and track:
            cursor.execute("INSERT OR IGNORE INTO playlist_tracks (playlist, track) VALUES (?, ?)",
                           (playlist['id'], track['id']))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))
        else:
            conn.close()
            return "Playlist or track not found."
    return render_template('add_track.html')

# Search Songs
@app.route('/search', methods=['GET', 'POST'])
def search():
    songs = []
    if request.method == 'POST':
        title = request.form.get('title')
        artist = request.form.get('artist')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        query = '''SELECT tracks.name, artists.name, tracks.duration, tracks.release_date 
                   FROM tracks
                   JOIN track_artists ON tracks.id = track_artists.track
                   JOIN artists ON track_artists.artist = artists.id'''
        
        conditions = []
        params = []
        if title:
            conditions.append("tracks.name LIKE ?")
            params.append(f"%{title}%")
        if artist:
            conditions.append("artists.name LIKE ?")
            params.append(f"%{artist}%")
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        cursor.execute(query, params)
        songs = cursor.fetchall()
        conn.close()
    return render_template('search.html', songs=songs)

# Play Playlist
@app.route('/play_playlist', methods=['GET', 'POST'])
def play_playlist():
    playlist_name = None
    playlist_tracks = []

    if request.method == 'POST':
        playlist_name = request.form['playlist_name']

        # Connect to the database
        conn = sqlite3.connect('music_streaming_platform_final.db')
        cursor = conn.cursor()

        # SQL query to get tracks and artists for the specified playlist
        query = """
        SELECT tracks.name AS track_name, artists.name AS artist_name
        FROM playlist_tracks
        JOIN tracks ON playlist_tracks.track = tracks.id
        JOIN track_artists ON track_artists.track = tracks.id
        JOIN artists ON track_artists.artist = artists.id
        JOIN playlists ON playlist_tracks.playlist = playlists.id
        WHERE playlists.name = ?;
        """
        cursor.execute(query, (playlist_name,))
        playlist_tracks = cursor.fetchall()

        # Close the connection
        conn.close()

    return render_template('play_playlist.html', playlist_tracks=playlist_tracks, playlist_name=playlist_name)


# Run the app
if __name__ == '__main__':
    app.run(debug=True)
