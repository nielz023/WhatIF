import React from 'react';
import {Composition} from 'remotion';
import {CutoutSheet} from './vacuum/CutoutSheet';
import {VacuumScene} from './vacuum/Scene';
import {FPS} from './vacuum/anim';
import {DURATION} from './vacuum/timing';

export const RemotionRoot: React.FC = () => (
  <>
    <Composition
      id="VacuumBalloon"
      component={VacuumScene}
      durationInFrames={Math.round(DURATION * FPS)}
      fps={FPS}
      width={1080}
      height={1920}
    />
    <Composition id="VacuumCutouts" component={CutoutSheet} durationInFrames={1} fps={FPS} width={1080} height={1920} />
  </>
);
