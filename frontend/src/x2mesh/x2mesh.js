import './x2mesh.css';
import React, {useState} from 'react';
import { MeshRenderer } from './meshRenderer';
import { Typography, Button } from '@mui/material';
import { MeshInfo, MeshControls, PromptField, StyleControls } from './helpers';

let socket;
let x;
const startSocket = () => new WebSocket(`ws://0.0.0.0:8000/ws/api/imad/upload/`);

function X2Mesh() {
  /*** Mesh Info ***/
  const [i, setI] = useState(1);
  const [meshURL, setMeshURL] = useState(undefined);
  const [stylizedMeshURL, setStylizedMeshURL] = useState(undefined);
  const [f, setF] = useState(42618);
  const [v, setV] = useState(21311);
  const [vn, setVn] = useState(21311);
  const [gs, setGS] = useState(false);
  const [ss, setSS] = useState(false);
  const [styleEmpty, setStyleEmpty] = useState(true);

  const loadMesh = (event) => {
    const data = JSON.parse(event.data);
    
    setF(data['f'])
    setV(data['v'])
    setVn(data['vn'])
    console.log(`uploaded mesh info:\n`, data);
  }
  
  if (socket === undefined) {socket = startSocket(); socket.onmessage = loadMesh;}

  const models = require.context("../media/models", true, /^\.\/.*\.obj$/);

  const getName = (path) => path.split("/").pop();

  const stylize = (event) => {
    setStyleEmpty(false);
    if (i % 2 === 1) setI(i + 1);
    const text2meshPrompt = document.getElementById("text2meshPrompt");
    socket.send(JSON.stringify({"type": "text2mesh", "data": text2meshPrompt.value}))
  }

  return ( 
    <div className="flex column align-center width-100">
      <Typography variant="h3" className="align-self-start" style={{marginTop: "20px", fontFamily: "'Martel Sans', sans-serif", marginLeft: "50px"}}>SmartStyle3D</Typography>
      
      <div className="flex align-center width-80 margin-15px">
        {/*** Controls ***/}
        <MeshControls socket={socket} setMesh={setMeshURL} i={i} setI={setI} setStyleEmpty={setStyleEmpty}/>

        {/*** Mesh ***/}
        <div className="flex" style={{width: "95%", height: "max(28vw, 336px)"}}>
          {/*** Renderer ***/}
          <MeshRenderer id={`meshRenderer`} name={getName(models("./mesh.obj"))} url={meshURL} className={`mesh-${i % 2}`} rotate={false}/>
          <MeshRenderer id={`meshRenderer2`} name={getName(models("./mesh_stylized.obj"))} url={stylizedMeshURL} className={`mesh-${(i + 1) % 2}`} rotate={true} empty={styleEmpty}/>

          {/*** Info ***/}
          <MeshInfo f={f} v={v} vn={vn}/>
        </div>
      </div>
          
      {/*** Text prompt ***/}
      <div className="flex column align-center width-100">
        <StyleControls gs={gs} ss={ss} setGS={setGS} setSS={setSS}/>
        <PromptField stylize={stylize}/>
      </div>
    </div>
  );
}

export default X2Mesh;

