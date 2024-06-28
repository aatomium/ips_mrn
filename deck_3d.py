import os

import dash
import dash_deck
import pydeck
import pandas as pd
from dash import Dash, html, Output, Input, State,dcc
import json
import dash_bootstrap_components as dbc

import dash_leaflet as dl
import dash_leaflet.express as dlx

from dash_extensions.javascript import arrow_function,assign

mapbox_api_token = "pk.eyJ1IjoicG90dGVyYWFhIiwiYSI6ImNsaGV6M2EyYzExbzYzZXBjZDIzb2s2YWgifQ.LvwhcrvYHJYn-3b_-wSQ1g"

placeholder_nom_etablissement = "NOM_ETABLISSEMENT"
placeholder_type_etablissement = "TYPE_ETABLISSEMENT"
placeholder_localisation_etablissement = "LOCALISATION_ETABLISSEMENT"
placeholder_ips_etablissement = "IPS_ETABLISSEMENT"
placeholder_image_etablissement = "/assets/placeholder.png"
def hex_to_rgb(value):
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))

INITIAL_VIEW_STATE = pydeck.ViewState(
    latitude=49.43911143788813, longitude=1.0980562166887944, zoom=11, max_zoom=16, pitch=45, bearing=0
)
def color_r(hex):
    return hex_to_rgb(hex)[0]
def color_g(hex):
    return hex_to_rgb(hex)[1]
def color_b(hex):
    return hex_to_rgb(hex)[2]
polygon = pydeck.Layer(
    'GeoJsonLayer',
    "assets/communes.geojson",
    id="communes",
    pickable=False,
    stroked=True,
    filled=True,
    extruded=False,  # Pas d'extrusion
    get_fill_color="properties.fill_color",
    get_line_color='[255, 255, 255, 255]',
    line_width_min_pixels=1,
)


geojson = pydeck.Layer(
    "GeoJsonLayer",
    "/assets/hauteur_etablissements.geojson",
    id="batiments",
    opacity=0.8,
    stroked=False,
    pickable=False,
    filled=True,
    extruded=True,
    wireframe=True,
    get_elevation="properties.hauteur",
    get_fill_color="[255, 255, 130]",
    get_line_color=[255, 255, 255],
)
factor = 5
etablissements = pydeck.Layer(
    "GeoJsonLayer",
    "assets/etablissements.geojson",
    pickable=True,
    id="etablissements",
    opacity=0.8,
    stroked=True,
    filled=True,
    radius_scale=6,
    radius_min_pixels=1,
    radius_max_pixels=100,
    line_width_min_pixels=1,
    get_radius="100",
    get_fill_color=[255, 140, 0],
    get_line_color=[0, 0, 0],
)
r = pydeck.Deck(
    layers=[polygon, geojson,etablissements],
    initial_view_state=INITIAL_VIEW_STATE,
    api_keys={"mapbox": mapbox_api_token},
)


app = dash.Dash(__name__,external_stylesheets=[dbc.themes.DARKLY])
app.title = "Carte IPS - Métropole Rouen Normandie"
tab1 = dbc.Tab(
    html.Div(
        [
            dbc.Modal(
                [
                    dbc.ModalHeader(dbc.ModalTitle(placeholder_nom_etablissement,id="nom_etablissement_tab1")),
                    dbc.ModalBody(placeholder_type_etablissement,id="type_etablissement_tab1"),
                    dbc.ModalBody(placeholder_localisation_etablissement,id="localisation_etablissement_tab1"),
                    dbc.ModalBody(placeholder_ips_etablissement,id="ips_etablissement_tab1"),
                    dbc.CardImg(src=placeholder_image_etablissement, id="image_etablissement_tab1"),
                    dbc.ModalFooter(dbc.Button("Close", id="close_tab1", className="ms-auto", n_clicks=0))
                ],id="modal_tab1",is_open=False
            ),
            dash_deck.DeckGL(r.to_json(), id="deck-gl", enableEvents=True, mapboxKey=r.mapbox_key,style={'top': '40px','height':'95%'})
        ]),
    label="Carte 3D", tab_id="t1"
)
f = open("methodo.md",encoding="utf8")
tab2 = dbc.Tab(
    html.Div(
        [
            dcc.Markdown(f.read(),style={'top': '60px','position' : 'absolute','left' : '10px'})

        ]),
        label="Méthodologie", tab_id="t2"
    )

classes = [0, 95, 101, 109, 120, 137]
colorscale = ['#e25756', '#fec38a', '#ffffd1', '#c2e5bd', '#66a2cd']
style = dict(weight=2, opacity=1, color='white', dashArray='3', fillOpacity=0.7)
# Create colorbar.
ctg = ["{} - {}".format(cls, classes[i + 1], classes[i+2]) for i, cls in enumerate(classes[:-2])] + ["{} - {}".format(classes[-2],classes[-1])]
colorbar = dlx.categorical_colorbar(categories=ctg, colorscale=colorscale, width=300, height=30, position="bottomleft")
# Geojson rendering logic, must be JavaScript as it is executed in clientside.
style_handle = assign(open("style_handle.js").read())
on_each_feature = assign(open("on_each_feature.js").read())

