import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
from htmltree import *


def read_data(ss_url):
    scope = ["https://spreadsheets.google.com/feeds"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        "client_secret.json", scope
    )
    client = gspread.authorize(creds)
    ss = client.open_by_url(ss_url)

    PLACES = {}
    pla = [ws for ws in ss.worksheets() if ws.title == "Places"][0]
    all_values = pla.get_all_values()
    for row_i, row in enumerate(all_values):
        tmp = row[1].split(",")
        if len(tmp) == 2:
            lat, lon = float(tmp[0]), float(tmp[1])
        PLACES[row[0]] = (lat, lon)

    PERSONS = {}
    incnba = [ws for ws in ss.worksheets() if ws.title == "Incunabula"][0]
    all_values = incnba.get_all_values()
    for row_i, row in enumerate(all_values):
        name, place, date_start, date_end, link = (
            row[0],
            row[1],
            row[2],
            row[3],
            row[4],
        )
        if place not in PLACES:
            print(f"{place} not found in PLACES sheet")
            continue
        if len(link) < 4:
            link = None
        PERSONS.setdefault(name, []).append(
            {
                "ID": f"person_{row_i}",
                "NAME": name,
                "PLACE": place,
                "LATLON": PLACES[place],
                "START": date_start,
                "STOP": date_end,
                "LINK": link,
            }
        )

    return PERSONS, PLACES


def headbody():
    head = Head(
        Meta(charset="utf-8"),
        Meta(name="viewport", content="width=device-width, initial-scale=1"),
        Meta(name="author", content="Etienne Posthumus"),
        Title("Incunabula Printers"),
        Link(
            href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.1/dist/css/bootstrap.min.css",
            rel="stylesheet",
            integrity="sha384-+0n0xVW2eSR5OomGNYDnhzAbDsOXxcvSN1TPprVMTNDbiYZCxYbOOl7+AMvyTG2x",
            crossorigin="anonymous",
        ),
        Link(
            href="data:image/x-icon;base64,AAABAAEAEBAAAAAAAABoBQAAFgAAACgAAAAQAAAAIAAAAAEACAAAAAAAAAEAAAAAAAAAAAAAAAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAP//AAD8fwAA/H8AAPxjAAD/4wAA/+MAAMY/AADGPwAAxjEAAP/xAAD/8QAA4x8AAOMfAADjHwAA//8AAP//AAA=",
            rel="icon",
            type="image/x-icon",
        ),
        Link(rel="preconnect", href="https://fonts.gstatic.com"),
        Link(
            href="https://fonts.googleapis.com/css2?family=Literata&display=swap",
            rel="stylesheet",
        ),
        Link(
            rel="stylesheet",
            href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css",
            integrity="sha512-xodZBNTC5n17Xt2atTPuE1HxjVMSvLVW9ocqUKLsCC5CXdbqCmblAshOMAS6/keqq/sMZMZ19scR4PsZChSR7A==",
            crossorigin="",
        ),
        Link(
            rel="stylesheet",
            href="https://unpkg.com/leaflet.markercluster@1.4.1/dist/MarkerCluster.css",
        ),
        Link(
            rel="stylesheet",
            href="https://unpkg.com/leaflet.markercluster@1.4.1/dist/MarkerCluster.Default.css",
        ),
        Script(
            src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js",
            integrity="sha512-XQoYMqMTK8LvdxXYG3nZ448hOEQiglfqkJs1NOQV44cWnUrBc8PkAOcXy20w0vlaXaVUearIOBhiXZ5V3ynxwA==",
            crossorigin="",
        ),
        Script(
            src="https://unpkg.com/leaflet.markercluster@1.4.1/dist/leaflet.markercluster.js"
        ),
        Script(
            _async="",
            defer="",
            data_domain="bookhistory.typograaf.com",
            src="https://plausible.io/js/plausible.js",
        ),
    )

    body = Body(
        Header(
            *[
                H1(
                    "Incunabula Printers",
                    _class="banner",
                    style={"color": "#eee", "margin": "1vw 0 0 2vw"},
                ),
                Div(
                    *[
                        A(
                            "Github Repo",
                            href="https://github.com/epoz/incunabula",
                        ),
                    ],
                    style={
                        "position": "absolute",
                        "top": "0",
                        "right": "0",
                        "padding": "10px 10px 0 0",
                    },
                ),
            ]
        ),
        style={"background-color": "#444", "font-family": "'Literata', serif"},
    )
    return head, body


def doc(*args):
    tmp = "".join([a.render() for a in args])
    return f"""<!doctype html>
<html lang="en">
{tmp}
</html>"""


def main():
    head, body = headbody()
    persons, places = read_data(
        "https://docs.google.com/spreadsheets/d/1MMBS0HXemRLqBYbdymyXvv4kxgEfIu6zh7flDMZaCpc/edit#gid=995798083"
    )

    body.C.append(
        Div(
            Div(
                Div(
                    Input(
                        id="input_filter",
                        type="text",
                        placeholder="Type here to Filter Names",
                        style={"width": "100%"},
                    ),
                    style={"margin-bottom": "1ch"},
                ),
                Div(
                    *[
                        Div(
                            *[
                                P(
                                    obj,
                                    style={"margin": "0", "display": "inline"},
                                ),
                            ],
                            style={"margin": "0", "cursor": "pointer"},
                        )
                        for obj in sorted(persons.keys())
                    ],
                    id="printer_names",
                ),
                style={
                    "color": "#ccc",
                    "height": "90vh",
                    "overflow-y": "scroll",
                    "width": "30vw",
                },
            ),
            Div(
                Div(
                    Span("Begin 1450", id="span_begin"),
                    Input(
                        type="range",
                        min="1450",
                        max="1550",
                        value="1450",
                        id="slider_begin",
                        _class="dateslider",
                    ),
                    Span("End 1550", id="span_end", style={"margin-left": "1ch"}),
                    Input(
                        type="range",
                        min="1450",
                        max="1550",
                        value="1550",
                        id="slider_end",
                        _class="dateslider",
                    ),
                    style={
                        "margin-bottom": "0.5vw",
                        "text-align": "right",
                        "color": "#eee",
                    },
                ),
                Div(
                    id="mapid",
                    style={
                        "height": "88vh",
                        "width": "100%",
                        "border": "1px solid black",
                    },
                ),
                style={"height": "90vh", "width": "65vw"},
            ),
            style={
                "display": "flex",
                "margin": "1vw 0 0 2vw",
            },
        )
    )

    return doc(
        head,
        body,
        Script(
            src="https://cdn.jsdelivr.net/npm/bootstrap@5.0.1/dist/js/bootstrap.bundle.min.js",
            integrity="sha384-gtEjrD/SeCtmISkJkNUaaKMoLD0//ElJ19smozuHV6z3Iehds+3Ulb9Bn9Plx0x4",
            crossorigin="anonymous",
        ),
        Script("PERSONS = %s" % json.dumps(persons)),
        Script(open("incunabula.js").read()),
    )


open("incunabula.html", "w").write(main())
