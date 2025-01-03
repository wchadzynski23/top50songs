import csv
from app import app, db, Song, Settings

def init_db():
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Create default settings
        settings = Settings(
            hero_title="Top 50 Songs of 2024",
            hero_description="Discover the most anticipated albums and songs of 2024",
            stats_enabled=True
        )
        db.session.add(settings)
        
        # Read songs from CSV and track seen titles to avoid duplicates
        seen_titles = set()
        with open('songs.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rank = 1
            for row in reader:
                # Split description from song/album title if present
                title_parts = row['song_or_album'].split('\n', 1)
                title = title_parts[0].strip()
                
                # Skip if we've already seen this title
                if title in seen_titles:
                    continue
                    
                seen_titles.add(title)
                description = title_parts[1].strip() if len(title_parts) > 1 else ''
                
                # Get the first line of the link (clean URL)
                link = row['link'].split('\n')[0].strip() if row['link'] else ''
                
                song = Song(
                    rank=rank,
                    artist=row['artist'].strip(),
                    title=title,
                    description=description,
                    link=link
                )
                db.session.add(song)
                rank += 1
        
        db.session.commit()

if __name__ == '__main__':
    init_db()
    print("Database initialized successfully!")
