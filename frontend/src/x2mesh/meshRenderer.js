import React from "react";
import "@babylonjs/loaders";
import { useSlotProps } from "@mui/base";
import { SceneComponent } from "./sceneComponent";
import {ArcRotateCamera, Vector3, HemisphericLight, SceneLoader, StandardMaterial, Color3} from "@babylonjs/core";
import {OBJFileLoader} from "@babylonjs/loaders";

export function MeshRenderer(props) {
    let mesh;
    const onSceneReady = (scene, name, url) => {
        scene.clearColor = new Color3.White();
        const mat = new StandardMaterial("mat", scene);
        const canvas = scene.getEngine().getRenderingCanvas();
        const light = new HemisphericLight("light", new Vector3(0, 0, 0), scene);
        const camera = new ArcRotateCamera("camera1", -Math.PI / 2, Math.PI / 2, 12, new Vector3(0, 0, 9), scene);
        mat.wireframe = true;
        light.intensity = 0.7;
        camera.attachControl(canvas, true);
        // const axes = new AxesViewer(scene, 1)
        mat.emissiveColor = Color3.Gray();
        OBJFileLoader.IMPORT_VERTEX_COLORS = true;
        if (url !== undefined) SceneLoader.Append("", url, scene, function (meshes) {mesh = meshes.meshes[0]; mesh.material = mat;}, undefined, undefined, ".obj");
        else if (!props.empty) SceneLoader.ImportMesh("", "/static/media/", name, scene, (meshes) => {mesh = meshes[0]; mesh.position = new Vector3(0, 0, 0); mesh.material = mat;});
        
        console.log("mesh ", mesh);
        console.log("Scene ", scene); 
    }

    const onRender = (scene) => {
        if (mesh !== undefined && props.rotate) {
            const rpm = 10;
            const deltaT = scene.getEngine().getDeltaTime();

            mesh.rotation.y += (rpm / 60) * Math.PI * 2 * (deltaT / 1000);
        }
    }

    return (
        <div style={props.style} id={props.id} className={`box-shadow 4 ${props.className}`}>
            <SceneComponent antialias url={props.url} name={props.name} onSceneReady={onSceneReady} onRender={onRender} id={useSlotProps.id} style={{width: "100%", height: "100%", outline: "none"}}/>
        </div>
    )
}
