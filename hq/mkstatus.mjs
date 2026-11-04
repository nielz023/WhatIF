import * as B from './dm.mjs';
import fs from 'fs';
const activity = [
  { title: 'Animeer video 3: geen regels meer', id: 'cmsg_01LkmukDuDNkj8pXsDu4v8WGTfi8z2mFAQH5Qa5zaASKk1', state: 'working', last: '5 nov 00:16', doing: 'Scène 10 (dag 4): stad gaat op zwart, kaarslicht. Scène 1 en 3-9 in de renderwachtrij op de pc.' },
  { title: 'Driftmark HQ (dit hoofdscherm)', id: 'cmsg_01LkmukDuDNkj8pXsDu4v8WGD3kJS5r6nXrqiC2f5NfjRQ', state: 'working', last: '5 nov 00:17', doing: 'Live data, echte tijd en alles in het Nederlands.' },
  { title: 'Bouw cast en sets voor geen-regels-video', id: 'cmsg_01LkmukDuDNkj8pXsDu4v8WGCHT43zJaABsdPF4uv4swV5', state: 'blocked', last: '4 nov 19:08', doing: 'Wacht op jouw reactie.' },
  { title: 'Schrijf titel, beschrijving en tags video 2', id: 'cmsg_01LkmukDuDNkj8pXsDu4v8WGFt2jvrzboJ4GbK8fbcasKv', state: 'blocked', last: '31 okt 15:23', doing: 'Wacht op jouw reactie.' },
  { title: 'Bedenk ideeën voor teaser-shorts', id: 'cmsg_01LkmukDuDNkj8pXsDu4v8WGS9PSyyns39jsYw5hE9SySp', state: 'blocked', last: '28 okt 12:30', doing: 'Wacht op jouw reactie.' },
  { title: 'Schrijf werkwijze-document', id: 'cmsg_01LkmukDuDNkj8pXsDu4v8WG3mkzfMZCLNKhwkm4CN7Tss', state: 'done', last: '4 nov 21:49' },
  { title: 'Verloop video 3', id: 'cmsg_01LkmukDuDNkj8pXsDu4v8WG8Td6Q42bhkx3TbQHgnSwbh', state: 'done', last: '4 nov 15:33' },
];
const s = { updated: 'donderdag 5 november 2026, 00:17', channel: B.CHANNEL, videos: B.VIDEOS, shorts: B.SHORTS, next: B.NEXT, ideas: B.IDEAS, links: B.LINKS, activity };
fs.writeFileSync('/mnt/project-files/driftmark-hq/status.json', JSON.stringify(s, null, 2));
console.log('ok', JSON.stringify(s).length);
