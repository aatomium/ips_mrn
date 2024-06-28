#!/usr/bin/env python

"""
File: main.py

Description: Main program for my IPS map website. Made with Dash, Dash Leaflet, Dash Deck and Dash Boostrap.
"""

__author__ = "Orian Latroupe"
__contact__ = " (orian.latroupe@gmail.com)"
__date__ = "2024-06-28"
__version__ = "1.0"

import os

import dash
from dash import html, Output, Input, State,dcc
import dash_deck
import dash_leaflet as dl
import dash_leaflet.express as dlx
import dash_bootstrap_components as dbc
from dash_extensions.javascript import assign

import pydeck

##############
##   MAIN   ##
##############
mapbox_api_token = os.environ['MAPBOX_TOKEN']

# placeholders for the modal
placeholder_nom_etablissement = "NOM_ETABLISSEMENT"
placeholder_type_etablissement = "TYPE_ETABLISSEMENT"
placeholder_localisation_etablissement = "LOCALISATION_ETABLISSEMENT"
placeholder_ips_etablissement = "IPS_ETABLISSEMENT"
placeholder_image_etablissement = "/assets/images/placeholder.png"

# Create Dash app
app = dash.Dash(__name__,external_stylesheets=[dbc.themes.DARKLY])
app.title = "Carte IPS - Métropole Rouen Normandie"


#####################
## First tab : 2D map

# Define classes and colorscale
classes = [0, 95, 101, 109, 120, 137]
colorscale = ['#e25756', '#fec38a', '#ffffd1', '#c2e5bd', '#66a2cd']
style = dict(weight=2, opacity=1, color='white', dashArray='3', fillOpacity=0.7)

# Create colorbar.
ctg = ["{} - {}".format(cls, classes[i + 1], classes[i+2]) for i, cls in enumerate(classes[:-2])] + ["{} - {}".format(classes[-2],classes[-1])]
colorbar = dlx.categorical_colorbar(categories=ctg, colorscale=colorscale, width=300, height=30, position="bottomleft")

# Geojson rendering logic, must be JavaScript as it is executed in clientside.
style_handle = assign(open("assets/style_handle.js").read())
on_each_feature = assign(open("assets/on_each_feature.js").read())

tab_2d = dbc.Tab(html.Div([
    # modal displayed on click
    dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle(placeholder_nom_etablissement,id="nom_etablissement_2d")),
            dbc.ModalBody(placeholder_type_etablissement,id="type_etablissement_2d"),
            dbc.ModalBody(placeholder_localisation_etablissement,id="localisation_etablissement_2d"),
            dbc.ModalBody(placeholder_ips_etablissement,id="ips_etablissement_2d"),
            dbc.CardImg(src=placeholder_image_etablissement, id="image_etablissement_2d"),
            dbc.ModalFooter(dbc.Button("Close", id="close_2d", className="ms-auto", n_clicks=0))
        ],id="modal_2d",is_open=False
    ),
    # 2D map
    dl.Map(center=[49.41969,1.05229], zoom=11, children=[
        dl.TileLayer(),
        dl.GeoJSON(url="/assets/communes.geojson",
                   style=style_handle,
                   id="map_ips",
                   onEachFeature=on_each_feature,
                   hideout=dict(colorscale=colorscale, classes=classes, style=style, colorProp="moyenne_ips"),),
        dl.GeoJSON(url='/assets/etablissements.geojson', id="map_etablissements",cluster=True, zoomToBoundsOnClick=True,
                   superClusterOptions={"radius": 100}),
        dl.GeoJSON(url='assets/seine.geojson'),
        colorbar
    ],style={'height': '93vh'}),

]),label="Carte 2D", tab_id="t_2d",style={"top":"60px","position":"relative","width" : "100%"})

@app.callback(
    Output("modal_2d", "is_open"),
    Output("nom_etablissement_2d","children"),
    Output("type_etablissement_2d","children"),
    Output("localisation_etablissement_2d","children"),
    Output("ips_etablissement_2d","children"),
    Output("image_etablissement_2d","src"),
    [Input("close_2d", "n_clicks"),Input("map_etablissements","clickData")],
    [State("modal_2d", "is_open")],
)
def toggle_modal_2d(close, infos_open, is_open):
    """
    Callback when the modal is toogled.

    @param boolean close : 1 if modal was toogle by close button, 0 otherwise 
    @param dict open : dictionnary with infos on establishment which was clicked if one was, None otherwise
    @param boolean is_open : boolean which specify if the modal is currently open or closed 
    @returns :
        - is_open boolean : 1 if we want the modal to be opened, 0 otherwise
        - nom_etablissement string : name of establishment that we wanna display on modal
        - type_etablissement string : type of establishment that we wanna display on modal
        - localisation_etablissement string : localisation of establishment that we wanna display on modal
        - ips_etablissement string : IPS of establishment that we wanna display on modal
        - image_etablissement string : image of establishment that we wanna display on modal
    """
    if close or infos_open:
        # get properties of establishment which was clicked
        prop = infos_open['properties']
        # verify the clicked data is not a cluster
        if not prop['cluster']:
            nom = f"{prop['appellation_officielle']} ({prop['libelle_commune']})" 
            typee = f"Type d'établissement : {prop['denomination_principale']}, établissement {prop['secteur_public_prive_libe'].lower()}"
            localisation = f"Situé {prop['adresse_uai']}, à {prop['libelle_commune']} ({prop['code_postal_uai']})"
            try:
                ips = f"IPS de {prop['fr-en-ips_ecoles_v2_ips'] or prop['fr-en-ips_colleges_v2_ips'] or prop['fr-en-ips_lycees_ips_ensemble_gt_pro']}"
            except:
                ips = "IPS indéfini"
            
            # get image if exists
            liste_images = [i for i in os.listdir("assets/images/") if prop['numero_uai'] in i]
            if not liste_images:
                image = placeholder_image_etablissement
            else:
                image = "assets/images/"+liste_images[0]
            return not is_open,nom,typee,localisation,ips,image
    # if function was called without any trigger, return is_open as it was and placeholders
    return is_open,placeholder_nom_etablissement,placeholder_type_etablissement,placeholder_localisation_etablissement,placeholder_ips_etablissement,placeholder_image_etablissement


