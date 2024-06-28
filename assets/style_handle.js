function(feature, context){
    const {classes, colorscale, style, colorProp} = context.hideout;
    const value = feature.properties[colorProp];
    if(value==null)
    {
        style.fillColor = '#808080';
        return style;
    }
    for (let i = 0; i < classes.length; ++i) {
        if (value > classes[i]) {
            style.fillColor = colorscale[i];
        }
    }
    return style;
}