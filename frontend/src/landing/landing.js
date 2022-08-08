import './landing.css';
import * as React from 'react';
import X2Mesh from '../x2mesh/x2mesh';
import { Button } from '@mui/material';
import NavBar from '../navbar/navbar';

function Landing() {
  const sections = ["Paper", "Code", "Demos"];

  return ( 
    <div className="flex column width-100 align-center">
        <div className="flex align-center column landing-1 width-100" style={{height: "max(40vw, 480px)"}}>
            <NavBar />
        </div>
        <div style={{marginTop: "min(-10vw, -120px)", width: "87%"}} className="flex justify-end">
            {sections.map((section, i) => <Button key={i} variant="contained" className="landing-button">{section}</Button>)}
        </div>
        <div id="demo" style={{width: "90%", margin: "20px", marginTop: "50px"}}>
            <X2Mesh />
        </div>
    </div>
  );
}

export default Landing;