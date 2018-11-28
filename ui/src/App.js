import React, { Component } from 'react';
import './App.css';
import Map from './glmap';
import Header from './header';
import {getURL} from './urls';

class App extends Component {
  render() {
    return (
      <div className="App">
        <Map
          URL={getURL.SimplifiedGeojson()}
          paintProp={'colour'}
        />
        <Header />        
      </div>
    );
  }
}

export default App;
