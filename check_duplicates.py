from app import app, db, Song
from collections import Counter

def check_duplicates():
    with app.app_context():
        songs = Song.query.order_by(Song.rank).all()
        counts = Counter(s.title for s in songs)
        duplicates = {k: v for k, v in counts.items() if v > 1}
        if duplicates:
            print("Found duplicate songs:", duplicates)
            # Delete duplicates
            for title in duplicates:
                dups = Song.query.filter_by(title=title).all()
                # Keep the first one, delete the rest
                for dup in dups[1:]:
                    db.session.delete(dup)
            db.session.commit()
            print("Duplicates removed.")
        else:
            print("No duplicates found.")
