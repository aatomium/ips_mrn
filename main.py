import dash_leaflet as dl
import dash_leaflet.express as dlx
from dash import Dash, html, Output, Input, State
from dash_extensions.javascript import arrow_function,assign
import dash_bootstrap_components as dbc

import requests

classes = [0, 95, 101, 109, 120, 137]
colorscale = ['#e25756', '#fec38a', '#ffffd1', '#c2e5bd', '#66a2cd']
style = dict(weight=2, opacity=1, color='white', dashArray='3', fillOpacity=0.7)
# Create colorbar.
ctg = ["{} - {}".format(cls, classes[i + 1], classes[i+2]) for i, cls in enumerate(classes[:-2])] + ["{} - {}".format(classes[-2],classes[-1])]
colorbar = dlx.categorical_colorbar(categories=ctg, colorscale=colorscale, width=300, height=30, position="bottomleft")
# Geojson rendering logic, must be JavaScript as it is executed in clientside.
style_handle = assign(open("style_handle.js").read())
on_each_feature = assign(open("on_each_feature.js").read())
# Create example app.
nom_etablissement_placeholder = "NOM_ETABLISSEMENT"
type_etablissement_placeholder = "TYPE_ETABLISSEMENT"
localisation_etablissement_placeholder = "LOCALISATION_ETABLISSEMENT"
ips_etablissement_placeholder = "IPS_ETABLISSEMENT"
image_etablissement_placeholder = "/assets/placeholder.png"
app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
app.layout = html.Div([
    dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle(nom_etablissement_placeholder,id="nom_etablissement")),
            dbc.ModalBody(type_etablissement_placeholder,id="type_etablissement"),
            dbc.ModalBody(localisation_etablissement_placeholder,id="localisation_etablissement"),
            dbc.ModalBody(ips_etablissement_placeholder,id="ips_etablissement"),
            dbc.CardImg(src=image_etablissement_placeholder, id="image_etablissement"),
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
    html.Div(id="capital")
])

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
            query = f"{prop['appellation_officielle'].lower().replace(' ','+')}+{prop['libelle_commune'].lower().replace(' ','+')}+image"
            import os
            liste_images = [i for i in os.listdir("assets/images/") if prop['numero_uai'] in i]
            if not liste_images:
                image = image_etablissement_placeholder
            else:
                image = "assets/images/"+liste_images[0]
            return not is_open,nom,typee,localisation,ips,image
    return is_open,nom_etablissement_placeholder,type_etablissement_placeholder,localisation_etablissement_placeholder,ips_etablissement_placeholder,image_etablissement_placeholder
if __name__ == '__main__':
    app.run_server(port=7777)