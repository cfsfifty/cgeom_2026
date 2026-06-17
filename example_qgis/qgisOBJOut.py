import datetime

# "layer" is a QgsVectorLayer instance
layer = iface.activeLayer()

datetimeString = datetime.datetime.now().strftime("%Y%m%d")
with open(f"c:/users/user/Talks/cgeom_2026/example_qgis/{layer.name()}_{datetimeString}.obj", "w") as outFile:
    print(f"# Layer '{layer.name()}' from {datetimeString}", file=outFile)

    # all features
    #selectFeatures = layer.getFeatures()
    selectFeatures = layer.selectedFeatures()
    poly_num_verts = 0
    for feature in selectFeatures:    
        # retrieve every feature with its geometry and attributes
        print("Feature ID: ", feature.id())
        # fetch attributes
        attrs = feature.attributes()
        # attrs is a list. It contains all the attribute values of this feature
        print(attrs)

        # fetch geometry
        # show some information about the feature geometry
        geom = feature.geometry()
        geomSingleType = QgsWkbTypes.isSingleType(geom.wkbType())
        if geom.type() == QgsWkbTypes.PointGeometry:
            # the geometry type can be of single or multi type
            if geomSingleType:
                x = geom.asPoint()
                print("Point: ", x)
            else:
                x = geom.asMultiPoint()
                print("MultiPoint: ", x)
        elif geom.type() == QgsWkbTypes.LineGeometry:
            if geomSingleType:
                x = geom.asPolyline()
                print("Line: ", x)
            else:
                x = geom.asMultiPolyline()
                print("MultiLine: ", x, "length: ", geom.length())
        elif geom.type() == QgsWkbTypes.PolygonGeometry:
            if geomSingleType:
                x = geom.asPolygon()
                print("Polygon: ", x, "Area: ", geom.area())
            else:
                arr = geom.asMultiPolygon()
                print("MultiPolygon: ", arr)
                for faces in arr:
                    print(f"g {feature['name']}", file=outFile, end='\n')
                    for points in faces:
                        for pi, p in enumerate(points):
                            if pi == len(points)-1:
                               break 
                            print(f"v {p[0]} {p[1]}", file=outFile, end='\n')
 
                        print(f"f", file=outFile, end='')
                        for fi in range(len(points)-1): # last point equals first point; omit
                            gi = poly_num_verts+fi+1
                            print(f" {gi}", file=outFile, end='')
                        print(f"", file=outFile, end='\n')
                        poly_num_verts += len(points)-1
        else:
            print("Unknown or invalid geometry")
