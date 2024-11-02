import './App.css';
import React, { useState, useEffect } from 'react';

function App() {
  const [playlist, setPlaylist] = useState("");
  const [error, setError] = useState(null);

  useEffect(() => {
    const token = sessionStorage.getItem("spotify_token"); // Check for a token in session storage

    // Check if we are on the authorize page
    const urlParams = new URLSearchParams(window.location.search);
    const code = urlParams.get('code');

    if (code) {
      // If there is a code, send it to the backend to get the token
      fetch("/authorize", {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ code })
      })
        .then(res => {
          if (!res.ok) {
            throw new Error('Failed to authorize');
          }
          return res.json();
        })
        .then(data => {
          if (data.status === "success") {
            sessionStorage.setItem("spotify_token", data.token); // Store the token
            window.location.href = '/getTracks'; // Redirect to /getTracks after successful login
          } else {
            throw new Error('Authorization failed');
          }
        })
        .catch(err => {
          console.error(err);
          setError(err.message);
        });
    } else if (token) {
      fetch("/getTracks") // Fetch tracks after successful login
        .then(res => {
          if (!res.ok) {
            throw new Error('Failed to fetch tracks');
          }
          return res.json();
        })
        .then(data => {
          setPlaylist(data.tracks); // Assuming data.tracks is an array of track IDs
          console.log('Fetched tracks:', data.tracks);
        })
        .catch(err => {
          console.error(err);
          setError(err.message);
        });
    } else {
      fetch("/login")
        .then(res => {
          if (!res.ok) {
            throw new Error('Failed to get login URL');
          }
          return res.json();
        })
        .then(data => {
          window.location.href = data.auth_url; // Redirect to Spotify login
        })
        .catch(err => {
          console.error(err);
          setError(err.message);
        });
    }
  }, []);

  return (
    <div>
      {error && <p>Error: {error}</p>}
      {playlist && <p>Your Playlist: {playlist.join(', ')}</p>}
    </div>
  );
}

export default App;
