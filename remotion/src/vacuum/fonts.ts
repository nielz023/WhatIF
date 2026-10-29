import {useEffect, useState} from 'react';
import {continueRender, delayRender, staticFile} from 'remotion';

// Fonts are bundled in public/ so every machine renders the same letters.
let loaded: Promise<void> | null = null;
const load = () => {
  if (!loaded) {
    const faces = [
      new FontFace('InterBlack', `url(${staticFile('vacuum/fonts/Inter-Black.otf')})`),
      new FontFace('SerifBI', `url(${staticFile('vacuum/fonts/FreeSerifBoldItalic.ttf')})`),
    ];
    loaded = Promise.all(faces.map((f) => f.load())).then((fs) => {
      fs.forEach((f) => (document.fonts as unknown as Set<FontFace>).add(f));
    });
  }
  return loaded;
};

export const useFonts = () => {
  const [handle] = useState(() => delayRender('Loading fonts'));
  useEffect(() => {
    load()
      .catch((e) => console.error(e))
      .finally(() => continueRender(handle));
  }, [handle]);
};
