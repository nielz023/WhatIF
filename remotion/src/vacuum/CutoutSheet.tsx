import React from 'react';
import {AbsoluteFill} from 'remotion';
import {Guy} from './draw/Guy';
import {POSES, PoseName} from './poses';
import {Balloon, CrumpledBalloon, GlassBalloon, HeDot} from './draw/Balloon';
import {Diamond, Kettlebell, Patch, Puff, Pump, Sparkle, SweatDrop, ThoughtBubble, pumpGrips} from './draw/Props';
import {useFonts} from './fonts';

// QA sheet: every cut-out on a coloured background, to catch glitches before animating.
const TILE_COLORS = ['#ff4fd8', '#22d3a4', '#ffb020', '#6d6bff'];

const Tile: React.FC<{i: number; label: string; children: React.ReactNode; w?: number; h?: number; ox?: number; oy?: number; s?: number}> = ({
  i,
  label,
  children,
  w = 270,
  h = 320,
  ox = 135,
  oy = 300,
  s = 0.5,
}) => {
  const col = i % 4;
  const row = Math.floor(i / 4);
  return (
    <g transform={`translate(${col * 270} ${row * 320})`}>
      <rect x={0} y={0} width={w} height={h} fill={TILE_COLORS[(col + row) % 4]} />
      <g transform={`translate(${ox} ${oy}) scale(${s})`}>{children}</g>
      <text x={8} y={22} fontFamily="InterBlack" fontSize={18} fill="#fff">
        {label}
      </text>
    </g>
  );
};

export const CutoutSheet: React.FC = () => {
  useFonts();
  const g = pumpGrips(80);
  // grip relative to the character (pump 180 px to the left of the feet)
  const rel: [number, number] = [-180 + g.right[0], g.right[1]];
  const names = Object.keys(POSES) as PoseName[];
  return (
    <AbsoluteFill style={{background: '#222'}}>
      <svg width={1080} height={1920} viewBox="0 0 1080 1920">
        {names.map((n, i) => (
          <Tile key={n} i={i} label={n}>
            <g transform="translate(-180 0)">
              <Pump ext={80} uid={`qp${i}`} />
            </g>
            <Guy pose={POSES[n](rel)} uid={`qg${i}`} />
          </Tile>
        ))}
        <Tile i={14} label="balloon" oy={170} s={0.85}>
          <Balloon uid="qb1" face={{eyes: 'open', mouth: 'smile', brows: 'relaxed'}} />
        </Tile>
        <Tile i={15} label="balloon scared" oy={170} s={0.85}>
          <Balloon uid="qb2" face={{eyes: 'wide', mouth: 'wide', brows: 'worried', look: [0.6, 0.4]}} />
          <g transform="translate(120 -60)">
            <SweatDrop />
          </g>
        </Tile>
        <Tile i={16} label="balloon angry" oy={170} s={0.85}>
          <Balloon uid="qb3" face={{eyes: 'angry', mouth: 'teeth', brows: 'angry'}} />
          {[...Array(8)].map((_, k) => (
            <g key={k} transform={`translate(${Math.cos(k) * 60} ${Math.sin(k * 1.7) * 70})`}>
              <HeDot />
            </g>
          ))}
        </Tile>
        <Tile i={17} label="crumpled" oy={170} s={1.2}>
          <CrumpledBalloon uid="qb4" face={{eyes: 'squeeze', mouth: 'wavy'}} />
        </Tile>
        <Tile i={18} label="bubble + glass" oy={160} s={0.8}>
          <ThoughtBubble w={300} h={230} />
          <g transform="translate(-50 20) scale(0.32)">
            <Balloon uid="qb6" face={{eyes: 'open', mouth: 'smile'}} />
          </g>
          <g transform="translate(50 -10) scale(0.32)">
            <GlassBalloon uid="qb5" face={{eyes: 'half', mouth: 'smirk', brows: 'relaxed'}} />
          </g>
        </Tile>
        <Tile i={19} label="diamond" oy={170} s={1.3}>
          <Diamond uid="qd1" face={{eyes: 'half', mouth: 'smirk', brows: 'relaxed'}} />
          <g transform="translate(70 -70)">
            <Sparkle />
          </g>
        </Tile>
        <Tile i={20} label="diamond dent" oy={170} s={1.3}>
          <Diamond uid="qd2" dent={1} face={{eyes: 'squeeze', mouth: 'wavy'}} />
        </Tile>
        <Tile i={21} label="dent 2" oy={170} s={1.3}>
          <Diamond uid="qd3" dent={2} face={{eyes: 'squeeze', mouth: 'wide'}} />
        </Tile>
        <Tile i={22} label="puffs" oy={160} s={1.6}>
          <g transform="translate(-40 -20)">
            <Puff uid="qf1" face={{eyes: 'angry', brows: 'angry', mouth: 'flat'}} />
          </g>
          <g transform="translate(40 40)">
            <Puff uid="qf2" face={{eyes: 'wide', brows: 'worried', mouth: 'o'}} />
          </g>
        </Tile>
        <Tile i={23} label="kettlebell" oy={240} s={1.4}>
          <Kettlebell uid="qk" />
          <g transform="translate(0 30)">
            <Patch />
          </g>
        </Tile>
      </svg>
    </AbsoluteFill>
  );
};
