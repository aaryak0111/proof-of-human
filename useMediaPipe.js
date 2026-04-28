// hooks/useMediaPipe.js
import * as faceDetection from '@tensorflow-models/face-detection';

export function useFaceDetection() {
    const detector = await faceDetection.createDetector(
        faceDetection.SupportedModels.MediaPipeFaceDetector,
        { runtime: 'tfjs', maxFaces: 1 }
    );
    return async (videoEl) => {
        const faces = await detector.estimateFaces(videoEl);
        if (!faces.length) return null;
        return {
            bbox: faces[0].box,
            keypoints: faces[0].keypoints,  // eyes, nose, lips
            confidence: faces[0].score
        };
    };
}