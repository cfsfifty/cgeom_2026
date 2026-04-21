import datetime

triangulateAsFan = False

# "layer" is a QgsVectorLayer instance
layer = iface.activeLayer()

datetimeString = datetime.datetime.now().strftime("%Y%m%d")
with open(f"C:/Users/cfuen/source/ComputationGeometry_2025/{layer.name()}_{datetimeString}.obj", "w") as outFile:
    print(f"# Layer '{layer.name()}' from {datetimeString}", file=outFile)

    # all features
    #selectFeatures = layer.getFeatures()
    selectFeatures = layer.selectedFeatures()
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
                for (gi, g) in enumerate(arr):
                    print(f"g {feature['name']}", file=outFile, end='\n')
                    for points in g:
                        for p in points:
                            print(f"v {p[0]} {p[1]}", file=outFile, end='\n')
 
                        if not triangulateAsFan:
                            print(f"f", file=outFile, end='')
                            for pi in range(len(points)):
                                print(f" {pi+1}", file=outFile, end='')
                            print(f"", file=outFile, end='\n')
                        else:
                            for pi in range(2, len(points)):
                                print(f"f 1", file=outFile, end='')
                                print(f" {pi} {pi+1}", file=outFile, end='\n')
        else:
            print("Unknown or invalid geometry")
