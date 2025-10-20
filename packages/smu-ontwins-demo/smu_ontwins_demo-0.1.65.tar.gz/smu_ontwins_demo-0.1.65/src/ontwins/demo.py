from typing import Optional
from gql import gql

from .core.keycloak import DeviceFlowAuth, DeviceAuthConfig
from .core.gql import init_gql, execute_gql

# 전역 상태
_SSO_SERVER: Optional[str] = None
_API_SERVER: Optional[str] = None
_auth: Optional[DeviceFlowAuth] = None

def init_auth(sso_server: str, api_server: str):
    global _SSO_SERVER, _API_SERVER, _auth
    _SSO_SERVER = sso_server
    _API_SERVER = api_server

    if not _auth:
        _auth = DeviceFlowAuth(
            DeviceAuthConfig(
                api_server_url=_API_SERVER,
                sso_server_url=_SSO_SERVER,
                client_id="sso-client",
            ),
        )

    authenticated = _auth.refresh_if_needed()
    if not authenticated: _auth.login(open_browser=True)

    _set_auth_for_gql()

def _set_auth_for_gql():
    global _API_SERVER, _auth
    _auth.refresh_if_needed()
    init_gql(_API_SERVER, _auth.get_access_token())

def _exec_with_auto_refresh(doc, variables: Optional[dict] = None):
    """execute_gql 래퍼: UNAUTHENTICATED이면 토큰 리프레시 후 1회 재시도.
    리프레시 실패 시엔 에러를 그대로 전파.
    """
    try:
        return execute_gql(doc, variables or {})
    except Exception as e:
        # 토큰 리프레시 시도
        if _auth is None or not _auth.refresh_if_needed():
            # 리프레시 실패 시 에러
            raise
        # 새 토큰으로 GQL 클라이언트 재생성 후 한 번 더 시도
        _set_auth_for_gql()
        return execute_gql(doc, variables or {})

Entity = gql("""
query Entity($id: Int!, $filter: EntityFilterInput) {
    entity(id: $id) {
        id
        system_properties
        createdAt
        relatedToMe(filter: $filter) {
            id
            system_properties
            createdAt
        }
    }
}
""")
def get_projects(domainId):
    projects = _exec_with_auto_refresh(
        Entity,
        {"id": domainId, "filter": { "system_properties_match": { "type": "project" }}}
    ).get(
        "entity", {}
    ).get(
        "relatedToMe", []
    )
    return projects

def _fetch_entity(entity_id: int | str) -> dict:
    """엔티티 단건 조회 (실패 시 빈 dict)."""
    return _exec_with_auto_refresh(Entity, {"id": entity_id}).get("entity", {}) or {}

def get_all_components(root_id: int | str, *, seen=None) -> list[dict]:
    """
    root_id를 시작으로 자신 및 모든 자식들을 순회해
    system_properties.type == 'component' 인 엔티티만 리스트로 반환.
    """
    if seen is None:
        seen = set()  # 순환/중복 방지

    if root_id in seen:
        return []
    seen.add(root_id)

    entity = _fetch_entity(root_id)
    if not entity:
        return []

    etype = (entity.get("system_properties") or {}).get("type")
    results: list[dict] = []

    # 현재 노드가 component면 포함
    if etype == "component":               # 문자열 비교는 == 사용 (is 금지)
        results.append(entity)

    # 자식 순회
    children = entity.get("relatedToMe", []) or []
    # 자식 id만 추출 (중복 제거)
    child_ids = {c.get("id") for c in children if c and c.get("id") is not None}

    for cid in child_ids:
        results.extend(get_all_components(cid, seen=seen))

    return results

def flatten_components_iter(nodes):
    seen = set()
    out  = []
    stack = list(nodes)[::-1]

    while stack:
        node = stack.pop()
        if not isinstance(node, dict):
            continue
        nid = node.get("id")
        if nid in seen:
            continue
        seen.add(nid)

        if (node.get("system_properties") or {}).get("type") == "component":
            out.append(node)

        children = node.get("relatedToMe") or []
        if isinstance(children, list):
            stack.extend(children)
    return out

