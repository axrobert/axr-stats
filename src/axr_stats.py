#!/usr/bin/env python3
"""AXR Stats — portable GitHub README cards. Python standard library only.

The action is client-side: OAuth tokens go only to the official WakaTime API.
No real stats are generated in demo mode.
"""
from __future__ import annotations

import argparse
import base64
from functools import lru_cache
import datetime as dt
import html
import json
import math
import os
from pathlib import Path
import re
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from zoneinfo import ZoneInfo
from config import read_config, choose, CARD_IDS

BASE = 'https://api.wakatime.com/api/v1'
MAX_API_RESPONSE_BYTES = 2_000_000


class WakaTimeRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Never forward an OAuth Bearer token outside the trusted API origin."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        parsed = urllib.parse.urlsplit(newurl)
        if (parsed.scheme != 'https' or
                parsed.hostname != 'api.wakatime.com' or
                parsed.port not in (None, 443) or
                parsed.username is not None or parsed.password is not None):
            raise RuntimeError('WakaTime attempted an unsafe API redirect')
        return super().redirect_request(req, fp, code, msg, headers, newurl)


THEMES = {
    'midnight': {'background':'#0c1220','surface':'#141e2c','outline':'#2b3a4f','text':'#edf3ff','muted':'#a7b6cc','accent':'#5caeff','success':'#54d2a0'},
    'graphite': {'background':'#111317','surface':'#1b2027','outline':'#353d48','text':'#f1f5f9','muted':'#a3adb9','accent':'#c3a7ff','success':'#58d7b0'},
    'aurora': {'background':'#0a171b','surface':'#10262b','outline':'#275056','text':'#eafffb','muted':'#a8cccb','accent':'#5de2c5','success':'#c3ef8e'},
}
RANKS = json.loads((Path(__file__).resolve().parents[1] / 'assets/badges/current/ranks.json').read_text(encoding='utf-8'))
LEVELS = [(entry['min_hours'], entry['name_en']) for entry in RANKS]
TYPOGRAPHY_SCALES = {'compact': 0.90, 'standard': 1.0, 'large': 1.08}


def presentation_theme(theme, typography='standard', show_rank_stars=True, show_card_subtitles=True):
    """Validated drawing preferences. Do not mutate the shared theme palette."""
    if type(typography) is not str or typography not in TYPOGRAPHY_SCALES:
        raise RuntimeError('Unknown typography preset')
    if type(show_rank_stars) is not bool:
        raise RuntimeError('show_rank_stars must be boolean')
    if type(show_card_subtitles) is not bool:
        raise RuntimeError('show_card_subtitles must be boolean')
    result = dict(theme)
    result['_show_card_subtitles'] = show_card_subtitles
    result['_font_scale'] = TYPOGRAPHY_SCALES[typography]
    result['_show_rank_stars'] = show_rank_stars
    return result

@lru_cache(maxsize=12)
def rank_image_data(level):
    """Inline original transparent artwork so SVGs retain the real badge."""
    if not 0 <= level < len(RANKS):
        raise ValueError('Unknown rank index')
    path = Path(__file__).resolve().parents[1] / 'assets/badges/current' / RANKS[level]['png']
    return base64.b64encode(path.read_bytes()).decode('ascii')


def api(path, token, params=None):
    """Read official WakaTime responses; retry only transient conditions.

    Never put credentials in a query string or an exception message.
    """
    url = BASE + '/' + path + (('?' + urllib.parse.urlencode(params)) if params else '')
    request = urllib.request.Request(url, headers={
        'Authorization': 'Bearer ' + token,
        'Accept': 'application/json',
        'User-Agent': 'AXR-Stats/0.1'
    })
    opener = urllib.request.build_opener(WakaTimeRedirectHandler())
    for attempt in range(4):
        try:
            with opener.open(request, timeout=25) as response:
                status = response.status
                raw = response.read(MAX_API_RESPONSE_BYTES + 1)
                if len(raw) > MAX_API_RESPONSE_BYTES:
                    raise RuntimeError('WakaTime API response exceeded the safe size limit')
                payload = json.loads(raw)
        except urllib.error.HTTPError as exc:
            if (exc.code == 429 or exc.code >= 500) and attempt < 3:
                time.sleep(2 * (attempt + 1))
                continue
            hint = {401: 'OAuth token expired or invalid; renew the Actions secret',
                    403: 'OAuth access denied; verify the token permissions',
                    429: 'Rate limit reached; retry later'}.get(exc.code, 'Check WakaTime availability')
            raise RuntimeError(f'WakaTime HTTP {exc.code} for {path}. {hint}') from None
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError) as exc:
            if attempt < 3:
                time.sleep(2 * (attempt + 1))
                continue
            raise RuntimeError(f'WakaTime connectivity/JSON error for {path}: {type(exc).__name__}') from None

        if not isinstance(payload, dict):
            raise RuntimeError('Invalid WakaTime response object for ' + path)
        if 'error' in payload or 'errors' in payload:
            raise RuntimeError('WakaTime reported an API error for ' + path)
        body = payload.get('data')
        if status == 202 or (isinstance(body, dict) and body.get('is_up_to_date') is False):
            if attempt < 3:
                time.sleep(4 * (attempt + 1))
                continue
            raise RuntimeError('WakaTime stats are still processing for ' + path)
        if 'data' not in payload:
            raise RuntimeError('Invalid WakaTime response for ' + path)
        return payload
    raise RuntimeError('WakaTime unavailable')


