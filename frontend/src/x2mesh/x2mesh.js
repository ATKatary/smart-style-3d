import './x2mesh.css';
import * as React from 'react';
import { Typography } from '@mui/material';
import { MeshRenderer } from './meshRenderer';
import { MeshInfo, MeshControls, PromptField, StyleControls } from './helpers';

let socket;
let x;
const startSocket = () => new WebSocket(`ws://0.0.0.0:8000/ws/api/imad/upload/`);

function X2Mesh() {
  /*** Mesh Info ***/
  const [f, setF] = React.useState(undefined);
  const [v, setV] = React.useState(undefined);
  const [vn, setVn] = React.useState(undefined);
  const [gs, setGS] = React.useState(false);
  const [ss, setSS] = React.useState(false);
  const [stylePrompt, setStylePrompt] = React.useState("");

  const loadMesh = (event) => {
    const data = JSON.parse(event.data);
    data.name = getName(models(`./${data.name}.obj`))

    setF(parseInt(data.f))
    setV(parseInt(data.v))
    setVn(parseInt(data.vn))

    console.log(`uploaded mesh info:\n`, data);
  }
  
  if (socket === undefined) {socket = startSocket(); socket.onmessage = loadMesh;}
  if (x === undefined) {setTimeout(() => {socket.send(JSON.stringify({"mesh": ""}))}, 2000); x = 1;}

  const models = require.context("../media/models", true, /^\.\/.*\.obj$/);

  const getName = (path) => {
    const fileName = path.split("/").pop()
    const n = fileName.length;
    return fileName.substring(0, n - 4);
  }

  const mesh = {
    dir: "/static/media/",
    name: getName(models("./mesh.obj")),
    ext: ".obj"
  }

  const stylizedMesh = {...mesh}
  stylizedMesh.name = getName(models("./mesh_stylized.obj"))

  return ( 
    <div className="flex column align-center width-100">
      <Typography variant="h3" className="align-self-start" style={{marginTop: "20px", fontFamily: "'Martel Sans', sans-serif", marginLeft: "50px"}}>SmartStyle3D</Typography>
      
      <div className="flex align-center width-80 margin-15px">
        {/*** Controls ***/}
        <MeshControls socket={socket}/>

        {/*** Mesh ***/}
        <div className="flex" style={{width: "95%", height: "max(28vw, 336px)"}}>
          {/*** Renderer ***/}
          <MeshRenderer id={`meshRenderer`} meshInfo={mesh}/>
          <MeshRenderer id={`meshRenderer2`} meshInfo={stylizedMesh}/>

          {/*** Info ***/}
          <MeshInfo f={f} v={v} vn={vn}/>
        </div>
      </div>
          
      {/*** Text prompt ***/}
      <div className="flex column align-center width-100">
        <StyleControls gs={gs} ss={ss} setGS={setGS} setSS={setSS}/>
        <PromptField prompt={stylePrompt} setPrompt={setStylePrompt} stylize={() => {}}/>
      </div>
    </div>
  );
}

export default X2Mesh;

