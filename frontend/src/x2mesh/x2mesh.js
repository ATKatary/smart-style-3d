import './x2mesh.css';
import * as React from 'react';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import { IconButton, TextareaAutosize, Typography } from '@mui/material';
import { StyleOption, Notify } from '../utils/utils';
import PlayCircleIcon from '@mui/icons-material/PlayCircle';
import { MeshRenderer } from './meshRenderer';

let socket;
const startSocket = () => new WebSocket(`ws://0.0.0.0:8000/ws/api/imad/upload/`);

function X2Mesh() {
  const [notifyOpen, setNotifyOpen] = React.useState(false);
  const [notifyMessage, setNotifyMessage] = React.useState("");

  const [globalStyling, setGlobalStyling] = React.useState(false);
  const [selectiveStyling, setSelectiveStyling] = React.useState(false);

  const [meshDir, setMeshDir] = React.useState("../media/model/");
  const [meshFileName, setMeshFileName] = React.useState("default.obj");

  const [stylePrompt, setStylePrompt] = React.useState("");

  const [faces, setFaces] = React.useState(297298);
  const [vertices, setVertices] = React.useState(337768);
  const [vertexNormals, setVertexNormals] = React.useState(0);

  const stringify = (t) => t? "on" : "off"
  const loadMesh = (event) => {
    const data = JSON.parse(event.data);
    const meshDir = data['meshDir'];
    const meshFileName = data['meshFileName'];

    const f = data['f'];
    const v = data['v'];
    const vn = data['vn'];

    setFaces(f);
    setVertices(v);
    setVertexNormals(vn);

    // setMeshDir(meshDir);
    // setMeshFileName(meshFileName);
    console.log(`mesh path ${meshDir}${meshFileName}`);
  }

  const selectMesh = (event) => {
    const reader = new FileReader()
    reader.onload = upload;
    reader.readAsText(event.target.files[0])
  }

  const upload = (event) => {
    socket.send(
      JSON.stringify({
        "mesh": event.target.result
      })
    )
  }
  if (socket === undefined) {socket = startSocket(); socket.onmessage = loadMesh;}

  return ( 
    <div className="flex column align-center width-100">
      <Typography variant="h3" className="align-self-start" style={{marginTop: "20px", fontFamily: "'Martel Sans', sans-serif", marginLeft: "50px"}}>X2Mesh</Typography>
      
      <div className="flex align-center width-80 margin-15px">
        {/*** Controls ***/}
        <div style={{width: "5%", background: "#646464"}} className="hcalc-28-2 flex column align-center box-shadow-4">
          <input hidden accept=".obj" type="file" id="meshUpload" onChange={selectMesh}/>
          <PlayCircleIcon  sx={{color: "#fff"}} style={{height: "25px", width: "90px"}} className="pointer margin-15px" onClick={() => {}}/>
          <CloudUploadIcon sx={{color: "#fff"}} style={{height: "25px", width: "90px"}} className="pointer margin-15px" onClick={() => {document.getElementById("meshUpload").click();}}/>
        </div>

        {/*** Mesh ***/}
        <div className="flex" style={{width: "95%", height: "max(28vw, 336px)"}}>
          {/*** Renderer ***/}
          <div style={{width: "95%", height: "100%", outline: "1px solid #646464"}} className="box-shadow-4">
            <MeshRenderer id="meshRenderer" meshDir={meshDir} meshFileName={meshFileName}/>
          </div>

          {/*** Info ***/}
          <div className="mesh-info box-shadow-4 flex column" style={{padding: "10px"}}>
            <Typography style={{fontWeight: "600", fontFamily: "'Martel Sans', sans-serif"}}>Mesh Info</Typography>
            <Typography style={{marginLeft: "10px", fontFamily: "'Martel Sans', sans-serif"}}>faces: {faces}</Typography>
            <Typography style={{marginLeft: "10px", fontFamily: "'Martel Sans', sans-serif"}}>vertices: {vertices}</Typography>
            <Typography style={{marginLeft: "10px", fontFamily: "'Martel Sans', sans-serif"}}>vertex normals: {vertexNormals}</Typography>
          </div>
        </div>
      </div>

      {/*** Text prompt ***/}
      <div className="flex column align-center width-100">
        <div className="flex" style={{width: "75%"}}>
          <StyleOption label={"Global styling"} value={globalStyling} setValue={() => {setGlobalStyling(!globalStyling); setNotifyMessage(`Global styling turned ${stringify(!globalStyling)}`); setNotifyOpen(true)}}/>
          <StyleOption label={"Selective styling"} value={selectiveStyling} setValue={() => {setSelectiveStyling(!selectiveStyling); setNotifyMessage(`Selective styling turned ${stringify(!selectiveStyling)}`); setNotifyOpen(true)}}/>
        </div>
        <TextareaAutosize 
          placeholder="input stylization prompt, e.g: A beautiful vase made out of bricks" 
          style={{resize: "none", padding: "15px"}} 
          className="width-80 box-shadow-4 no-outline no-border" 
          value={stylePrompt}
          onChange={(event) => {setStylePrompt(event.target.value); console.log(stylePrompt)}}
          minRows={1} 
          maxRows={1}/>
      </div>

      <Notify open={notifyOpen} handleClose={() => setNotifyOpen(false)} message={notifyMessage}/>
    </div>
  );
}

export default X2Mesh;