def esc(v): return html.escape(str(v), quote=True)
def duration(seconds):
    try:
        value = float(0 if seconds is None else seconds)
    except (TypeError, ValueError, OverflowError):
        raise RuntimeError('WakaTime supplied an invalid duration') from None
    if not math.isfinite(value) or value < 0:
        raise RuntimeError('WakaTime supplied an invalid duration')
    h, m = divmod(round(value/60), 60)
    return f'{h:,}h {m:02d}m'

def label(x,y,value,theme,size=14,weight=400,color='text',anchor=None):
    a=f' text-anchor="{anchor}"' if anchor else ''
    factor = theme.get('_font_scale', 1.0)
    font_size = str(size) if factor == 1 else f'{size * factor:.2f}'.rstrip('0').rstrip('.')
    return f'<text x="{x}" y="{y}" font-family="Arial,sans-serif" font-size="{font_size}" font-weight="{weight}" fill="{theme[color]}"{a}>{esc(value)}</text>'

def shell(w,h,title,subtitle,body,t):
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{esc(title)}">'
    svg += f'<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="18" fill="{t["background"]}" stroke="{t["outline"]}" stroke-width="2"/>'
    svg += f'<rect x="28" y="26" width="4" height="23" rx="2" fill="{t["accent"]}"/>'
    svg += label(45,45,title,t,21,700)
    if t.get('_show_card_subtitles', True):
        svg += label(28,70,subtitle,t,12,color='muted')
    svg += body+'</svg>\n'
    ET.fromstring(svg)
    return svg

def level_for(hours):
    level=max(i for i,(minimum,_) in enumerate(LEVELS) if hours>=minimum)
    current,name=LEVELS[level]
    next_level=LEVELS[level+1][0] if level+1<len(LEVELS) else None
    ratio=min(1,max(0,(hours-current)/(next_level-current))) if next_level else 1
    return level,name,next_level,ratio

def star(cx,cy,outer=10,inner=4.5):
    coords=[]
    for i in range(10):
        angle=math.pi*(-0.5+i/5)
        r=outer if i%2==0 else inner
        coords.append(f'{cx+math.cos(angle)*r:.2f},{cy+math.sin(angle)*r:.2f}')
    return ' '.join(coords)

def shield(t,level,x,y,scale=1):
    """Embed the real rank PNG instead of a procedural vector placeholder."""
    size = 160 * float(scale)
    return (f'<image x="{x}" y="{y}" width="{size:.1f}" height="{size:.1f}" '
            f'href="data:image/png;base64,{rank_image_data(level)}"/>')

