function(feature, layer, context){
    let moyenne_ips = `${Math.round(feature.properties.moyenne_ips)}`;
    let nombre_etablissements = `${feature.properties.nombre_etablissements}`
    let final_text = `${moyenne_ips} de moyenne d'IPS sur ${nombre_etablissements} etablissements`
    if(feature.properties.moyenne_ips == null)
    {
        final_text="aucune donnee"
    }
    layer.bindTooltip(`${feature.properties.NOM} (${final_text})`);
}