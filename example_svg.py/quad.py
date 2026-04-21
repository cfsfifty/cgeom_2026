"""
Tutorial:
    https://developer.mozilla.org/en-US/docs/Web/SVG/Tutorial/Basic_Shapes
"""
import svg


def draw() -> svg.SVG:
    return svg.SVG(
        width=200,
        height=250,
        elements=[
            svg.Rect(
                x=0, y=0,
                width=200, height=250,
                stroke="black",
                fill="transparent",
                stroke_width=2,
            ),
            svg.Circle(
                cx=25, cy=75, r=20,
                stroke="red",
                fill="transparent",
                stroke_width=5,
            ),
            svg.Polyline(
                points=[
                    200, 150, 200, 200, 50, 200, 50, 150,
                    200, 150,
                ],
                stroke="orange",
                fill="transparent",
                stroke_width=5,
            ),
            #svg.Path(
            #    d=[
            #        svg.M(20, 230),
            #        svg.Q(40, 205, 50, 230),
            #        svg.T(90, 230),
            #    ],
            #    fill="none",
            #    stroke="blue",
            #    stroke_width=5,
            #),
            #svg.Polygon(
            #    points=[
            #        200, 150, 200, 200, 50, 200, 50, 150,
            #    ],
            #    stroke="green",
            #    fill="transparent",
            #    stroke_width=5,
            #),
        ],
    )


if __name__ == '__main__':    
    svg = draw()
    #print(svg)
    with open("quad.svg", 'w') as output:
        output.write(svg.as_str())

