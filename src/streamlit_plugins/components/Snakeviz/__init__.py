import cProfile
import json
import os
import os.path
import re
from pstats import Stats, SortKey
from typing import Union, List, Dict

import streamlit.components.v1 as components

try:
    from urllib.parse import quote
except ImportError:
    from urllib import quote

_RELEASE = os.getenv("RELEASE", "").upper() != "DEV"
# _RELEASE = True

if _RELEASE:
    absolute_path = os.path.dirname(os.path.abspath(__file__))
    build_path = os.path.join(absolute_path, "frontend", "build")
    _component_func = components.declare_component("st_snakeviz", path=build_path)
else:
    _component_func = components.declare_component("st_snakeviz", url="http://localhost:3000")

#
# PINNED_NAV_STYLE = f"""
#                     <style>
#                     iframe[title="{_component_func.name}"] {{
#                         position: fixed;
#                         z-index: 1000;
#                         box-sizing: content-box;
#                         top: calc(2.875rem - 0.5rem);
#                         border: 2px solid #ff4b56;
#                         border: 1px solid #9e9e9e;
#                         border-radius: 5px;
#                     }}
#                     </style>
#                 """


import os.path
from itertools import chain


def xhtml_escape(value: Union[str, bytes]):
    _xhtml_escape_re = re.compile(r'''[&<>"']''')
    _xhtml_escape_dict = {
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;",
    }
    return _xhtml_escape_re.sub(
        lambda match: _xhtml_escape_dict[match.group(0)], value if isinstance(value, str) else value.decode('utf8')
    )


def table_rows(stats: Stats) -> List[List[Union[List[str], str, int]]]:
    """
    Generate a list of stats info lists for the snakeviz stats table.
    Each list will be a series of strings of:
    calls tot_time tot_time_per_call cum_time cum_time_per_call file_line_func
    """
    rows = []

    for k, v in stats.stats.items():
        flf = xhtml_escape('{0}:{1}({2})'.format(
            os.path.basename(k[0]), k[1], k[2]))
        name = '{0}:{1}({2})'.format(*k)

        if v[0] == v[1]:
            calls = str(v[0])
        else:
            calls = '{1}/{0}'.format(v[0], v[1])

        fmt = '{0:.4g}'.format

        tot_time = fmt(v[2])
        cum_time = fmt(v[3])
        tot_time_per = fmt(v[2] / v[0]) if v[0] > 0 else 0
        cum_time_per = fmt(v[3] / v[0]) if v[0] > 0 else 0

        rows.append(
            [
                [calls, v[1]],
                tot_time,
                tot_time_per,
                cum_time,
                cum_time_per,
                flf,
                name
            ]
        )

    return rows


def json_stats(stats: Stats) -> Dict[str, dict]:
    """
    Convert the all_callees data structure to something compatible with
    JSON. Mostly this means all keys need to be strings.
    """
    keyfmt = '{0}:{1}({2})'.format

    def _replace_keys(d):
        return dict((keyfmt(*k), v) for k, v in d.items())

    stats.calc_callees()

    nstats = {}

    for k, v in stats.all_callees.items():
        nk = keyfmt(*k)
        nstats[nk] = {}
        nstats[nk]['children'] = dict((keyfmt(*ck), list(cv)) for ck, cv in v.items())
        nstats[nk]['stats'] = list(stats.stats[k][:4])
        nstats[nk]['callers'] = dict((keyfmt(*ck), list(cv)) for ck, cv in stats.stats[k][-1].items())
        nstats[nk]['display_name'] = keyfmt(os.path.basename(k[0]), k[1], k[2])

    # remove anything that both never called anything and was never called
    # by anything.
    # this is profiler cruft.
    no_calls = set(k for k, v in nstats.items() if not v['children'])
    called = set(chain.from_iterable(d['children'].keys() for d in nstats.values()))
    cruft = no_calls - called

    for c in cruft:
        del nstats[c]

    return nstats


def generate_profile(profile_function, *args, **kwargs) -> Stats:
    profiler = cProfile.Profile()
    profiler.enable()

    profile_function(*args, **kwargs)

    profiler.disable()

    # EXTRAER CARACTERISTICAS
    stats = Stats(profiler)
    stats.sort_stats(SortKey.TIME)
    stats.print_stats()
    return stats

    # Analizar los datos con otras herramientas. Pej; snakeviz
    # stats.dump_stats(f"temp.prof")


def st_snakeviz(profile_name, profile_function, *args, **kwargs):
    stats = generate_profile(profile_function, *args, **kwargs)
    _component_func(
        profile_name=profile_name, table_rows=table_rows(stats), callees=json_stats(stats)
    )


# class VizHandler:
#     def get(self, profile_name):
#         abspath = os.path.abspath(profile_name)
#         if os.path.isdir(abspath):
#             self._list_dir(abspath)
#         else:
#             try:
#                 s = Stats(profile_name)
#             except:
#                 raise RuntimeError('Could not read %s.' % profile_name)
#             self.render(
#                 'viz.html', profile_name=profile_name,
#                 table_rows=table_rows(s), callees=json_stats(s)
#             )
#
#     def _list_dir(self, path):
#         """
#         Show a directory listing.
#
#         """
#         entries = os.listdir(path)
#         dir_entries = [[[
#             '..',
#             quote(os.path.normpath(os.path.join(path, '..')), safe='')
#         ]]]
#         for name in entries:
#             if name.startswith('.'):
#                 # skip invisible files/directories
#                 continue
#             fullname = os.path.join(path, name)
#             displayname = linkname = name
#             # Append / for directories or @ for symbolic links
#             if os.path.isdir(fullname):
#                 displayname += '/'
#             if os.path.islink(fullname):
#                 displayname += '@'
#             dir_entries.append(
#                 [[displayname, quote(os.path.join(path, linkname), safe='')]])
#
#         self.render(
#             'dir.html', dir_name=path, dir_entries=json.dumps(dir_entries)
#         )