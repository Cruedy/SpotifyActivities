import logo from './logo.svg';
import './App.css';
import React, {useState, useEffect} from 'react';

function App() {
  const [playlist, setPlaylist] = useState("")

  useEffect(() => {
    fetch("/api/route").then(
      res => res.json()
    ).then(
      data => {
        setPlaylist(data.playlist)
        console.log(data)
      });
  }, [])
  return (
    <p>
      {playlist}
    </p>
  );
}

export default App;
