"""Navigator labeller for sites on the underscore naming override (builder section 12a).

Feed it a `get_all_elements` result (page, or `scope_component_id` for a definition):
  page_labels(load_tree(path), "About", "about_")  -> [(component, element, label)]
  comp_labels("Card: Team", root)                  -> same, for inside a definition
Turn each tuple into a `set_display_name` action (add `scope_component_id` for definitions),
send about 60 per `data_element_tool` call, then read a sample back with `get_display_name`.
Built 8 Oct 2026 (1,201 labels on its first site). Read the output before sending:
hand-fix odd ones (e.g. "List List") rather than special-casing them here.
"""
import json

UTIL = {
    "page-wrapper": "Page Wrapper", "main-wrapper": "Main",
    "padding-global": "Side Padding",
    "container-large": "Container Large", "container-medium": "Container Medium",
    "container-small": "Container Small", "container-full": "Container Full",
    "container-semi-full": "Container Semi Full",
    "padding-section-large": "Section Padding Large", "padding-section-medium": "Section Padding Medium",
    "padding-section-small": "Section Padding Small",
    "button-group": "Buttons", "text-style-tagline": "Tagline",
    "section-script-css": "Section CSS", "section-script-js": "Section JS",
    "global-styles": "Global Styles Embed", "global-scripts": "Global Scripts Embed",
    "text-rich-text": "Rich Text",
}
WORD = {"wrapper": "Wrap", "cms": "CMS", "cta": "CTA", "faq": "FAQ", "js": "JS", "css": "CSS",
        "seo": "SEO", "id": "ID", "ui": "UI"}
INST = {"Global Styles", "Global Scripts", "Navbar", "Footer"}
TYPE_LABEL = {"TabsWrapper": "Tabs", "TabsMenu": "Tab Menu", "TabsLink": "Tab", "TabsContent": "Tab Panes", "TabsPane": "Pane",
              "FormForm": "Form", "FormWrapper": "Form Block", "FormSuccessMessage": "Success Message", "FormErrorMessage": "Error Message"}
SKIP_TYPES = {"String", "Body", "PaginationPreviousIcon", "PaginationNextIcon"}


def title(s, sep="_"):
    return " ".join(WORD.get(w, w.capitalize()) for w in s.split(sep) if w)


def find_root(x):
    if isinstance(x, dict):
        if "children" in x and "id" in x and "type" in x:
            return x
        for v in x.values():
            r = find_root(v)
            if r:
                return r
    if isinstance(x, list):
        for v in x:
            r = find_root(v)
            if r:
                return r


def section_classes(root):
    found = []

    def walk(n):
        for c in (n.get("styleNames") or [])[:1]:
            if c.endswith("_section") and not c.startswith("component_"):
                found.append(c)
        for k in n.get("children") or []:
            walk(k)
    walk(root)
    return found


