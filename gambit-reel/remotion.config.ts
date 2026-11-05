import {Config} from "@remotion/cli/config";

Config.setEntryPoint("src/index.tsx");
// three.js sahneleri için GPU'lu Chrome: ANGLE ile WebGL
Config.setChromiumOpenGlRenderer("angle");
Config.setConcurrency(4);
