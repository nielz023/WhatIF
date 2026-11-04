import { Area, AreaChart, Bar, BarChart, CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis, Cell, Pie, PieChart } from 'recharts';
import type { ReactNode } from 'react';

export const CHART_COLORS = ['#22d3ee', '#a855f7', '#fb923c', '#f43f5e', '#22c55e', '#facc15', '#3b82f6', '#ec4899'];

const axis = { stroke: '#475569', fontSize: 11, tickLine: false, axisLine: false } as const;
const tooltip = {
  contentStyle: { background: '#0b1230', border: '1px solid #2b3a70', borderRadius: 12, fontSize: 12, color: '#e2e8f0' },
  labelStyle: { color: '#94a3b8' },
  cursor: { fill: 'rgba(99,102,241,.08)' },
};

export function ChartPanel({ title, children, right, h = 240 }: { title: ReactNode; children: ReactNode; right?: ReactNode; h?: number }) {
  return (
    <div className="panel p-4">
      <div className="mb-3 flex items-center justify-between gap-2">
        <div className="text-sm font-semibold text-white">{title}</div>
        {right}
      </div>
      <div style={{ height: h }}>{children}</div>
    </div>
  );
}

export function AreaSeries({ data, keys, fmt }: { data: object[]; keys: { key: string; color: string; name?: string }[]; fmt?: (v: number) => string }) {
  return (
    <ResponsiveContainer>
      <AreaChart data={data} margin={{ left: -10, right: 8, top: 5 }}>
        <defs>
          {keys.map((k) => (
            <linearGradient key={k.key} id={`g-${k.key}`} x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={k.color} stopOpacity={0.45} />
              <stop offset="100%" stopColor={k.color} stopOpacity={0} />
            </linearGradient>
          ))}
        </defs>
        <CartesianGrid stroke="#1e2a52" strokeDasharray="3 3" vertical={false} />
        <XAxis dataKey="label" {...axis} minTickGap={20} />
        <YAxis {...axis} tickFormatter={fmt} width={56} />
        <Tooltip {...tooltip} formatter={(v: number) => (fmt ? fmt(v) : v.toLocaleString())} />
        {keys.length > 1 && <Legend wrapperStyle={{ fontSize: 11 }} />}
        {keys.map((k) => <Area key={k.key} type="monotone" dataKey={k.key} name={k.name ?? k.key} stroke={k.color} strokeWidth={2} fill={`url(#g-${k.key})`} />)}
      </AreaChart>
    </ResponsiveContainer>
  );
}

export function LineSeries({ data, keys, fmt }: { data: object[]; keys: { key: string; color: string; name?: string }[]; fmt?: (v: number) => string }) {
  return (
    <ResponsiveContainer>
      <LineChart data={data} margin={{ left: -10, right: 8, top: 5 }}>
        <CartesianGrid stroke="#1e2a52" strokeDasharray="3 3" vertical={false} />
        <XAxis dataKey="label" {...axis} minTickGap={20} />
        <YAxis {...axis} tickFormatter={fmt} width={48} />
        <Tooltip {...tooltip} />
        <Legend wrapperStyle={{ fontSize: 11 }} />
        {keys.map((k) => <Line key={k.key} type="monotone" dataKey={k.key} name={k.name ?? k.key} stroke={k.color} strokeWidth={2} dot={false} />)}
      </LineChart>
    </ResponsiveContainer>
  );
}

export function Bars({ data, x, keys, stacked, fmt, layout }: { data: object[]; x: string; keys: { key: string; color: string; name?: string }[]; stacked?: boolean; fmt?: (v: number) => string; layout?: 'horizontal' | 'vertical' }) {
  const vertical = layout === 'vertical';
  return (
    <ResponsiveContainer>
      <BarChart data={data} layout={layout} margin={{ left: vertical ? 10 : -10, right: 8, top: 5 }}>
        <CartesianGrid stroke="#1e2a52" strokeDasharray="3 3" vertical={vertical} horizontal={!vertical} />
        {vertical ? <XAxis type="number" {...axis} tickFormatter={fmt} /> : <XAxis dataKey={x} {...axis} minTickGap={10} />}
        {vertical ? <YAxis type="category" dataKey={x} {...axis} width={100} /> : <YAxis {...axis} tickFormatter={fmt} width={52} />}
        <Tooltip {...tooltip} formatter={(v: number) => (fmt ? fmt(v) : v.toLocaleString())} />
        {keys.length > 1 && <Legend wrapperStyle={{ fontSize: 11 }} />}
        {keys.map((k) => <Bar key={k.key} dataKey={k.key} name={k.name ?? k.key} fill={k.color} radius={vertical ? [0, 6, 6, 0] : [6, 6, 0, 0]} stackId={stacked ? 'a' : undefined} />)}
      </BarChart>
    </ResponsiveContainer>
  );
}

export function Donut({ data, fmt }: { data: { name: string; value: number }[]; fmt?: (v: number) => string }) {
  return (
    <ResponsiveContainer>
      <PieChart>
        <Pie data={data} dataKey="value" nameKey="name" innerRadius="58%" outerRadius="85%" paddingAngle={2} stroke="none">
          {data.map((_, i) => <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />)}
        </Pie>
        <Tooltip {...tooltip} formatter={(v: number) => (fmt ? fmt(v) : v.toLocaleString())} />
        <Legend wrapperStyle={{ fontSize: 11 }} layout="vertical" align="right" verticalAlign="middle" />
      </PieChart>
    </ResponsiveContainer>
  );
}
