import React from "react"
import {FreeCamera, Vector3, HemisphericLight, SceneLoader, MeshBuilder, Color4} from "@babylonjs/core";
import { useSlotProps } from "@mui/base";
import "@babylonjs/loaders";
import { SceneComponent } from "./sceneComponent";

let mesh;
const onSceneReady = (scene, meshDir, meshFileName) => {
    scene.clearColor = new Color4(0, 0, 0, 0)
    const canvas = scene.getEngine().getRenderingCanvas();
    const light = new HemisphericLight("light", new Vector3(0, 1, 0), scene);
    const camera = new FreeCamera("camera1", new Vector3(0, 5, -10), scene);
    SceneLoader.ImportMesh("", meshDir, meshFileName, scene, (meshes) => {mesh = meshes[0]});
    
    light.intensity = 0.7;
    camera.setTarget(Vector3.Zero());
    camera.attachControl(canvas, true);
    
    setTimeout(function() {console.log("mesh ", mesh); mesh.position = new Vector3(0, 1, 0); console.log("Scene ", scene); scene.render()}, 2000);
}

const onRender = (scene) => {
    if (mesh !== undefined) {
        const rpm = 10;
        const deltaT = scene.getEngine().getDeltaTime();

        mesh.rotation.y += (rpm / 60) * Math.PI * 2 * (deltaT / 1000);
    }
}

export function MeshRenderer(props) {
    return (
        <SceneComponent antialias meshFileName={props.meshFileName} onSceneReady={onSceneReady} onRender={onRender} id={useSlotProps.id} style={{width: "100%", height: "100%", outline: "none"}}/>
    )
}
