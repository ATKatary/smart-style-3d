import '../landing/landing.css';
import * as React from 'react';
import { Button } from '@mui/material';

function NavBar() {
  const sections = ["API", "Research", "About"];

  return ( 
    <div className="flex width-100 align-center">
        {sections.map((section, i) => <Button key={i} style={{width: "100px", margin: "15px", color: "#fff", borderRadius: "25px", paddingRight: "20px", paddingLeft: "20px"}}>{section}</Button>)}
    </div>
  );
}

export default NavBar;