def page_labels(root, page_label, page_prefix):
    """page_prefix like 'about_' ; page_label like 'About'."""
    acts = []

    def label(n, ctx):
        t = n.get("type")
        cls = n.get("styleNames") or []
        if t in SKIP_TYPES:
            return None, ctx
        if t == "ComponentInstance":
            nm = n.get("instanceDetails", {}).get("name", "")
            if nm.startswith("Section: "):
                return "Component: " + nm[9:], ctx
            if nm in INST:
                return "Component: " + nm, ctx
            return None, ctx
        if not cls:
            return None, ctx
        c = cls[0]
        combo = [x for x in cls[1:] if x.startswith("is-")]
        if c.endswith("_section") and not c.startswith("component_"):
            inner = c[len(page_prefix):-len("_section")] if c.startswith(page_prefix) else c[:-len("_section")]
            sec = title(inner)
            return f"{page_label}: {sec}", {"sec": sec, "sp": c[:-len("section")]}
        if c in UTIL:
            return UTIL[c], ctx
        if c == "button":
            if "is-load-more" in combo:
                return "Load More", ctx
            if "is-navbar" in combo:
                return "Navbar Button", ctx
            return ("Submit Button" if t == "FormButton" else "Button"), ctx
        if "-" in c and "_" not in c:
            lab = title(c, "-")
        else:
            sp = (ctx or {}).get("sp")
            if sp and c.startswith(sp):
                rest = c[len(sp):]
            elif c.startswith(page_prefix):
                rest = c[len(page_prefix):]
            elif c.startswith("component_"):
                rest = c.split("_", 2)[-1]
            else:
                rest = c
            lab = title(rest)
            if rest == "content" and ctx:
                lab = f"{ctx['sec']} Content"
            if rest == "header":
                lab = "Heading Block"
            if rest in ("list", "list_wrap", "list_wrapper") and ctx:
                lab = f"{ctx['sec']} " + ("List" if rest == "list" else "List Wrap")
        if t in TYPE_LABEL:
            lab = TYPE_LABEL[t]
        if combo:
            cv = combo[0][3:]
            lab = f"{lab} {cv}" if cv.isdigit() else title(cv, "-") + " " + lab
        return lab, ctx

    def walk(n, ctx):
        kids = n.get("children") or []
        res = [label(k, ctx) for k in kids]
        labs = [r[0] for r in res]
        tot = {l: labs.count(l) for l in labs if l}
        cnt = {}
        for k, (l, kctx) in zip(kids, res):
            if l and tot[l] > 1 and not l.startswith(page_label + ":") and not l.startswith("Component:"):
                cnt[l] = cnt.get(l, 0) + 1
                l = f"{l} {cnt[l]}"
            if l:
                acts.append((k["id"]["component"], k["id"]["element"], l))
            walk(k, kctx)

    walk(root, None)
    return acts


def load_tree(path):
    txt = open(path).read()
    return find_root(json.loads(txt))


def comp_labels(name, root):
    """Labels inside one component definition. Returns [(component, element, label)]."""
    rc = (root.get("styleNames") or [""])[0]
    if name.startswith("Section: "):
        short = name[9:]
        prefix = rc[:-len("section")] if rc.endswith("_section") else rc + "_"
        rootlab = "Component: " + short
    elif name in ("Navbar", "Footer"):
        short, prefix, rootlab = name, name.lower() + "_", name
    else:
        short = name.split(": ")[-1]
        prefix, rootlab = rc + "_", name
    out = [(root["id"]["component"], root["id"]["element"], rootlab)]

    def label(n):
        t = n.get("type")
        cls = n.get("styleNames") or []
        if t in ("ComponentInstance", "Slot") or t in SKIP_TYPES or not cls:
            return None
        c = cls[0]
        combo = [x for x in cls[1:] if x.startswith("is-")]
        if c in UTIL:
            return UTIL[c]
        if c == "button":
            if "is-load-more" in combo:
                return "Load More"
            if "is-navbar" in combo:
                return "Navbar Button"
            return "Submit Button" if t == "FormButton" else "Button"
        if "-" in c and "_" not in c:
            lab = title(c, "-")
        else:
            if c.startswith(prefix):
                rest = c[len(prefix):]
            elif c.startswith("component_"):
                rest = c.split("_", 2)[-1]
            else:
                rest = c
            lab = title(rest)
            if rest == "content" and name.startswith("Section: "):
                lab = f"{short} Content"
            if rest == "header":
                lab = "Heading Block"
        if t in TYPE_LABEL:
            lab = TYPE_LABEL[t]
        if combo:
            cv = combo[0][3:]
            lab = f"{lab} {cv}" if cv.isdigit() else title(cv, "-") + " " + lab
        return lab

    def walk(n):
        kids = n.get("children") or []
        labs = [label(k) for k in kids]
        tot = {l: labs.count(l) for l in labs if l}
        cnt = {}
        for k, l in zip(kids, labs):
            if l and tot[l] > 1:
                cnt[l] = cnt.get(l, 0) + 1
                l = f"{l} {cnt[l]}"
            if l:
                out.append((k["id"]["component"], k["id"]["element"], l))
            walk(k)
    walk(root)
    return out
