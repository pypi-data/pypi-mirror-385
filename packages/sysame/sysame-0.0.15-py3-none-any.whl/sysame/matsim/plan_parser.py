"""
Module for parsing MATSim plans xml file.
"""

##### IMPORTS #####
from __future__ import annotations

# Standard imports
import math
import gzip
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple, Sequence

# Third party imports
import polars as pl
import pandas as pd  # type: ignore
from lxml import etree as ET  # type: ignore

# Local imports

##### CONSTANTS #####


##### CLASSES #####
@dataclass
class ParsedPlans:
    persons: pl.DataFrame
    plans: pl.DataFrame
    elements: pl.DataFrame
    activities: pl.DataFrame
    legs: pl.DataFrame
    plan_summary: pl.DataFrame


##### FUNCTIONS #####
def _open_xml_source(path: str):
    """
    Returns a context manager that yields a binary file-like object for the given path.
    Supports .xml and .xml.gz files.
    """

    class _Ctx:
        def __init__(self, p: str):
            self.p = p
            self.f = None

        def __enter__(self):
            if self.p.lower().endswith(".gz"):
                self.f = gzip.open(self.p, "rb")
            else:
                self.f = open(self.p, "rb")
            return self.f

        def __exit__(self, exc_type, exc, tb):
            try:
                if self.f is not None:
                    self.f.close()
            finally:
                self.f = None

    return _Ctx(path)


def _parse_time_to_seconds(s: Optional[str]) -> Optional[int]:
    if not s:
        return None
    t = s.strip()
    try:
        if ":" in t:
            hh, mm, ss = t.split(":")
            return int(hh) * 3600 + int(mm) * 60 + int(ss)
        return int(float(t))
    except Exception:
        return None


def _cast_attr_value(java_class: Optional[str], text: Optional[str]) -> Any:
    if text is None:
        return None
    t = text.strip()
    if java_class:
        jc = java_class.rsplit(".", 1)[-1].lower()
        if jc in ("integer", "int", "long"):
            try:
                return int(t)
            except Exception:
                return t
        if jc in ("double", "float", "bigdecimal"):
            try:
                return float(t)
            except Exception:
                return t
        if jc in ("boolean",):
            return t.lower() in ("true", "1", "yes")
        return t
    if t.lower() in ("true", "false"):
        return t.lower() == "true"
    try:
        if "." in t:
            return float(t)
        return int(t)
    except Exception:
        return t


