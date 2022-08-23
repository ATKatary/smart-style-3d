import React, { useEffect, useRef } from "react";
import { Engine, Scene } from "@babylonjs/core";

export function SceneComponent({antialias, url, name, engineOptions, adaptToDeviceRatio, sceneOptions, onRender, onSceneReady, ...rest}) {
    const meshCanvas = useRef(null);
    
    useEffect(() => {
        const { current: canvas } = meshCanvas;

        const engine = new Engine(canvas, antialias, engineOptions, adaptToDeviceRatio);
        const scene = new Scene(engine, sceneOptions);
        
        if (scene.isReady()) onSceneReady(scene, name, url);
        else scene.onReadyObservable.addOnce((scene_) => onSceneReady(scene_, name, url));
        
        engine.runRenderLoop(() => {
            if (typeof onRender === "function") onRender(scene);
            scene.render();
        });
        
        const resize = () => scene.getEngine().resize();
    
        if (window) window.addEventListener("resize", resize);
    
        return () => {
            scene.getEngine().dispose();
    
            if (window) window.removeEventListener("resize", resize);
        };
    }, [antialias, url, name, engineOptions, adaptToDeviceRatio, sceneOptions, onRender, onSceneReady]);

    return <canvas ref={meshCanvas} {...rest}/>
}   