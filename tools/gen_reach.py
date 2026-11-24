# Rusk's Reach, stage two: the settlement. Buildings are boxes with doors; the generator writes the wall segments.
W, H = 3200, 2200
TX, TY = 0.006, 0.009          # wall thickness in fractions (19 px, 20 px)
DW = 70 / W                    # door width on a horizontal wall (70 px: the animal is r 20)
DH = 70 / H                    # door height on a vertical wall

def seg(x, y, w, h, high=True, door=False):
    d = {'x': round(x, 4), 'y': round(y, 4), 'w': round(w, 4), 'h': round(h, 4)}
    if high: d['high'] = True
    if door: d['door'] = True
    return d

def box(x, y, w, h, doors, label):
    # doors: list of (side, t) with side in n/s/e/w and t the fraction along that side (0..1) of the door centre
    out = [('// ' + label, None)]
    sides = {'n': [], 's': [], 'e': [], 'w': []}
    for side, t in doors: sides[side].append(t)
    def run(side, x0, y0, length, horiz):
        cuts = sorted(sides[side])
        pos = 0.0
        for t in cuts:
            c = t * length
            a, b = c - (DW if horiz else DH) / 2, c + (DW if horiz else DH) / 2
            if a - pos > 0.002:
                out.append((None, seg(x0 + (pos if horiz else 0), y0 + (0 if horiz else pos), (a - pos) if horiz else TX, TY if horiz else (a - pos))))
            out.append((None, seg(x0 + (a if horiz else 0), y0 + (0 if horiz else a), (b - a) if horiz else TX, TY if horiz else (b - a), True, True)))
            pos = b
        if length - pos > 0.002:
            out.append((None, seg(x0 + (pos if horiz else 0), y0 + (0 if horiz else pos), (length - pos) if horiz else TX, TY if horiz else (length - pos))))
    run('n', x, y, w, True)
    run('s', x, y + h - TY, w, True)
    run('w', x, y, h, False)
    run('e', x + w - TX, y, h, False)
    return out

walls = []
walls.append(('// the edge of the world', None))
for s in [seg(0, 0, 1, 0.02), seg(0, 0.98, 1, 0.02), seg(0, 0, 0.012, 1), seg(0.988, 0, 0.012, 1)]: walls.append((None, s))

B = [
    # (x, y, w, h, doors, label)
    (0.10, 0.08, 0.17, 0.20, [('s', 0.5), ('e', 0.5)], 'the Hook and Eye: the bar, two doors'),
    (0.33, 0.06, 0.12, 0.14, [('s', 0.35)], 'a residence, north row'),
    (0.48, 0.06, 0.12, 0.14, [('s', 0.65)], 'a residence, north row'),
    (0.66, 0.10, 0.18, 0.22, [('w', 0.4), ('s', 0.3)], 'the salvage workshop'),
    (0.08, 0.40, 0.14, 0.24, [('e', 0.3)], 'the storehouse'),
    (0.30, 0.42, 0.16, 0.16, [('n', 0.5), ('e', 0.5)], 'the market hall'),
    (0.56, 0.44, 0.13, 0.18, [('w', 0.5)], 'the animal holding: Erina will want to see this'),
    (0.14, 0.72, 0.15, 0.18, [('n', 0.6)], 'a residence, south'),
    (0.38, 0.72, 0.20, 0.16, [('n', 0.3), ('e', 0.6)], 'the processing shed: the hooks'),
    (0.70, 0.70, 0.13, 0.18, [('w', 0.5), ('n', 0.5)], 'Rusk\\u2019s house, for later'),
]
for b in B: walls += box(*b)

# the crashed transport: a long hull on the east edge, broken open; low cover of its own chunks; the crew arrive beside it
walls.append(('// the wreck: the hull, cracked open, on the east edge', None))
for s in [seg(0.86, 0.36, 0.11, 0.012), seg(0.86, 0.58, 0.11, 0.012), seg(0.955, 0.36, 0.012, 0.09), seg(0.955, 0.52, 0.012, 0.07),
          seg(0.885, 0.42, 0.03, 0.02, False), seg(0.91, 0.50, 0.03, 0.02, False), seg(0.84, 0.30, 0.035, 0.02, False), seg(0.83, 0.62, 0.04, 0.02, False)]:
    walls.append((None, s))
# the salvage yard: crane bases (high) and hook cradles (low) in the north east open ground
walls.append(('// the salvage yard: crane bases and hook cradles', None))
for s in [seg(0.88, 0.10, 0.03, 0.04), seg(0.93, 0.18, 0.03, 0.04), seg(0.86, 0.20, 0.04, 0.02, False), seg(0.91, 0.08, 0.04, 0.02, False)]:
    walls.append((None, s))
# the market: stalls between the hall and the north row (low)
walls.append(('// market stalls and street junk: low cover, never in a doorway', None))
low = [(0.33, 0.30), (0.40, 0.33), (0.47, 0.30), (0.54, 0.34), (0.24, 0.50), (0.52, 0.66), (0.62, 0.34), (0.78, 0.46), (0.74, 0.58), (0.34, 0.64),
       (0.64, 0.84), (0.28, 0.86), (0.10, 0.30), (0.86, 0.78), (0.46, 0.92), (0.22, 0.66), (0.60, 0.26), (0.88, 0.66), (0.08, 0.92), (0.92, 0.90)]
for (x, y) in low: walls.append((None, seg(x, y, 0.035, 0.018, False)))

# (Ben, 24 Nov) nodules of low cover against the long walls: crate stacks touching each face, clear of the doorways
walls.append(('// crate stacks against the buildings: low cover to move between, never in a doorway', None))
CW, CH = 0.013, 0.017
for (x, y, w, h, doors, label) in B:
    dn = [t for sd, t in doors if sd == 'n']; ds = [t for sd, t in doors if sd == 's']; de = [t for sd, t in doors if sd == 'e']; dw = [t for sd, t in doors if sd == 'w']
    def clear(ts, t, length, gap): return all(abs(tt * length - t) > gap for tt in ts)
    # north and south faces: every 0.055 along, offset so the first sits in from the corner
    n = int(w / 0.055)
    for i in range(n):
        t = (i + 0.5) * w / n
        if clear(dn, t, w, 0.045): walls.append((None, seg(x + t - CW / 2, y - CH, CW, CH, False)))
        if clear(ds, t, w, 0.045) and (i % 2 == 1): walls.append((None, seg(x + t - CW / 2, y + h, CW, CH, False)))
    m = int(h / 0.08)
    for i in range(m):
        t = (i + 0.5) * h / m
        if clear(dw, t, h, 0.06) and (i % 2 == 0): walls.append((None, seg(x - CW, y + t - CH / 2, CW, CH, False)))
        if clear(de, t, h, 0.06): walls.append((None, seg(x + w, y + t - CH / 2, CW, CH, False)))

lines = []
for c, s in walls:
    if c: lines.append('    ' + c)
    else:
        parts = ['x: %s' % s['x'], 'y: %s' % s['y'], 'w: %s' % s['w'], 'h: %s' % s['h']]
        if s.get('high'): parts.append('high: true')
        if s.get('door'): parts.append('door: true')
        lines.append('    {' + ', '.join(parts) + '},')
open('/tmp/claude-0/-home-claude/37bd8a55-7c10-5331-978a-ed5d0bfb1436/scratchpad/reach_walls.txt', 'w').write('\n'.join(lines) + '\n')
print(len([1 for c, s in walls if s]), 'segments', len([1 for c, s in walls if s and s.get('door')]), 'doors')