######################
## Second tab : 3D map

# Create all the layers : for cities, educational establishments - 3D and pins - and for the Seine

communes = pydeck.Layer(
    'GeoJsonLayer',
    "assets/communes.geojson",
    id="communes",
    pickable=False,
    stroked=True,
    filled=True,
    extruded=False,  # No extrusion
    get_fill_color="properties.fill_color",
    get_line_color='[255, 255, 255, 255]',
    line_width_min_pixels=1,
)

etablissements_3d = pydeck.Layer(
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

etablissements_pins = pydeck.Layer(
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

seine = pydeck.Layer(
    "GeoJsonLayer",
    "assets/seine.geojson",
    pickable=False,
    line_width_min_pixels=5,
    get_line_color=[0,0,255]
)

# define initial view state
INITIAL_VIEW_STATE = pydeck.ViewState(
    latitude=49.43911143788813, longitude=1.0980562166887944, zoom=11, max_zoom=16, pitch=45, bearing=0
)

# create the Deck
deck = pydeck.Deck(
    layers=[communes, etablissements_pins,etablissements_3d,seine],
    initial_view_state=INITIAL_VIEW_STATE,
    api_keys={"mapbox": mapbox_api_token},
)

tab_3d = dbc.Tab(
    html.Div(
        [
            # modal
            dbc.Modal(
                [
                    dbc.ModalHeader(dbc.ModalTitle(placeholder_nom_etablissement,id="nom_etablissement_3d")),
                    dbc.ModalBody(placeholder_type_etablissement,id="type_etablissement_3d"),
                    dbc.ModalBody(placeholder_localisation_etablissement,id="localisation_etablissement_3d"),
                    dbc.ModalBody(placeholder_ips_etablissement,id="ips_etablissement_3d"),
                    dbc.CardImg(src=placeholder_image_etablissement, id="image_etablissement_3d"),
                    dbc.ModalFooter(dbc.Button("Close", id="close_3d", className="ms-auto", n_clicks=0))
                ],id="modal_3d",is_open=False
            ),
            # 3D map
            dash_deck.DeckGL(deck.to_json(), id="deck-gl", enableEvents=True, mapboxKey=deck.mapbox_key,style={'position': 'relative','top': '70px','height':'92vh'})
        ]),
    label="Carte 3D", tab_id="t1"
)

# callback for toogle modal
@app.callback(
    Output("modal_3d", "is_open"),
    Output("nom_etablissement_3d","children"),
    Output("type_etablissement_3d","children"),
    Output("localisation_etablissement_3d","children"),
    Output("ips_etablissement_3d","children"),
    Output("image_etablissement_3d","src"),
    [Input("close_3d", "n_clicks"),Input("deck-gl","clickInfo")],
    [State("modal_3d", "is_open")],
)
def toggle_modal_3d(close, infos_open, is_open):
    """
    Callback when the modal is toogle 

    @param boolean close : 1 if modal was toogle by close button, 0 otherwise 
    @param dict infos_open : dictionnary with infos on establishment which was clicked if it was, None otherwise
    @param boolean is_open : boolean which specify if the modal is currently open or closed 
    @returns :
        - is_open boolean : 1 if we want the modal to be opened, 0 otherwise
        - nom_etablissement string : name of establishment that we wanna display on modal
        - type_etablissement string : type of establishment that we wanna display on modal
        - localisation_etablissement string : localisation of establishment that we wanna display on modal
        - ips_etablissement string : IPS of establishment that we wanna display on modal
        - image_etablissement string : image of establishment that we wanna display on modal
    """
    if infos_open:
        # get properties of establishment which was clicked
        prop = infos_open['object']['properties']
        # verify the clicked data is on the establishment layer (otherwise Layer is None for unknown reason)
        if infos_open['layer']:
            nom = f"{prop['appellation_officielle']} ({prop['libelle_commune']})" 
            typee = f"Type d'établissement : {prop['denomination_principale']}, établissement {prop['secteur_public_prive_libe'].lower()}"
            localisation = f"Situé {prop['adresse_uai']}, à {prop['libelle_commune']} ({prop['code_postal_uai']})"
            try:
                ips = f"IPS de {prop['fr-en-ips_ecoles_v2_ips'] or prop['fr-en-ips_colleges_v2_ips'] or prop['fr-en-ips_lycees_ips_ensemble_gt_pro']}"
            except:
                ips = "IPS indéfini"
            
            # get image if exists
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


######################
## Third tab : methodo


# Open Markdown file as "methodo.md" and setup it in a tab
f = open("assets/methodo.md",encoding="utf8")
tab_metho = dbc.Tab(
    html.Div(
        [
            dcc.Markdown(f.read(),style={'top': '60px','position' : 'absolute','left' : '10px'})
        ]),
        label="Méthodologie", tab_id="t2"
    )


# create the final layout of our app, with the 3 tabs, and start the app
app.layout = dbc.Container(dbc.Tabs([tab_2d, tab_3d, tab_metho], active_tab='t_2d', id='tabs',style={'left':'0px', 'position' : 'absolute'}))
if __name__ == "__main__":
    app.run_server(port=80,host="0.0.0.0")