def lifetime_card(lifetime,month,week,t):
    data=lifetime.get('data')
    if not isinstance(data,dict) or not isinstance(data.get('total_seconds'),(int,float)):
        raise RuntimeError('WakaTime all-time stats are unavailable or invalid')
    seconds=float(data['total_seconds'])
    if not math.isfinite(seconds) or seconds < 0:
        raise RuntimeError('WakaTime lifetime total must be finite and non-negative')
    level,name,nxt,progress=level_for(seconds/3600)
    filled=5 if nxt is None else min(5,int(progress*5))
    marks=''.join(f'<polygon points="{star(210+i*27,184,10,4.5)}" fill="{t["accent"] if i<filled else t["outline"]}"/>' for i in range(5)) if t.get('_show_rank_stars', True) else ''
    bar=f'<rect x="193" y="275" width="234" height="9" rx="4" fill="{t["outline"]}"/><rect x="193" y="275" width="{234*progress:.1f}" height="9" rx="4" fill="{t["success"]}"/>'
    body=shield(t,level,29,97,1.04)+label(193,115,'CUSTOM LEVEL SYSTEM · HOURS',t,11,700,color='muted')
    body+=label(193,155,name,t,30,700,color='accent')+marks
    body+=label(193,227,'All-time coding activity',t,12,color='muted')+label(193,259,duration(seconds),t,31,700)+bar
    body+=label(193,304,('Next tier: '+str(nxt)+'h') if nxt else 'Maximum tier',t,12,color='muted')
    body+=f'<path d="M456 99 V309" stroke="{t["outline"]}"/>'
    body+=label(480,127,'LAST 30 DAYS',t,11,700,color='muted')+label(480,166,duration(month.get('total_seconds')),t,23,700)
    body+=label(480,225,'LAST 7 DAYS',t,11,700,color='muted')+label(480,263,duration(week.get('total_seconds')),t,23,700)
    return shell(700,340,'Lifetime & progression','Original tiers; not the WakaTime leaderboard',body,t)

def languages_card(stats,t,historical=False,max_rows=10):
    """Control language card information density; default keeps legacy size."""
    if type(max_rows) is not int or max_rows not in (5, 8, 10):
        raise RuntimeError("Language rows must be 5, 8 or 10")
    items=sorted(stats.get('languages') or [],key=lambda x:float(x.get('total_seconds') or 0),reverse=True)[:max_rows]
    maximum=max([float(i.get('total_seconds') or 0) for i in items] or [0])
    total=float(stats.get('total_seconds') or 0)
    body=label(32,109,'LANGUAGE DISTRIBUTION',t,11,700,color='muted')
    body+=label(669,109,duration(total),t,14,700,anchor='end')
    body+=f'<path d="M30 125 H670" stroke="{t["outline"]}"/>'
    for index,item in enumerate(items):
        y=160+index*29
        name=str(item.get('name') or 'Other')
        if len(name)>20: name=name[:19]+'…'
        secs=max(0,float(item.get('total_seconds') or 0))
        w=280*secs/maximum if maximum else 0
        percent=100*secs/total if total else 0
        body+=label(32,y,name,t,13,600)
        body+=f'<rect x="220" y="{y-13}" width="280" height="15" rx="5" fill="{t["surface"]}"/>'
        body+=f'<rect x="220" y="{y-13}" width="{w:.2f}" height="15" rx="5" fill="{t["accent"]}"/>'
        body+=label(510,y,f'{percent:.1f}%',t,11,color='muted')+label(668,y,duration(secs),t,12,600,anchor='end')
    if not items: body+=label(32,200,'No languages recorded in the available all-time data.',t,color='muted')
    return shell(700,190+max_rows*29,'Languages','All-time coding languages · verified WakaTime records' if historical else 'Last 30 days · verified WakaTime records',body,t)

def activity_card(today_seconds, avg_seconds, t):
    """Same canvas, header and footer geometry as the weekly ranking card."""
    fraction = min(1.0, max(0.0, float(today_seconds or 0) / (8 * 3600)))
    cx, cy, radius = 175, 198, 84
    theta = math.pi * (1 - fraction)
    x = cx + radius * math.cos(theta)
    y = cy - radius * math.sin(theta)
    body = (
        f'<path d="M91 198 A84 84 0 0 1 259 198" fill="none" '
        f'stroke="{t["outline"]}" stroke-width="12" stroke-linecap="round"/>'
    )
    if fraction > 0:
        body += (
            f'<path d="M91 198 A84 84 0 {1 if fraction > .5 else 0} 1 '
            f'{x:.2f} {y:.2f}" fill="none" stroke="{t["success"]}" '
            'stroke-width="12" stroke-linecap="round"/>'
        )
    body += label(cx, 184, duration(today_seconds), t, 26, 700, anchor='middle')
    body += label(cx, 207, 'Logged today', t, 12, color='muted', anchor='middle')
    body += f'<path d="M28 251 H322" stroke="{t["outline"]}"/>'
    body += label(28, 280, 'Daily average (7 days)', t, 11, color='muted')
    body += label(322, 280, duration(avg_seconds), t, 12, 700, anchor='end')
    return shell(350, 300, 'Activity', 'Today · visual 8h target', body, t)