def get_twin_data():
    FindEntitiesByTags = gql("""
    query FindEntitiesByTags($tags: [String!]!) {
        findEntitiesByTags(input: { tags: $tags }) {
            id
            properties
            system_properties
            createdAt
            updatedAt
            deletedAt
        }
    }
    """)
    EntitiesTree = gql("""
    query EntitiesTree($ids: [Int!]!) {
        entitiesTree(ids: $ids) {
            id
            properties
            system_properties
        }
    }
    """)

    components = flatten_components_iter(get_all_components(globals()["SELECTED_PROJECT_ID"]))

    tags = ["rack"]
    tagged_racks = _exec_with_auto_refresh(FindEntitiesByTags, {"tags": tags}).get("findEntitiesByTags", [])

    ids = [rack["id"] for rack in tagged_racks]
    ids = [id for id in ids if id in {comp["id"] for comp in components}]
    racks = _exec_with_auto_refresh(EntitiesTree, {"ids": ids}).get("entitiesTree", [])

    sorted_racks = sorted(
        racks,
        key=lambda d: (d["properties"]["worldPosition"][0], d["properties"]["worldPosition"][1])
    )
    return sorted_racks




from datetime import datetime, timedelta
from typing import List, Dict, Any

def to_kst_label(item: Dict[str, Any]) -> str:
    # item 예:
    # {'id': 200572, 'properties': {'name': 'New Project'},
    #  'system_properties': {'type': 'project'},
    #  'createdAt': '2025-10-20T07:42:41.254Z'}
    name = item.get("properties", {}).get("name", "(이름없음)")
    created_at = item.get("createdAt")
    # '...Z' → UTC로 파싱 후 +9시간
    dt_utc = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
    dt_kst = dt_utc + timedelta(hours=9)
    # 초는 생략하고 분까지만
    stamp = dt_kst.strftime("%Y-%m-%d %H:%M")
    return f"{name} ({stamp})"

def build_selector_options(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    # make_selector가 기대하는 형식으로 변환: {'label': ..., 'value': ...}
    return [{"label": to_kst_label(it), "value": it["id"]} for it in items]

from IPython.display import display, HTML, clear_output
import ipywidgets as widgets

def make_selector(
    options: List[Dict[str, Any]],
    var_name: str = "SELECTED_ID",
    title: str = "프로젝트를 선택하세요",
    allow_multiple: bool = False,
    default=None,
):
    labels = [o["label"] for o in options]
    values = [o["value"] for o in options]
    label_to_value = dict(zip(labels, values))

    title_html = widgets.HTML(f"<h4 style='margin:4px 0'>{title}</h4>")
    selector = (
        widgets.SelectMultiple(options=labels, rows=min(10, max(4, len(labels))))
        if allow_multiple else
        widgets.Dropdown(options=labels)
    )

    # default(값 id)를 라벨로 매핑
    if default is not None:
        if allow_multiple:
            want = default if isinstance(default, (list, tuple)) else [default]
            selector.value = tuple([lbl for lbl, val in label_to_value.items() if val in want])
        else:
            for lbl, val in label_to_value.items():
                if val == default:
                    selector.value = lbl
                    break

    confirm_btn = widgets.Button(description="확인", button_style="primary")
    cancel_btn  = widgets.Button(description="취소")
    out = widgets.Output()

    def on_confirm(_):
        if allow_multiple:
            chosen_labels = list(selector.value)  # 라벨들
            selected = [label_to_value[lbl] for lbl in chosen_labels]  # id 리스트
            label_text = ", ".join(chosen_labels) if chosen_labels else "(선택 없음)"
        else:
            chosen_label = selector.value                     # 라벨
            selected = label_to_value.get(chosen_label, None) # id
            label_text = chosen_label or "(선택 없음)"

        globals()[var_name] = selected

        with out:
            clear_output(wait=True)
            display(HTML(
                f"<div style='padding:8px;border:1px solid #e0e0e0;border-radius:8px;'>"
                f"<b>프로젝트 선택됨</b> - {label_text}"
                f"</div>"
            ))

    def on_cancel(_):
        with out:
            clear_output(wait=True)
            display(HTML("<div style='color:#999'>취소되었습니다.</div>"))

    confirm_btn.on_click(on_confirm)
    cancel_btn.on_click(on_cancel)
    display(widgets.VBox([title_html, selector, widgets.HBox([confirm_btn, cancel_btn]), out]))

def select_project():
    from .core.gql import _xdomain
    projects = get_projects(_xdomain)
    opts = build_selector_options(projects)
    make_selector(opts, var_name="SELECTED_PROJECT_ID")
