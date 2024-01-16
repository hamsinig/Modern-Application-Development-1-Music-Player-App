
#importing necessary modules
from flask import Blueprint, render_template, request, flash, redirect, url_for
from sqlalchemy import func
from flask_login import login_user, login_required, logout_user, current_user
from .models import User, Album, Song,Rating,Playlist  # Update this line
from . import db
from sqlalchemy import or_
from sqlalchemy.orm import joinedload





auth = Blueprint('auth', __name__)
#renders admin's page
@auth.route('/admin')
@login_required
def home():
    return render_template('admin/index.html')
#renders 
@auth.route('/admin/user/',methods=['GET', 'POST'])
@login_required
def user_table():
   
    
    users = User.query.filter(User.username != 'admin').all()

    return render_template('admin/user_table.html', users=users)
#the route which changes the permission of the albums and songs of creators when their status(Whitelist or blacklist) changes  
@auth.route('/admin/userperm/<int:id>', methods=['GET', 'POST'])
@login_required
def editt_perm_role(id):
    user = User.query.get(id)
    songs = db.session.query(
        Song
    ).join(
        User, Song.creator_id == User.id
    ).filter(
        User.id == id
    ).all()

    if user:
        if request.method == 'POST':
            new_perm = request.form.get('permission')
            user.role=new_perm
            db.session.commit()
            if new_perm == 'blacklist':
                new_flag_value = 'red' 
            else:
                new_flag_value='green'    

                for song in songs:
                    # Update the flag attribute for each song
                    
                    song.flag = new_flag_value

                # Commit the changes to the database after the loop
                db.session.commit()



    return redirect(url_for('auth.user_table'))
                 