def _euclidean(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    return math.hypot(p2[0] - p1[0], p2[1] - p1[1])


def parse_matsim_plans(path: str) -> ParsedPlans:
    """
    Stream-parse a MATSim plans file (.xml or .xml.gz) into normalized Polars tables and a per-plan summary.

    Tables:
      - persons(person_id, attributes, selected_plan_indices)
      - plans(person_id, plan_index, plan_uid, score, selected, attributes)
      - elements(person_id, plan_index, elem_index, elem_type, ref_index)
      - activities(person_id, plan_index, act_index, type, x, y, link, facility, start_time_s, end_time_s, attributes)
      - legs(person_id, plan_index, leg_index, mode, dep_time_s, arr_time_s, trav_time_s,
             euclid_dist_m, route_type, route_start_link, route_end_link,
             route_trav_time_s, route_distance_m, route_links, route_raw, attributes)
      - plan_summary(person_id, plan_index, plan_uid, score, selected,
                     activities, modes, points, leg_times_s, leg_euclid_dists_m,
                     leg_route_dists_m, total_time_s, total_euclid_dist_m, total_route_dist_m)
    """
    # Records
    persons_records: List[Dict[str, Any]] = []
    plans_records: List[Dict[str, Any]] = []
    elements_records: List[Dict[str, Any]] = []
    activities_records: List[Dict[str, Any]] = []
    legs_records: List[Dict[str, Any]] = []
    plan_summary_records: List[Dict[str, Any]] = []

    # Streaming context
    iterparse_kwargs: Dict[str, Any] = dict(
        events=(
            "start",
            "end",
        )
    )
    iterparse_kwargs.update(
        dict(load_dtd=False, resolve_entities=False, huge_tree=True)
    )
    # Open path as plain or gz before iterparse and consume events inside this block
    with _open_xml_source(path) as _src:
        context = ET.iterparse(_src, **iterparse_kwargs)

        # Person state
        current_person_id: Optional[str] = None
        person_attrs: Dict[str, Any] = {}
        selected_plan_idxs_for_person: List[int] = []

        # Plan state
        in_plan = False
        plan_index = -1
        plan_score: Optional[float] = None
        plan_selected = False
        plan_attrs: Dict[str, Any] = {}
        elem_index = -1

        # Activity state
        in_activity = False
        act_index = -1
        current_activity_attrs: Dict[str, Any] = {}
        current_activity_partial: Optional[Dict[str, Any]] = None

        # Leg state
        in_leg = False
        leg_index = -1
        current_leg_attrs: Dict[str, Any] = {}
        leg_route_ctx: Dict[str, Any] = {}

        # For euclidean distances
        last_activity_point: Optional[Tuple[float, float]] = None
        pending_leg_row_idx: Optional[int] = (
            None  # index in legs_records awaiting next activity
        )

        # Per-plan summary accumulators
        summary_act_types: List[str] = []
        summary_modes: List[str] = []
        summary_points: List[Dict[str, float]] = []
        summary_leg_times: List[Optional[int]] = []
        summary_leg_euclid_dists: List[float] = []
        summary_leg_route_dists: List[Optional[float]] = []

        # Attribute collection target stack
        attr_target_stack: List[Dict[str, Any]] = []

        def finish_plan():
            # Ensure we mutate the outer lists rather than creating locals
            nonlocal \
                summary_leg_euclid_dists, \
                summary_leg_route_dists, \
                summary_leg_times
            # Align arrays
            if len(summary_leg_euclid_dists) < len(summary_leg_times):
                summary_leg_euclid_dists += [0.0] * (
                    len(summary_leg_times) - len(summary_leg_euclid_dists)
                )
            if len(summary_leg_route_dists) < len(summary_leg_times):
                summary_leg_route_dists += [None] * (
                    len(summary_leg_times) - len(summary_leg_route_dists)
                )

            total_time = sum(t for t in summary_leg_times if isinstance(t, int))
            total_euclid = float(sum(summary_leg_euclid_dists))
            total_route_vals = [
                d for d in summary_leg_route_dists if isinstance(d, (int, float))
            ]
            total_route = float(sum(total_route_vals)) if total_route_vals else None

            plan_uid = f"{current_person_id}#{plan_index}"
            plans_records.append(
                dict(
                    person_id=current_person_id,
                    plan_index=plan_index,
                    plan_uid=plan_uid,
                    score=plan_score,
                    selected=plan_selected,
                    attributes=dict(plan_attrs) if plan_attrs else None,
                )
            )
            plan_summary_records.append(
                dict(
                    person_id=current_person_id,
                    plan_index=plan_index,
                    plan_uid=plan_uid,
                    score=plan_score,
                    selected=plan_selected,
                    activities=list(summary_act_types),
                    modes=list(summary_modes),
                    points=list(summary_points),
                    leg_times_s=list(summary_leg_times),
                    leg_euclid_dists_m=list(summary_leg_euclid_dists),
                    leg_route_dists_m=list(summary_leg_route_dists),
                    total_time_s=total_time if total_time > 0 else None,
                    total_euclid_dist_m=total_euclid if total_euclid > 0 else None,
                    total_route_dist_m=total_route,
                )
            )

        for event, elem in context:
            tag = elem.tag
            if isinstance(tag, str) and "}" in tag:
                tag = tag.split("}", 1)[1]

            if event == "start":
                if tag == "person":
                    current_person_id = elem.attrib.get("id")
                    person_attrs = {}
                    selected_plan_idxs_for_person = []
                    plan_index = -1

                elif tag == "plan" and current_person_id is not None:
                    in_plan = True
                    plan_index += 1
                    plan_score = None
                    plan_selected = False
                    plan_attrs = {}
                    elem_index = -1
                    in_activity = False
                    in_leg = False
                    act_index = -1
                    leg_index = -1
                    last_activity_point = None
                    pending_leg_row_idx = None

                    summary_act_types = []
                    summary_modes = []
                    summary_points = []
                    summary_leg_times = []
                    summary_leg_euclid_dists = []
                    summary_leg_route_dists = []

                    score_raw = elem.attrib.get("score")
                    if score_raw is not None:
                        try:
                            plan_score = float(score_raw)
                        except Exception:
                            plan_score = None
                    sel_raw = elem.attrib.get("selected", "no").lower()
                    plan_selected = sel_raw in ("yes", "true", "1")
                    if plan_selected:
                        selected_plan_idxs_for_person.append(plan_index)

                elif tag == "activity" and in_plan:
                    in_activity = True
                    elem_index += 1
                    act_index += 1
                    current_activity_attrs = {}
                    current_activity_partial = None

                    act_type = elem.attrib.get("type", "")
                    x = elem.attrib.get("x")
                    y = elem.attrib.get("y")
                    link = elem.attrib.get("link")
                    facility = elem.attrib.get("facility")
                    start_time_s = _parse_time_to_seconds(elem.attrib.get("start_time"))
                    end_time_s = _parse_time_to_seconds(elem.attrib.get("end_time"))

                    if x is not None and y is not None:
                        try:
                            px, py = float(x), float(y)
                        except Exception:
                            px, py = float("nan"), float("nan")
                    else:
                        px, py = float("nan"), float("nan")
                    pt_struct = {"x": px, "y": py}

                    # Summary
                    summary_act_types.append(act_type)
                    summary_points.append(pt_struct)

                    # Resolve pending leg euclidean distance
                    if (
                        pending_leg_row_idx is not None
                        and last_activity_point is not None
                    ):
                        eu = _euclidean(last_activity_point, (px, py))
                        legs_records[pending_leg_row_idx]["euclid_dist_m"] = eu
                        summary_leg_euclid_dists.append(eu)
                        pending_leg_row_idx = None

                    # Update last activity point
                    if not math.isnan(px) and not math.isnan(py):
                        last_activity_point = (px, py)

                    # Stash partial activity
                    current_activity_partial = dict(
                        person_id=current_person_id,
                        plan_index=plan_index,
                        act_index=act_index,
                        type=act_type,
                        x=px,
                        y=py,
                        link=link,
                        facility=facility,
                        start_time_s=start_time_s,
                        end_time_s=end_time_s,
                    )

                    # Ordered elements
                    elements_records.append(
                        dict(
                            person_id=current_person_id,
                            plan_index=plan_index,
                            elem_index=elem_index,
                            elem_type="activity",
                            ref_index=act_index,
                        )
                    )

                elif tag == "leg" and in_plan:
                    in_leg = True
                    elem_index += 1
                    leg_index += 1
                    current_leg_attrs = {}
                    leg_route_ctx = {}

                    mode = elem.attrib.get("mode", "")
                    dep_time_s = _parse_time_to_seconds(
                        elem.attrib.get("dep_time") or elem.attrib.get("departure_time")
                    )
                    arr_time_s = _parse_time_to_seconds(
                        elem.attrib.get("arr_time") or elem.attrib.get("arrival_time")
                    )
                    trav_time_s = _parse_time_to_seconds(
                        elem.attrib.get("trav_time") or elem.attrib.get("travel_time")
                    )

                    # Summary
                    summary_modes.append(mode)
                    summary_leg_times.append(trav_time_s)

                    # Leg row (euclid distance filled after next activity)
                    legs_records.append(
                        dict(
                            person_id=current_person_id,
                            plan_index=plan_index,
                            leg_index=leg_index,
                            mode=mode,
                            dep_time_s=dep_time_s,
                            arr_time_s=arr_time_s,
                            trav_time_s=trav_time_s,
                            euclid_dist_m=None,
                            route_type=None,
                            route_start_link=None,
                            route_end_link=None,
                            route_trav_time_s=None,
                            route_distance_m=None,
                            route_links=None,
                            route_raw=None,
                            attributes=None,
                        )
                    )
                    pending_leg_row_idx = len(legs_records) - 1

                    # Ordered elements
                    elements_records.append(
                        dict(
                            person_id=current_person_id,
                            plan_index=plan_index,
                            elem_index=elem_index,
                            elem_type="leg",
                            ref_index=leg_index,
                        )
                    )

                elif tag == "route" and in_leg:
                    # Capture route attrs; body parsed at 'end'
                    route_type = elem.attrib.get("type")
                    leg_route_ctx = {
                        "route_type": route_type,
                        "route_start_link": elem.attrib.get("start_link")
                        or elem.attrib.get("startLinkId"),
                        "route_end_link": elem.attrib.get("end_link")
                        or elem.attrib.get("endLinkId"),
                        "route_trav_time_s": _parse_time_to_seconds(
                            elem.attrib.get("trav_time")
                            or elem.attrib.get("travel_time")
                        ),
                        "route_distance_m": None,
                        "route_links": None,
                        "route_raw": None,
                    }
                    dist_attr = elem.attrib.get("distance")
                    if dist_attr is not None:
                        try:
                            leg_route_ctx["route_distance_m"] = float(dist_attr)
                        except Exception:
                            leg_route_ctx["route_distance_m"] = None

                elif tag == "attributes":
                    # Push current attributes target
                    if in_activity:
                        attr_target_stack.append(current_activity_attrs)
                    elif in_leg:
                        attr_target_stack.append(current_leg_attrs)
                    elif in_plan:
                        attr_target_stack.append(plan_attrs)
                    elif current_person_id is not None:
                        attr_target_stack.append(person_attrs)
                    else:
                        # population-level attributes ignored
                        attr_target_stack.append({})

            elif tag == "route" and in_leg:
                raw_text = (elem.text or "").strip()
                leg_route_ctx["route_raw"] = raw_text if raw_text else None
                rtype = (leg_route_ctx.get("route_type") or "").lower()
                route_links: Optional[List[str]] = None
                if rtype == "links" and raw_text:
                    route_links = [tok for tok in raw_text.split() if tok]
                leg_route_ctx["route_links"] = route_links

                # Merge into the current leg (last appended)
                if legs_records:
                    for k, v in leg_route_ctx.items():
                        legs_records[-1][k] = v
                    # Summary: prefer explicit route distance if present
                    summary_leg_route_dists.append(
                        leg_route_ctx.get("route_distance_m")
                    )

                elem.clear()

            elif tag == "activity" and in_activity:
                # Emit activity row
                activities_records.append(
                    dict(
                        **(current_activity_partial or {}),
                        attributes=dict(current_activity_attrs)
                        if current_activity_attrs
                        else None,
                    )
                )
                in_activity = False
                current_activity_attrs = {}
                current_activity_partial = None
                elem.clear()

            elif tag == "leg" and in_leg:
                # Attach collected leg attributes
                if legs_records:
                    legs_records[-1]["attributes"] = (
                        dict(current_leg_attrs) if current_leg_attrs else None
                    )
                    # If no <route> was present, still align route distances
                    if len(summary_leg_route_dists) < len(summary_leg_times):
                        summary_leg_route_dists.append(
                            legs_records[-1].get("route_distance_m")
                        )
                in_leg = False
                current_leg_attrs = {}
                leg_route_ctx = {}
                elem.clear()

            elif tag == "plan" and in_plan:
                # If a leg is pending without closing activity, pad distance
                if pending_leg_row_idx is not None:
                    legs_records[pending_leg_row_idx]["euclid_dist_m"] = 0.0
                    summary_leg_euclid_dists.append(0.0)
                    pending_leg_row_idx = None
                finish_plan()
                in_plan = False
                plan_attrs = {}
                elem.clear()

            elif tag == "person" and current_person_id is not None:
                persons_records.append(
                    dict(
                        person_id=current_person_id,
                        attributes=dict(person_attrs) if person_attrs else None,
                        selected_plan_indices=list(selected_plan_idxs_for_person),
                    )
                )
                current_person_id = None
                person_attrs = {}
                selected_plan_idxs_for_person = []
                elem.clear()

            elif tag == "attributes":
                if attr_target_stack:
                    attr_target_stack.pop()
                elem.clear()

            elif tag == "attribute":
                if attr_target_stack:
                    target = attr_target_stack[-1]
                    name = elem.attrib.get("name")
                    cls = elem.attrib.get("class")
                    val = _cast_attr_value(cls, elem.text)
                    if name:
                        target[name] = val
                elem.clear()

            else:
                elem.clear()

    # Build Polars DataFrames (robust to empty records)
    def _df_or_empty(
        records: List[Dict[str, Any]], empty_cols: Dict[str, List[Any]]
    ) -> pl.DataFrame:
        return pl.DataFrame(records) if records else pl.DataFrame(empty_cols)

    persons_df = _df_or_empty(
        persons_records,
        {"person_id": [], "attributes": [], "selected_plan_indices": []},
    )
    plans_df = _df_or_empty(
        plans_records,
        {
            "person_id": [],
            "plan_index": [],
            "plan_uid": [],
            "score": [],
            "selected": [],
            "attributes": [],
        },
    )
    elements_df = _df_or_empty(
        elements_records,
        {
            "person_id": [],
            "plan_index": [],
            "elem_index": [],
            "elem_type": [],
            "ref_index": [],
        },
    )
    activities_df = _df_or_empty(
        activities_records,
        {
            "person_id": [],
            "plan_index": [],
            "act_index": [],
            "type": [],
            "x": [],
            "y": [],
            "link": [],
            "facility": [],
            "start_time_s": [],
            "end_time_s": [],
            "attributes": [],
        },
    )
    legs_df = _df_or_empty(
        legs_records,
        {
            "person_id": [],
            "plan_index": [],
            "leg_index": [],
            "mode": [],
            "dep_time_s": [],
            "arr_time_s": [],
            "trav_time_s": [],
            "euclid_dist_m": [],
            "route_type": [],
            "route_start_link": [],
            "route_end_link": [],
            "route_trav_time_s": [],
            "route_distance_m": [],
            "route_links": [],
            "route_raw": [],
            "attributes": [],
        },
    )
    plan_summary_df = _df_or_empty(
        plan_summary_records,
        {
            "person_id": [],
            "plan_index": [],
            "plan_uid": [],
            "score": [],
            "selected": [],
            "activities": [],
            "modes": [],
            "points": [],
            "leg_times_s": [],
            "leg_euclid_dists_m": [],
            "leg_route_dists_m": [],
            "total_time_s": [],
            "total_euclid_dist_m": [],
            "total_route_dist_m": [],
        },
    )

    return ParsedPlans(
        persons=persons_df,
        plans=plans_df,
        elements=elements_df,
        activities=activities_df,
        legs=legs_df,
        plan_summary=plan_summary_df,
    )


def _levenshtein_norm(a: Sequence[str], b: Sequence[str]) -> float:
    # Normalized Levenshtein distance in [0,1]
    m, n = len(a), len(b)
    if m == 0 and n == 0:
        return 0.0
    dp = [list(range(n + 1))] + [[i] + [0] * n for i in range(1, m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            cost = 0 if a[i - 1] == b[j - 1] else 1
            dp[i][j] = min(
                dp[i - 1][j] + 1,  # deletion
                dp[i][j - 1] + 1,  # insertion
                dp[i - 1][j - 1] + cost,  # substitution
            )
    return dp[m][n] / max(m, n)


def _jaccard_distance(a: Sequence[str], b: Sequence[str]) -> float:
    sa, sb = set(a), set(b)
    if not sa and not sb:
        return 0.0
    inter = len(sa & sb)
    union = len(sa | sb)
    return 1.0 - (inter / union if union else 0.0)


def _align_indices(
    acts_a: Sequence[str],
    acts_b: Sequence[str],
    strategy: str = "index",  # "index" or "by_type"
) -> List[Tuple[int, int]]:
    pairs: List[Tuple[int, int]] = []
    if strategy == "index":
        L = min(len(acts_a), len(acts_b))
        pairs = [(i, i) for i in range(L)]
    else:
        # by_type: match kth occurrence of each type
        from collections import defaultdict

        pos_a = defaultdict(list)
        pos_b = defaultdict(list)
        for i, t in enumerate(acts_a):
            pos_a[t].append(i)
        for j, t in enumerate(acts_b):
            pos_b[t].append(j)
        for t in set(pos_a.keys()) & set(pos_b.keys()):
            L = min(len(pos_a[t]), len(pos_b[t]))
            pairs.extend((pos_a[t][k], pos_b[t][k]) for k in range(L))
        pairs.sort()
    return pairs


def _mean_abs_diff_norm_seconds(
    xs: Sequence[Optional[int]],
    ys: Sequence[Optional[int]],
    pairs: List[Tuple[int, int]],
    day_seconds: int = 24 * 3600,
) -> Optional[float]:
    vals: List[float] = []
    for i, j in pairs:
        xi = xs[i] if i < len(xs) else None
        yj = ys[j] if j < len(ys) else None
        if isinstance(xi, int) and isinstance(yj, int):
            vals.append(abs(xi - yj) / day_seconds)
    if not vals:
        return None
    return min(1.0, sum(vals) / len(vals))


def _mean_point_distance_m(
    pts_a: Sequence[Dict[str, float]],
    pts_b: Sequence[Dict[str, float]],
    pairs: List[Tuple[int, int]],
) -> Optional[float]:
    dists: List[float] = []
    for i, j in pairs:
        if i >= len(pts_a) or j >= len(pts_b):
            continue
        ax, ay = pts_a[i].get("x", float("nan")), pts_a[i].get("y", float("nan"))
        bx, by = pts_b[j].get("x", float("nan")), pts_b[j].get("y", float("nan"))
        if not (math.isnan(ax) or math.isnan(ay) or math.isnan(bx) or math.isnan(by)):
            dists.append(math.hypot(ax - bx, ay - by))
    if not dists:
        return None
    return sum(dists) / len(dists)


def _total_time_s(summary_row: Dict[str, Any]) -> Optional[float]:
    # Sum of leg_times_s ignoring None; returns None if no values present
    times = summary_row.get("leg_times_s") or []
    vals = [t for t in times if isinstance(t, (int, float))]
    if not vals:
        return None
    return float(sum(vals))


def _total_dist_m(summary_row: Dict[str, Any]) -> Optional[float]:
    # Prefer route total, then euclid
    total = summary_row.get("total_route_dist_m")
    if isinstance(total, (int, float)) and total > 0:
        return float(total)
    total = summary_row.get("total_euclid_dist_m")
    if isinstance(total, (int, float)) and total > 0:
        return float(total)
    # Fallback: sum of leg_route_dists_m else euclid
    legs_route = summary_row.get("leg_route_dists_m") or []
    legs_eu = summary_row.get("leg_euclid_dists_m") or []
    vals = [d for d in legs_route if isinstance(d, (int, float))]
    if not vals:
        vals = [d for d in legs_eu if isinstance(d, (int, float))]
    if not vals:
        return None
    return float(sum(vals))


def compare_plans_for_person(
    parsed: ParsedPlans,
    person_id: str,
    align: str = "index",  # "index" or "by_type"
    weights: Optional[Dict[str, float]] = None,
    space_scale_m: float = 5000.0,  # normalization for spatial mean distance
) -> pl.DataFrame:
    """
    Returns pairwise plan comparison for this person with per-dimension metrics and an overall distance in [0,1].
    Metrics:
      - d_act_seq: normalized Levenshtein over activity sequence
      - d_mode_seq: normalized Levenshtein over leg mode sequence
      - d_act_set: Jaccard distance over unique activity types
      - d_start_time: mean absolute diff of activity start times (normalized by day), aligned per 'align'
      - d_total_time: normalized abs diff of total travel time
      - d_total_dist: normalized abs diff of total distance (route>euclid)
      - d_space_mean: mean point distance (meters) for aligned activities
      - overall: weighted blend (auto-renormalized if some metrics are None)
    """
    if weights is None:
        weights = {
            "d_act_seq": 0.30,
            "d_mode_seq": 0.20,
            "d_act_set": 0.10,
            "d_start_time": 0.15,
            "d_total_time": 0.10,
            "d_total_dist": 0.10,
            "d_space_mean": 0.05,  # normalized by space_scale_m
        }

    # Collect this person's plans (summary) and activity start times
    ps = parsed.plan_summary.filter(pl.col("person_id") == person_id).sort("plan_index")
    if ps.height == 0:
        return pl.DataFrame(
            {"person_id": [], "plan_i": [], "plan_j": [], "overall": []}
        )

    # Build helper dict of plan_index -> activity start times
    acts = (
        parsed.activities.filter(pl.col("person_id") == person_id)
        .select(["plan_index", "act_index", "start_time_s", "end_time_s"])
        .sort(["plan_index", "act_index"])
        .group_by("plan_index")
        .agg(
            [
                pl.col("start_time_s").alias("act_start_times_s"),
                pl.col("end_time_s").alias("act_end_times_s"),
            ]
        )
    )
    # Join into summary for convenience (lists)
    ps = ps.join(acts, on="plan_index", how="left")

    # Convert to list of python dict rows for easy pairwise loops
    plans: List[Dict[str, Any]] = ps.to_dicts()

    rows: List[Dict[str, Any]] = []
    for i in range(len(plans)):
        for j in range(i + 1, len(plans)):
            A, B = plans[i], plans[j]

            acts_a: List[str] = A.get("activities") or []
            acts_b: List[str] = B.get("activities") or []
            modes_a: List[str] = A.get("modes") or []
            modes_b: List[str] = B.get("modes") or []
            pts_a: List[Dict[str, float]] = A.get("points") or []
            pts_b: List[Dict[str, float]] = B.get("points") or []
            a_starts: List[Optional[int]] = A.get("act_start_times_s") or []
            b_starts: List[Optional[int]] = B.get("act_start_times_s") or []

            pairs = _align_indices(acts_a, acts_b, strategy=align)

            # Per-dimension metrics
            d_act_seq = _levenshtein_norm(acts_a, acts_b)
            d_mode_seq = _levenshtein_norm(modes_a, modes_b)
            d_act_set = _jaccard_distance(acts_a, acts_b)
            d_start_time = _mean_abs_diff_norm_seconds(a_starts, b_starts, pairs)

            ta, tb = _total_time_s(A), _total_time_s(B)
            if ta is not None and tb is not None and max(ta, tb) > 0:
                d_total_time = abs(ta - tb) / max(ta, tb)
            else:
                d_total_time = None

            da, db = _total_dist_m(A), _total_dist_m(B)
            if da is not None and db is not None and max(da, db) > 0:
                d_total_dist = abs(da - db) / max(da, db)
            else:
                d_total_dist = None

            space_mean = _mean_point_distance_m(pts_a, pts_b, pairs)
            d_space_mean = (
                None if space_mean is None else min(1.0, space_mean / space_scale_m)
            )

            # Overall weighted score (skip Nones, renormalize weights)
            metrics = {
                "d_act_seq": d_act_seq,
                "d_mode_seq": d_mode_seq,
                "d_act_set": d_act_set,
                "d_start_time": d_start_time,
                "d_total_time": d_total_time,
                "d_total_dist": d_total_dist,
                "d_space_mean": d_space_mean,
            }
            use_weights = {
                k: w for k, w in weights.items() if metrics.get(k) is not None
            }
            wsum = sum(use_weights.values()) or 1.0
            overall = sum(metrics[k] * use_weights[k] for k in use_weights) / wsum

            rows.append(
                dict(
                    person_id=person_id,
                    plan_i=A["plan_index"],
                    plan_j=B["plan_index"],
                    d_act_seq=d_act_seq,
                    d_mode_seq=d_mode_seq,
                    d_act_set=d_act_set,
                    d_start_time=d_start_time,
                    d_total_time=d_total_time,
                    d_total_dist=d_total_dist,
                    d_space_mean_m=space_mean,
                    overall=overall,
                )
            )

    return pl.DataFrame(rows)
