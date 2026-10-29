import React from 'react';
import {Audio, Sequence, staticFile} from 'remotion';
import {FPS} from './anim';
import {VO_START} from './timing';
import {CUES} from './cues';

// Voice at 0 dB on its own layer, sound effects on another, quiet under the voice.
const db = (x: number) => Math.pow(10, x / 20);

export const Sound: React.FC = () => (
  <>
    <Sequence from={Math.round(VO_START * FPS)} layout="none" name="voice">
      <Audio src={staticFile('vacuum/vo/take1.mp3')} volume={1} />
    </Sequence>
    {CUES.map((c, i) => (
      <Sequence key={i} from={Math.max(0, Math.round(c.at * FPS))} layout="none" name={`sfx ${c.f}`}>
        <Audio src={staticFile(`vacuum/sfx/${c.f}.wav`)} volume={db(c.db)} />
      </Sequence>
    ))}
  </>
);
