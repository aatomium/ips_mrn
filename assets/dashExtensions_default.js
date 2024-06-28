window.dashExtensions = Object.assign({}, window.dashExtensions, {
    default: {
        function0: function(feature, context) {
            const {
                classes,
                colorscale,
                style,
                colorProp
            } = context.hideout;
            const value = feature.properties[colorProp];
            if (value == null) {
                style.fillColor = '#808080';
                return style;
            }
            for (let i = 0; i < classes.length; ++i) {
                if (value > classes[i]) {
                    style.fillColor = colorscale[i];
                }
            }
            return style;
        },
        function1: function(feature, layer, context) {
            let moyenne_ips = `${Math.round(feature.properties.moyenne_ips)}`;
            let nombre_etablissements = `${feature.properties.nombre_etablissements}`
            let final_text = `${moyenne_ips} de moyenne d'IPS sur ${nombre_etablissements} etablissements`
            if (feature.properties.moyenne_ips == null) {
                final_text = "aucune donnee"
            }
            layer.bindTooltip(`${feature.properties.NOM} (${final_text})`);
        }
    }
});