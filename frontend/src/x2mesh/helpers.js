import './x2mesh.css';
import * as React from 'react';
import SendIcon from '@mui/icons-material/Send';
import { StyleOption, Notify } from '../utils/utils';
import PlayCircleIcon from '@mui/icons-material/PlayCircle';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import { TextareaAutosize, Typography, IconButton, Tooltip, Button } from '@mui/material';


/**
 * 
 * @param {*} props a map containing the mesh info which includes the number of face (f), vertices (v), and vertex normals (vn)
 * @returns a gui displaying the mesh info
 */
export function MeshInfo(props) {
    return (
        <div className="mesh-info box-shadow-4 flex column" style={{padding: "10px"}}>
            <div className="flex column">
                <Typography style={{fontWeight: "600", fontFamily: "'Martel Sans', sans-serif"}}>Mesh Info</Typography>
                <Typography style={{marginLeft: "10px", fontFamily: "'Martel Sans', sans-serif"}}>faces: {props.f}</Typography>
                <Typography style={{marginLeft: "10px", fontFamily: "'Martel Sans', sans-serif"}}>vertices: {props.v}</Typography>
                <Typography style={{marginLeft: "10px", fontFamily: "'Martel Sans', sans-serif"}}>vertex normals: {props.vn}</Typography>
            </div>
        </div>
    )
}

/**
 * 
 * @param {*} props 
 * @returns 
 */
export function PromptField(props) {
    return (
        <div className="flex width-80">
            <TextareaAutosize 
            id="text2meshPrompt"
            placeholder="input stylization prompt, e.g: A beautiful vase made out of bricks" 
            style={{resize: "none", padding: "15px", width: "65%"}} 
            className="box-shadow-4 no-outline no-border" 
            minRows={1} 
            maxRows={1}/>
            {/* <Tooltip title="Stylize">
                <IconButton style={{marginLeft: "10px"}} onClick={props.stylize}><SendIcon /></IconButton>
            </Tooltip> */}
            <Button style={{marginLeft: "10px"}} onClick={props.stylize}>Stylize</Button>
        </div>

    )
}

/**
 * 
 * @param {*} props 
 * @returns 
 */
export function MeshControls(props) {
    const selectMesh = (event) => {
        const reader = new FileReader()
        reader.onload = upload;
        reader.readAsText(event.target.files[0])
    }
    const upload = (event) => {
        const mesh = event.target.result;
        const blob = new Blob([mesh])
        const url = URL.createObjectURL(blob)
        
        if (props.i % 2 === 0) props.setI(props.i + 1) 
        props.setStyleEmpty(true);

        props.setMesh(url)
        props.socket.send(JSON.stringify({"type": "upload","data": event.target.result}));
    }

    return (
        <div style={{width: "5%", background: "#646464"}} className="hcalc-28-2 flex column align-center box-shadow-4">
            <input hidden accept=".obj" type="file" id="meshUpload" onChange={selectMesh}/>
            <Tooltip title="stylize">
               <PlayCircleIcon  sx={{color: "#fff"}} style={{height: "25px", width: "90px"}} className="pointer margin-15px" onClick={() => {}}/>
            </Tooltip>
            <Tooltip title="upload">
                <CloudUploadIcon sx={{color: "#fff"}} style={{height: "25px", width: "90px"}} className="pointer margin-15px" onClick={() => {document.getElementById("meshUpload").click();}}/>
            </Tooltip>
        </div>
    )
}

/**
 * 
 * @param {*} props 
 * @returns 
 */
export function StyleControls(props) {
    const stringify = (t) => t? "on" : "off";
    const [notifyOpen, setNotifyOpen] = React.useState(false);
    const [notifyMessage, setNotifyMessage] = React.useState("");
    
    return (
        <>
            <div className="flex" style={{width: "75%"}}>
                <StyleOption label={`Global styling`} value={props.gs} setValue={() => {props.setGS(!props.gs); setNotifyMessage(`Global styling turned ${stringify(!props.gs)}`); setNotifyOpen(true)}}/>
                <StyleOption label={`Selective styling`} value={props.ss} setValue={() => {props.setSS(!props.ss); setNotifyMessage(`Selective styling turned ${stringify(!props.ss)}`); setNotifyOpen(true)}}/>

            </div>
            <Notify open={notifyOpen} handleClose={() => setNotifyOpen(false)} message={notifyMessage}/>
        </>
    )
  }