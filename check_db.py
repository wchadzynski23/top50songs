from app import db, Song, User
import os
from dotenv import load_dotenv

load_dotenv()

def check_database():
    try:
        # Check users
        users = User.query.all()
        print(f"\nUsers in database: {len(users)}")
        for user in users:
            print(f"- Username: {user.username}")

        # Check songs
        songs = Song.query.all()
        print(f"\nSongs in database: {len(songs)}")
        for song in songs[:5]:  # Show first 5 songs
            print(f"- {song.title} by {song.artist}")
        
        if len(songs) > 5:
            print(f"... and {len(songs) - 5} more songs")

        print("\nDatabase connection successful!")
        
    except Exception as e:
        print(f"Error connecting to database: {str(e)}")

if __name__ == "__main__":
    check_database()
