import {AbsoluteFill, Audio, Composition, interpolate, registerRoot, Sequence, staticFile} from "remotion";
import {Reel} from "./Reel";
import {GIRIS_SN, Terminal} from "./Terminal";
import {FPS, TOPLAM} from "./zaman";

const GIRIS = Math.round(GIRIS_SN * FPS);
const SES = 0.5; // şarkının ses seviyesi

// Tam sürüm: şarkının başından gambit-cli kesiti, 12,1. saniyeden itibaren skor animasyonu
const Tam: React.FC = () => (
  <AbsoluteFill style={{background: "#000"}}>
    <Audio src={staticFile("sarki-tam.mp3")}
      volume={(f) => SES * interpolate(f, [GIRIS + TOPLAM - 30, GIRIS + TOPLAM], [1, 0], {extrapolateLeft: "clamp", extrapolateRight: "clamp"})} />
    <Sequence durationInFrames={GIRIS}><Terminal /></Sequence>
    <Sequence from={GIRIS}><Reel sesli={false} /></Sequence>
  </AbsoluteFill>
);

const Root: React.FC = () => (
  <>
    <Composition id="Reel" component={Reel} durationInFrames={TOPLAM} fps={FPS} width={1080} height={1920} />
    <Composition id="Tam" component={Tam} durationInFrames={GIRIS + TOPLAM} fps={FPS} width={1080} height={1920} />
  </>
);

registerRoot(Root);