def rank_card(week, leaders, t):
    """Public position only, sharing the Activity card's layout grid."""
    current = (leaders or {}).get('current_user') or {}
    rank = current.get('rank')
    valid = isinstance(rank, int) and not isinstance(rank, bool) and rank > 0
    body = label(28, 125, 'PUBLIC LEADERBOARD', t, 11, 700, color='muted')
    body += label(
        28, 179, '#'+str(rank) if valid else '—', t, 46, 700,
        color='success' if valid else 'muted'
    )
    body += label(
        28, 201, 'Official WakaTime position' if valid
        else 'Position not confirmed', t, 12, color='muted'
    )
    body += f'<path d="M28 251 H322" stroke="{t["outline"]}"/>'
    body += label(28, 280, 'Last 7 days', t, 11, color='muted')
    body += label(322, 280, duration(week.get('total_seconds')), t, 12, 700, anchor='end')
    return shell(350, 300, 'Weekly ranking', 'WakaTime public leaderboard', body, t)


def heatmap_card(summaries,today,t):
    by_date={}
    for row in summaries:
        d=(row.get('range') or {}).get('date')
        if d: by_date[d]=max(0,float((row.get('grand_total') or {}).get('total_seconds') or 0))
    start=today-dt.timedelta(days=29)
    start_mon=start-dt.timedelta(days=start.weekday())
    total=active=0
    palette=[t['surface'],'#125c59','#178481','#3dbba6',t['success']]
    body=''
    for n in range(30):
        day=start+dt.timedelta(days=n)
        seconds=by_date.get(day.isoformat(),0)
        total+=seconds
        active+=seconds>0
        intensity=0 if seconds<=0 else min(4,max(1,math.ceil(seconds/7200)))
        diff=(day-start_mon).days
        x,y=62+(diff//7)*29,98+(diff%7)*25
        body+=f'<rect x="{x}" y="{y}" width="20" height="20" rx="4" fill="{palette[intensity]}"><title>{day.isoformat()}: {esc(duration(seconds))}</title></rect>'
    body+=label(300,139,duration(total),t,31,700)+label(300,163,'Last 30 days',t,13,color='muted')
    body+=label(300,217,f'{active}/30',t,27,700,color='success')+label(300,240,'Active days',t,13,color='muted')
    body+=f'<path d="M30 285 H670" stroke="{t["outline"]}"/>'
    body+=label(48,314,'Less',t,11,color='muted')
    body+=''.join(f'<rect x="{94+i*25}" y="301" width="18" height="18" rx="4" fill="{c}"/>' for i,c in enumerate(palette))
    body+=label(230,314,'More',t,11,color='muted')
    return shell(700,342,'Activity heatmap','Last 30 days · day boundaries in your timezone',body,t)

def badge_card(lifetime,t):
    data=lifetime.get('data')
    if not isinstance(data,dict) or not isinstance(data.get('total_seconds'),(int,float)):
        raise RuntimeError('Lifetime stats unavailable for badge')
    seconds = float(data['total_seconds'])
    if not math.isfinite(seconds) or seconds < 0:
        raise RuntimeError('WakaTime lifetime total must be finite and non-negative')
    level,name,nxt,progress=level_for(seconds/3600)
    filled=5 if nxt is None else int(progress*5)
    body=shield(t,level,38,82,.88)
    body+=label(96,220,name,t,16,700,color='accent',anchor='middle')
    if t.get('_show_rank_stars', True):
        body+=''.join(f'<polygon points="{star(53+i*22,244,7,3)}" fill="{t["accent"] if i<filled else t["outline"]}"/>' for i in range(5))
    return shell(192,269,'Emblem','Hours-based tier',body,t)

def cards(lifetime,month,week,summaries,leaders,today,theme='midnight',all_langs=None,language_rows=10,
          typography='standard',show_rank_stars=True,show_card_subtitles=True):
    if theme not in THEMES: raise RuntimeError('Unknown theme')
    t=presentation_theme(THEMES[theme],typography,show_rank_stars,show_card_subtitles)
    a,b=month.get('data'),week.get('data')
    c=summaries.get('data')
    if not isinstance(a,dict) or not isinstance(b,dict) or not isinstance(c,list):
        raise RuntimeError('Invalid WakaTime stats data')
    out={'lifetime.svg':lifetime_card(lifetime,a,b,t),'languages.svg':languages_card(all_langs['data'],t,True,language_rows) if all_langs is not None else languages_card(a,t,max_rows=language_rows),
         'activity.svg':activity_card(0,b.get('daily_average',0),t),
         'ranking.svg':rank_card(b,leaders,t),'heatmap.svg':heatmap_card(c,today,t),
         'emblem.svg':badge_card(lifetime,t)}
    for name,svg in out.items():
        ET.fromstring(svg)
        if re.search(r'(Card Error|Heatmap Error|WakaTime API error)',svg):
            raise RuntimeError('Unexpected error text in '+name)
    return out

def write_cards(rendered,target):
    target=Path(target)
    target.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.axr-',dir=str(target)) as tmp:
        for filename,contents in rendered.items():
            (Path(tmp)/filename).write_text(contents,encoding='utf-8')
        for filename in rendered:
            os.replace(Path(tmp)/filename,target/filename)

def main(argv=None):
    p=argparse.ArgumentParser(description='AXR Stats — WakaTime SVG cards for README.md')
    p.add_argument('--output', default=None)
    p.add_argument('--theme', choices=('midnight','graphite','aurora'), default=None)
    p.add_argument('--timezone', default=None,help='IANA timezone, e.g. America/Maceio')
    p.add_argument('--config', type=Path,default=None,help='Optional JSON presentation settings (never credentials)')
    opts=p.parse_args(argv)
    configuration=read_config(opts.config)
    opts.output=choose(opts.output,configuration,'output','dist')
    opts.theme=choose(opts.theme,configuration,'theme','midnight')
    opts.timezone=choose(opts.timezone,configuration,'timezone','UTC')
    if configuration.get('colors'):
        THEMES['_user_config']={**THEMES[opts.theme],**configuration['colors']}
        opts.theme='_user_config'
    token=os.environ.get('WAKATIME_OAUTH_TOKEN','').strip()
    if not token:
        raise RuntimeError('Set WAKATIME_OAUTH_TOKEN in GitHub Actions secrets; do not use plugin API keys')
    try:
        tz=ZoneInfo(opts.timezone)
    except Exception:
        raise RuntimeError('Unknown IANA timezone') from None
    today=dt.datetime.now(tz).date()
    lifetime=api('users/current/all_time_since_today',token)
    month=api('users/current/stats/last_30_days',token)
    all_langs=api('users/current/stats/all_time',token)
    week=api('users/current/stats/last_7_days',token)
    summaries=api('users/current/summaries',token,{'start':(today-dt.timedelta(days=29)).isoformat(),'end':today.isoformat(),'timezone':opts.timezone})
    try: leaders=api('leaders',token)
    except RuntimeError: leaders={}
    result=cards(lifetime,month,week,summaries,leaders,today,opts.theme,all_langs,
                 language_rows=configuration.get('language_rows',10),
                 typography=configuration.get('typography','standard'),
                 show_rank_stars=configuration.get('show_rank_stars',True),
                 show_card_subtitles=configuration.get('show_card_subtitles',True))
    daily={str((x.get('range') or {}).get('date')):float((x.get('grand_total') or {}).get('total_seconds') or 0) for x in summaries.get('data',[])}
    result['activity.svg']=activity_card(
        daily.get(today.isoformat(),0),week.get('data',{}).get('daily_average',0),
        presentation_theme(THEMES[opts.theme],
                           configuration.get('typography','standard'),
                           configuration.get('show_rank_stars',True),
                           configuration.get('show_card_subtitles',True)))
    selected = configuration.get('cards', CARD_IDS)
    # Emblem PNG compositing needs lifetime.svg as an internal input.
    internal = set(selected)
    if 'emblem' in internal:
        internal.add('lifetime')
    write_cards({key: value for key, value in result.items()
                 if key.removesuffix('.svg') in internal}, opts.output)
    lifetime_seconds=float(lifetime['data']['total_seconds'])
    tier_index=level_for(lifetime_seconds/3600)[0]
    (Path(opts.output)/'.rank-level').write_text(str(tier_index), encoding='ascii')
    print(f'AXR Stats: generated {len(result)} validated SVGs in {opts.output}')

if __name__=='__main__':
    try: main()
    except RuntimeError as e:
        print('AXR Stats error: '+str(e),file=sys.stderr)
        sys.exit(1)