#changing roles
@auth.route('/admin/user/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_user_role(id):
        user = User.query.get(id)
        if user:
            
            if request.method == 'POST':
                
            
                new_role = request.form.get('role') 

                
                user.role = new_role
                db.session.commit()
                if new_role=='creator':
                    user.permission='whitelist'

                    db.session.commit()
                else:
                    user.permission='blacklist'
                    db.session.commit()

                new_permission= request.form.get('permission')
                user.permission = new_permission
                db.session.commit()
                
                return redirect(url_for('auth.user_table'))
        return redirect(url_for('auth.user_table'))
#route which renders the playlist created by users
@auth.route('/playlist')
@login_required
def playlist():
    playlists = Playlist.query.filter_by(user_id=current_user.id).all()
    return render_template('user_dashboard.html', playlists=playlists)

# Route to handle the creation of a new playlist
@auth.route('/create_playlist/', methods=['POST'])
@login_required
def create_playlist():
    playlist_name = request.form.get('playlist_name')

    # Create a new playlist
    new_playlist = Playlist(user_id=current_user.id, name=playlist_name)
    db.session.add(new_playlist)
    db.session.commit()

    flash('Playlist created successfully!', 'success')
    return redirect(url_for('auth.explore'))


#route for admin to change song permissions
@auth.route('/admin/change_song_permissions/<int:Songid>/<string:flag>', methods=['GET', 'POST'])
@login_required
def change_song_permissions(Songid, flag):
    # Assuming 'flag' is a column in your database model
    song = Song.query.get(Songid)

    if song:
        # Toggle the value of 'flag'
        if flag == 'green':
            song.flag = 'red'
        else:
            song.flag = 'green'

        db.session.commit()

    return redirect(url_for('auth.song_table'))
#renders the page where admins can view all the songs
@auth.route('/admin/song/')
@login_required
def song_table():
      

        result = db.session.query(
            Song.Songid,
            Song.Song_name,
            Song.Song_Lyrics,
            Song.Song_genre,
            Song.Song_Artist,
            Song.Song_rating,
            Song.flag
        )



    

        return render_template('admin/song_table.html',songs=result)
    

#allowing admin to alter song details
@auth.route('/admin/edit_song/<int:Songid>', methods=['GET', 'POST'])
@login_required
def song_table_query(Songid): 
    song = Song.query.get(Songid)
    
    creator_name = db.session.query(User.username).join(Song, User.id == Song.creator_id).filter(Song.Songid == Songid).first()
    
    if request.method == 'POST':
        new_rating = request.form.get('Song_rating')
        
        if song:
            total_ratings = sum(rating.rating for rating in song.ratings)
            average_rating = total_ratings / len(song.ratings)
            song.Song_rating = average_rating
            db.session.commit()
            return redirect(url_for('auth.song_table'))
    return redirect(url_for('auth.song_table'))   
#allowing creators to delete songs
@auth.route('/delete_song/<int:Songid>',methods=['POST'])
@login_required
def deletee_song(Songid): 
    song = Song.query.get(Songid)
    if song:
        
       
        db.session.delete(song)
        db.session.commit()
   
    return redirect(url_for('auth.creator_dashboard'))  
         
#giving admin the power to delete songs
@auth.route('/admin/delete_song/<int:Songid>',methods=['POST'])
@login_required
def delete_song(Songid): 
    song = Song.query.get(Songid)
    if song:
        
       
        db.session.delete(song)
        db.session.commit()
   
    return redirect(url_for('auth.song_table'))            
#admin's page for viewing all the albums uploaded by all creators
@auth.route('/admin/album/')
@login_required
def album_table():
    


        result_query = (
            db.session.query(
                Album.album_id,
                Album.album_title,
                Album.album_artist,
                func.group_concat(Song.Song_name, ', ').label('songs'),
                Album.flag
            )
            .join(Song, Album.album_id == Song.album_id)
            
            .group_by(Album.album_id)
            .all()
            

        )
       
        
    

        return render_template('admin/album_table.html', albums=result_query)
#deleting a playlist
@auth.route('/delete_playlist/<int:playlist_id>', methods=['GET', 'POST'])
@login_required
def delete_playlist(playlist_id):
    playlist = Playlist.query.get_or_404(playlist_id)

    # Check if the current user is the owner of the playlist
    if current_user.id != playlist.user_id:
        flash('You do not have permission to delete this playlist.', 'error')
        return redirect(url_for('auth.user_dashboard'))

    try:
        db.session.delete(playlist)
        db.session.commit()
        flash('Playlist deleted successfully.', 'success')
    except Exception as e:
        print(str(e))
        flash('An error occurred while deleting the playlist.', 'error')

    return redirect(url_for('auth.user_dashboard'))

# Remove Song from Playlist route
@auth.route('/remove_song/<int:song_id>/<int:playlist_id>', methods=['GET', 'POST'])
@login_required
def remove_song(song_id, playlist_id):
    song = Song.query.get_or_404(song_id)
    playlist = Playlist.query.get_or_404(playlist_id)

    # Check if the current user is the owner of the playlist
    if current_user.id != playlist.user_id:
        flash('You do not have permission to remove songs from this playlist.', 'error')
        return redirect(url_for('auth.user_dashboard'))

    try:
        # Remove the song from the playlist
        playlist.songs.remove(song)
        db.session.commit()
        flash('Song removed from playlist successfully.', 'success')
    except Exception as e:
        print(str(e))
        flash('An error occurred while removing the song from the playlist.', 'error')

    return redirect(url_for('auth.user_dashboard'))



#changing album permissions and song permissions when album permissions are changed
@auth.route('/admin/change_album_permissions/<int:album_id>/<string:flag>', methods=['GET', 'POST'])
def change_album_permissions(album_id, flag):
    # Assuming 'flag' is a column in your database model
    album = Album.query.get(album_id)
    


    if album:
        if request.method=='POST':
            # Toggle the value of 'flag'
            if flag == 'green':
                album.flag = 'red'
                db.session.commit()
                for song in album.songs:
                    song.flag ='red'
                    db.session.commit()

            else:
                album.flag = 'green'
                for song in album.songs:
                    song.flag ='green'
                    db.session.commit()

            db.session.commit()

    return redirect(url_for('auth.album_table')) 
#deleting an album
@auth.route('/deletee_album/<int:album_id>',methods=['POST'])
@login_required
def deletee_album(album_id):
    album = Album.query.get(album_id)
    if album:
       
        db.session.delete(album)
        db.session.commit()

        
    return redirect(url_for('auth.creator_dashboard'))
#allowing creators to edit album
@auth.route('/edit_album_title/<int:album_id>', methods=['POST'])
@login_required
def edit_album(album_id):
    album = Album.query.get(album_id)

    # Check if the album exists and belongs to the current user
    
    new_album_title = request.form.get('new_album_title')

        # Update the album title
    album.album_title = new_album_title
    db.session.commit()
    return redirect(url_for('auth.creator_dashboard'))
#editting details of song by creators
@auth.route('/editt_song/<int:Songid>',methods=['POST'])
@login_required
def edit_song(Songid):
    if request.method=='POST':
        song = Song.query.get(Songid)
        song.Song_name = request.form.get('Song_name')
        song.Song_Lyrics = request.form.get('Song_Lyrics')
        db.session.commit()
        return redirect(url_for('auth.creator_dashboard'))


#adding songs to an album        
@auth.route('/addd_song/<int:album_id>/<string:Song_Artist>',methods=['POST'])
@login_required
def addd_song(album_id,Song_Artist):
    if request.method == 'POST':
        # Get the form data
        song_name = request.form.get('Song_name')
        song_lyrics = request.form.get('Song_Lyrics')
        song_genre = request.form.get('Song_genre')
        
        # Create a new Song object
        new_song = Song(
            Song_name=song_name,
            Song_Lyrics=song_lyrics,
            Song_Artist=Song_Artist,
            Song_genre=song_genre,
            album_id=album_id  # Assign the album_id
        )

        # Add the new song to the database
        db.session.add(new_song)
        db.session.commit()

        flash('Song added successfully!', 'success3')
        
        # Redirect to the creator_dashboard or wherever you want to go after adding a song
        return redirect(url_for('auth.creator_dashboard'))
#deleting an album
@auth.route('/admin/delete_album/<int:album_id>',methods=['POST'])
def delete_album(album_id):
    album = Album.query.get(album_id)
    if album:
       
        db.session.delete(album)
        db.session.commit()

        
    return redirect(url_for('auth.album_table'))

def update_average_rating(song):
    if not song.ratings:
        song.ratings = 0
    else:
        total_ratings = sum(rating.rating for rating in song.ratings)
        average_rating = total_ratings / len(song.ratings)
        

    # Commit the changes to the database
    db.session.commit()

    return average_rating
#rating an album
@auth.route('/rate/<int:song_id>', methods=['POST'])
@login_required
def rate_song(song_id):
    if request.method == 'POST':
        rating = request.form.get('rating')

        song = Song.query.get(song_id)
        existing_rating = Rating.query.filter_by(user_id=current_user.id, song_id=song_id).first()

        if existing_rating:
            flash("You've already rated this song",category='danger')
            return redirect(url_for('auth.explore'))

        else:
        # If the user hasn't rated the song, add the new rating
            new_rating = Rating(user_id=current_user.id, song_id=song_id, rating=rating)
            db.session.add(new_rating)

            total_ratings = sum(int(rating.rating) for rating in song.ratings)

            
            average_rating = total_ratings / len(song.ratings)
            song.Song_rating = average_rating
            
            db.session.commit()
            update_average_rating(song)

        # Update average rating
           

    # Render the explore page without the 'is_existing' flag
    return redirect(url_for('auth.explore'))
#renders admin's dashboard
@auth.route('/adminsdashboard')
def index():
    total_users = User.query.count()
    creators_count = User.query.filter(User.role == 'creator').count()
    users_count = User.query.filter(User.role != 'creator').count()
    songs_count = Song.query.count()
    unique_genres = db.session.query(Song.Song_genre).distinct().count()
    albums_count = Album.query.count()

    return render_template('admin/adminsdashboard.html',
                           total_users=total_users,
                           creators_count=creators_count,
                           users_count=users_count,
                           songs_count=songs_count,
                           unique_genres=unique_genres,
                           albums_count=albums_count)


# function whch adds new user to database
def add_user(username, email, password):
                new_user = User(username=username, email=email, password=password)
                db.session.add(new_user)
                db.session.commit()

#renders login page for user                
@auth.route('/login', methods=['GET', 'POST'])

def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        if user is not None:
            # Check if the password matches
            
            if user.password == password:
                login_user(user)
               
                return redirect(url_for('auth.user_dashboard'))

           
                
            else:
                flash('Incorrect password, try again.', category='error4')
        else:
            flash('Username does not exist.', category='error4')

    return render_template("login.html", user=current_user)
#allowing creators to add albums
@auth.route('/add_album', methods=['POST'])
@login_required
def add_album():
    if request.method == 'POST':
        album_title = request.form.get('album_title')

        
        new_album = Album(album_title=album_title, album_artist=current_user.username)

        db.session.add(new_album)
        db.session.commit()
        albumy = Album.query.filter_by(album_title=album_title).one()
        AlbId= albumy.album_id
        song_name = request.form.get('Song_name')
        song_lyrics = request.form.get('Song_Lyrics')
        song_genre = request.form.get('Song_genre')

       
        new_song = Song(Song_name=song_name, Song_Lyrics=song_lyrics, Song_genre=song_genre, Song_Artist=current_user.username,album_id=AlbId)

        # Add the new song to the database
        db.session.add(new_song)
        db.session.commit()
        

        flash('Album added successfully!', 'success1')

    return redirect(url_for('auth.creator_dashboard'))
#renders user's dashboard
@auth.route('/user_dashboard')
@login_required
def user_dashboard():
     
    
    playlists_with_songs = (
    Playlist.query
    .filter(Playlist.user_id == current_user.id)
    .join(Playlist.songs)
    
    
    .filter(User.permission == 'whitelist')
    .all()
)
   
    

    
    return render_template("user_dashboard.html", user=current_user,playlists_with_songs=playlists_with_songs)

#renders creator's dashboard along with the albums and songs uploaded by the creator
@auth.route('/creator_dashboard')
@login_required
def creator_dashboard():
        if current_user.role=='creator':
    
    
        
            albums = Album.query.filter_by(album_artist=current_user.username).all()
            result = db.session.query(
        Song.Songid,
        Song.Song_name,
        Song.Song_Lyrics,
        Song.Song_genre,
        Song.Song_Artist,
        Song.Song_rating,
        Song.flag
    ).filter(Song.Song_Artist == current_user.username).all()

            return render_template("creator_dashboard.html", user=current_user, albums=albums,songs=result)
        else:
            flash("You don't have access to creator's dashboard because you're not a creator ",category='error2')
            return redirect(url_for('auth.user_dashboard'))

       
   
        
#allows normal users to register as creator to upload music
@auth.route('/register_as_creator', methods=['POST'])
@login_required
def register_as_creator():
    username = request.form.get('username')
    password = request.form.get('password')

    # Check if the entered credentials match the current user
    if current_user.username == username and current_user.password == password:
        if current_user.role=='creator':
            flash('You have already registered as a creator, log in!', category='error2')
            return redirect(url_for('auth.user_dashboard'))
        
        else:# Update the role to 'creator'
            current_user.role = 'creator'
            current_user.permission='whitelist'
            db.session.commit()

        # Commit changes to the database
        

        flash('Successfully registered as a creator!', category='success3')
        return redirect(url_for('auth.creator_dashboard'))
        
    else:
        flash('Invalid credentials for creator registration.', category='error2')

    return redirect(url_for('auth.user_dashboard'))
#logging in as a creator for normal user
@auth.route('/login_as_creator', methods=['POST'])
@login_required
def creator_login():
    entered_username = request.form.get('username')
    entered_password = request.form.get('password')
    existing_user = User.query.filter_by(username=entered_username).first()

    if existing_user:
        if current_user.username == existing_user.username and existing_user.password== entered_password:
            if existing_user.role == 'creator':
                flash('Successfully logged in as a creator!', category='success3')
        
                return redirect(url_for('auth.creator_dashboard'))
            else:
                flash('You need to register as a creator first', category='error2')
                return redirect(url_for('auth.user_dashboard'))
               
        else:
            flash('You\'re logging in from a different user', category='error2')
            return redirect(url_for('auth.user_dashboard'))
            
    else:
        # Redirect to the login page with an error message if the login fails
        flash('Incorrect Username or Password', category='error2')
        return redirect(url_for('auth.user_dashboard'))
       

    
#allowing users to update their details
@auth.route('/update_details', methods=['POST'])
@login_required
def update_details():
    if request.method == 'POST':
        new_username = request.form.get('username')
        new_email = request.form.get('email')
        new_name = request.form.get('name')
        new_location = request.form.get('location')

        # Assuming you have a current_user object from Flask-Login
        current_user.username = new_username
        current_user.email = new_email
        current_user.name = new_name
        current_user.location = new_location

        # Commit changes to the database
        db.session.commit()

        # Redirect to the user dashboard or another page
        flash('Details updated successfully!', category='success2')
        return redirect(url_for('auth.user_dashboard'))

    
    flash('Failed to update details.', category='error2')
    return redirect(url_for('auth.user_dashboard'))

#the route which logs out the current user
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    r='false'
    flash("Logout done!")
    return redirect(url_for('auth.welcome'))


#allows signing up of new users
@auth.route('/signup1', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        existing_username = User.query.filter_by(username=username).first()
        # Check if email already exists
        existing_email = User.query.filter_by(email=email).first()

        
        if existing_email:
            flash('Email already exists. Please use a different email.', category='error')
        elif existing_username:
            flash('Username already exists. Please choose a different username.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(username) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif password1 is not None and len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')

        else:
            try:
                add_user(username,email,password1)
                db.session.commit()
                flash('Registration successful!', 'success')
                return redirect(url_for('auth.login'))

           
            except Exception as e:
                db.session.rollback()
                flash('Email ID/ already exists. Please use a different email.', 'error')
                return redirect(url_for('auth.signup'))


           
            
            
           
            
        
            
    
    return render_template("signup1.html")

#allows addition of new songs to existing playlist
@auth.route('/add_to_playlist/<int:Songid>', methods=['POST'])
@login_required
def add_to_playlist(Songid):
    if request.method == 'POST':
        playlist_id = request.form.get('playlist_id')

        user_playlists = Playlist.query.filter_by(user_id=current_user.id).all()

        playlist = Playlist.query.get(playlist_id)
        song = Song.query.get(Songid)

        if not playlist:
            flash('Invalid playlist.', 'danger')
        elif song in playlist.songs:
            flash('Song is already in the playlist.', 'warning')
        else:
            # Check if the song is linked to any other playlist for the current user
            linked_playlists = Playlist.query.filter(
                Playlist.user_id == current_user.id,
                Playlist.songs.any(Song.Songid == Songid)

            ).all()

            if linked_playlists:
                flash('Song is already linked to another playlist for the current user.', 'warning')
            else:
                # Add the song to the playlist
                playlist.songs.append(song)
                db.session.commit()
                flash('Song added to the playlist successfully!', 'success6')

        return redirect(url_for('auth.explore'))


#renders the page which searches
@auth.route('/search')
def search():
    return render_template('search.html')
#the route which renders the results
@auth.route('/search_results')
def search_results():
    query = request.args.get('query', '')
    
    
    is_artist_query = bool(Song.query.filter(Song.Song_Artist.ilike(f'%{query}%')).first())

    if is_artist_query:
        # Query only songs by the artist
        songs_by_artist = (
    Song.query
    .join(User, Song.Song_Artist == User.username)
    .filter(User.permission == 'whitelist', Song.flag == 'green', Song.Song_Artist.ilike(f'%{query}%'))
    .all()
)
        # Query albums by the artist
        albums_by_artist = (
    Album.query
    .join(User, Album.album_artist == User.username)
    .filter(User.permission == 'whitelist', Album.flag == 'green', Album.album_artist.ilike(f'%{query}%'))
    .options(joinedload(Album.songs))
    .all()
)

        return render_template('search.html', songs_by_artist=songs_by_artist, albums_by_artist=albums_by_artist)
    else:
        # Query songs and albums as before
        songs = Song.query.filter(
    or_(Song.Song_name.ilike(f'%{query}%'), Song.Song_Artist.ilike(f'%{query}%')),
    Song.flag == 'green'
).all()
        albums = (
    Album.query
    .join(User, Album.album_artist == User.username)
    .filter(User.permission == 'whitelist', Album.album_title.ilike(f'%{query}%'), Album.flag == 'green', Album.songs.any(Song.flag == 'green'))
    .options(joinedload(Album.songs))
    .all()
)
        songs_by_genre = (
    Song.query
    .join(Album, Song.album_id == Album.album_id)
    .join(User, Song.Song_Artist == User.username)
    .filter(Song.Song_genre.ilike(f'%{query}%'), Song.flag == 'green', User.permission == 'whitelist')
    .all()
)

        return render_template('search.html', songs=songs, albums=albums,songs_by_genre=songs_by_genre)
#the home page    
@auth.route('/')
def welcome():
    return render_template("welcome.html")
#explore page which renders the recommended songs
@auth.route('/explore')
@login_required
def explore():
    
   
    
    all_albums=Album.query.all()
    all_users=User.query.all()
    playlist_names = Playlist.query.with_entities(Playlist.id, Playlist.name).filter_by(user_id=current_user.id).all()
    result = (
    db.session.query(Song)
    .join(Album, Song.album_id == Album.album_id)
    .join(User, Song.Song_Artist == User.username)
    .filter(Song.flag == 'green', Album.flag == 'green', User.permission == 'whitelist')
    .all()
)

# Sort songs by average rating in descending order
    recommended_songs_data = sorted(result, key=lambda x: x.Song_rating, reverse=True)

    
    return render_template("explore.html", playlist_names=playlist_names, recommended_songs=recommended_songs_data, )
@auth.route('/admin/login', methods=['POST'])
def admin_login():
    admin_username = request.form.get('adminUsername')
    admin_password = request.form.get('adminPassword')


    admin_user = User.query.filter_by(username=admin_username, password=admin_password).first()

    if admin_user:
        # Successful login
        login_user(admin_user)
        return redirect(url_for('auth.index'))
    else:
        # Incorrect username or password
        flash("Incorrect username or password", category="danger")
        return redirect(url_for('auth.welcome'))
