document.addEventListener('DOMContentLoaded', async () => {
    const songsContainer = document.querySelector('.songs-container');

    async function loadSongs() {
        try {
            const response = await fetch('songs.csv');
            const csvText = await response.text();
            const songs = parseCSV(csvText);
            displaySongs(songs);
        } catch (error) {
            console.error('Error loading songs:', error);
            songsContainer.innerHTML = `
                <div class="error">
                    Error loading songs. Please make sure the CSV file is available.
                </div>
            `;
        }
    }

    function parseCSV(csvText) {
        const lines = csvText.split('\n').filter(line => line.trim());
        const songs = [];
        let currentSong = null;
        let currentField = '';
        let inQuotes = false;

        // Skip header
        for (let i = 1; i < lines.length; i++) {
            const line = lines[i];
            
            for (let char of line) {
                if (char === '"') {
                    inQuotes = !inQuotes;
                } else if (char === ',' && !inQuotes) {
                    if (!currentSong) {
                        currentSong = { artist: currentField.trim(), song_or_album: '', link: '' };
                    } else {
                        currentSong.song_or_album = currentField.trim();
                    }
                    currentField = '';
                } else {
                    currentField += char;
                }
            }
            
            // End of line
            if (currentField.includes('https://')) {
                currentSong.link = currentField.trim();
                songs.push(currentSong);
                currentSong = null;
            } else if (currentSong) {
                currentSong.song_or_album += (currentSong.song_or_album ? '\n' : '') + currentField.trim();
            }
            currentField = '';
        }

        return songs.map((song, index) => {
            const songLines = song.song_or_album.split('\n');
            return {
                rank: index + 1,
                artist: song.artist.replace(/^"|"$/g, ''),
                title: songLines[0].replace(/^"|"$/g, ''),
                description: songLines.slice(1).join('\n').replace(/^"|"$/g, ''),
                link: song.link.replace(/^"|"$/g, '')
            };
        });
    }

    function displaySongs(songs) {
        songsContainer.innerHTML = songs.map(song => `
            <div class="song-card">
                <div class="song-rank">#${song.rank}</div>
                <div class="song-artist">${song.artist}</div>
                <div class="song-title">${song.title}</div>
                <div class="song-description">${song.description}</div>
                <a href="${song.link}" class="song-link" target="_blank" rel="noopener noreferrer">
                    Listen on Spotify
                </a>
            </div>
        `).join('');
    }

    // Initial load
    loadSongs();
});