tab3 = dbc.Tab( html.Div([
    dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle(placeholder_nom_etablissement,id="nom_etablissement")),
            dbc.ModalBody(placeholder_type_etablissement,id="type_etablissement"),
            dbc.ModalBody(placeholder_localisation_etablissement,id="localisation_etablissement"),
            dbc.ModalBody(placeholder_ips_etablissement,id="ips_etablissement"),
            dbc.CardImg(src=placeholder_image_etablissement, id="image_etablissement"),
            dbc.ModalFooter(dbc.Button("Close", id="close", className="ms-auto", n_clicks=0))
        ],id="modal",is_open=False
    ),
    dl.Map(center=[49.41969,1.05229], zoom=11, children=[
        dl.TileLayer(),
        dl.GeoJSON(url="/assets/communes.geojson",
                   style=style_handle,
                   id="map_ips",
                   onEachFeature=on_each_feature,
                   hideout=dict(colorscale=colorscale, classes=classes, style=style, colorProp="moyenne_ips"),),
        dl.GeoJSON(url='/assets/etablissements.geojson', id="map_etablissements",cluster=True, zoomToBoundsOnClick=True,
                   superClusterOptions={"radius": 100}),
        colorbar
    ],style={'height': '100vh'}),
    html.Div(id="capital"),

]),label="Carte 2D", tab_id="t3",style={"top":"60px","position":"relative","left" : "-300px"})
app.layout = dbc.Container(dbc.Tabs([tab3, tab1, tab2], active_tab='t3', id='tabs',style={'left':'0px', 'position' : 'absolute'}))

@app.callback(
    Output("modal_tab1", "is_open"),
    Output("nom_etablissement_tab1","children"),
    Output("type_etablissement_tab1","children"),
    Output("localisation_etablissement_tab1","children"),
    Output("ips_etablissement_tab1","children"),
    Output("image_etablissement_tab1","src"),
    [Input("close_tab1", "n_clicks"),Input("deck-gl","clickInfo")],
    [State("modal_tab1", "is_open")],
)
def toggle_modal_tab1(close, infos_open, is_open):
    if infos_open:
        if infos_open['layer']:
            prop = infos_open['object']['properties']
            nom = f"{prop['appellation_officielle']} ({prop['libelle_commune']})" 
            typee = f"Type d'établissement : {prop['denomination_principale']}, établissement {prop['secteur_public_prive_libe'].lower()}"
            localisation = f"Situé {prop['adresse_uai']}, à {prop['libelle_commune']} ({prop['code_postal_uai']})"
            try:
                ips = f"IPS de {prop['fr-en-ips_ecoles_v2_ips'] or prop['fr-en-ips_colleges_v2_ips'] or prop['fr-en-ips_lycees_ips_ensemble_gt_pro']}"
            except:
                ips = "IPS indéfini"
            import os
            liste_images = [i for i in os.listdir("assets/images/") if prop['numero_uai'] in i]
            if not liste_images:
                image = placeholder_image_etablissement
            else:
                image = "assets/images/"+liste_images[0]
            return not is_open,nom,typee,localisation,ips,image
        return is_open,placeholder_nom_etablissement,placeholder_type_etablissement,placeholder_localisation_etablissement,placeholder_ips_etablissement,placeholder_image_etablissement
    elif close:
        return not is_open, placeholder_nom_etablissement,placeholder_type_etablissement,placeholder_localisation_etablissement,placeholder_ips_etablissement,placeholder_image_etablissement
    return is_open,placeholder_nom_etablissement,placeholder_type_etablissement,placeholder_localisation_etablissement,placeholder_ips_etablissement,placeholder_image_etablissement

@app.callback(
    Output("modal", "is_open"),
    Output("nom_etablissement","children"),
    Output("type_etablissement","children"),
    Output("localisation_etablissement","children"),
    Output("ips_etablissement","children"),
    Output("image_etablissement","src"),
    [Input("close", "n_clicks"),Input("map_etablissements","clickData")],
    [State("modal", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        prop = n2['properties']
        if not prop['cluster']:
            nom = f"{prop['appellation_officielle']} ({prop['libelle_commune']})" 
            typee = f"Type d'établissement : {prop['denomination_principale']}, établissement {prop['secteur_public_prive_libe'].lower()}"
            localisation = f"Situé {prop['adresse_uai']}, à {prop['libelle_commune']} ({prop['code_postal_uai']})"
            try:
                ips = f"IPS de {prop['fr-en-ips_ecoles_v2_ips'] or prop['fr-en-ips_colleges_v2_ips'] or prop['fr-en-ips_lycees_ips_ensemble_gt_pro']}"
            except:
                ips = "IPS indéfini"
            import os
            liste_images = [i for i in os.listdir("assets/images/") if prop['numero_uai'] in i]
            if not liste_images:
                image = placeholder_image_etablissement
            else:
                image = "assets/images/"+liste_images[0]
            return not is_open,nom,typee,localisation,ips,image
    return is_open,placeholder_nom_etablissement,placeholder_type_etablissement,placeholder_localisation_etablissement,placeholder_ips_etablissement,placeholder_image_etablissement

if __name__ == "__main__":
    app.run_server(port=80,host="0.0.0.0")