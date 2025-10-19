# AnimaGeo

## Installation

```bash
pip install --upgrade animageo
```

## Using in terminal

```bash
animageo test.ggb -s default.json -px 240 auto
```

*Description:*

```
usage: animageo ggbfile [-o OUTPUT] [-px PX PX] [-s STYLE] [-d DEBUG]

positional arguments:
  ggbfile                       GeoGebra file to parse

options:
  -o OUTPUT, --output OUTPUT    SVG file to export into
  -px PX PX                     image width and height in px (values: num or auto)
  -s STYLE, --style STYLE       JSON file with style definitions    
  -d DEBUG, --debug DEBUG       print options

  -h, --help                    show this help message and exit
```

## Using in code

1. Preparing code `test.py`:

```python
from animageo import *

class TestScene(AnimaGeoScene):
    def construct(self):       
        self.loadGeoGebra('test.ggb', style_json_file = 'default.json', px_size = [400, 'auto'])    
        self.exportSVG('test.svg')
```

2. Run compilation:

```bash
manim 'test.py' TestScene
```


## Style definitions in JSON

Here is an example of JSON-file for styling images:

```json
{
   "name": "default",
   "version": 0.1,
   "style": {
       "dot": {
           "main": 7,
           "bold": 9,
           "aux": 5
       },
       "line": {
           "main": 2,
           "bold": 2.5,
           "aux": 1.5
       },
       "angle": {
           "line": 1,
           "r_default": 20,
           "r_shift": 3,
           "r_right": 14
       },
       "strich": {
           "width": 1,
           "len": 12,
           "shift": 4
       },
       "arrow": {
           "width": 7.5,
           "length": 10.5
       },
       "color": {
           "black": "#000000",
           "main": "#2581b5",
           "light": "#bef3fc",
           "aux": "#000000",
           "acc": "#ef60ab",
           "acc_light": "#ffd2ee"
       },
       "font": {
           "size": 17
       }
   },
   "technic": {
       "line_caps": "round",
       "right_angle_joint": "miter",
       "polygon_boundary_layer": "top",
       "points_display": "only_labels",
       "crop_padding": 4,
       "scale_export": 0.75
   },
   "ggb_export": {
       "colors": {
           "#1565c0": "main",
           "#1565c0 0.1": "main 0",
           "#d32f2f": "acc",
           "#d32f2f 0.1": "acc_light 1",
           "#616161": "aux",
           "#000000 0.6": "main",
           "#000000 0.1": "light 1",
           "#1565c0 0": "white 1",
           "#d32f2f 0": "white 1"
       },
       "dot": {
           "5": "main"
       },
       "line": {
           "5": "main",
           "3": "aux"
       }
   }
}

```


*Description:*

**technic:**

*round* - закруглять концы всех отрезков
*butt* - обрезать концы всех отрезков
*square* - концы отрезков завершаются квадратами
```json
        "line_caps": "round" | "butt" | "square",  
```

*round* - скруглять соединение уголка в отображении отметки прямого угла
```json
        "right_angle_joint": "round" | "bevel" | "miter" 
```

*top* - отображать границу многоугольников поверх остальных линий (Важно! это касается именно дополнительных отрезков-сторон, создаваемых автоматически в GeoGebra)
```json
        "polygon_boundary_layer": "top" | "auto"
```

*only_labels* - скрывать все точки (оставляя их надписи, если они есть)
*only_points* - скрывать надписи (оставляя точки, если они видимые)
```json
        "points_display": "only_labels" | "only_points" | "auto"
```

обрезать картинку по содержимому, оставляя поле 4px
```json
        "crop_padding": 4 
```

вспомогательный коэффициент растяжения/сжатия всех параметров при экспорте в svg (должен влиять и на размеры и на толщины, стили…)
```json
        "scale_export": 0.75,  1 
```

**ggb_export:**

конвертирует конкретные цвета из GeoGebra в другие цвета c возможным параметром прозрачности (цвет либо конкретный, либо по имени из стилевика)
```json
    "colors": {}
```

конвертирует определенную ширину линии из GeoGebra в другую заданную ширину (величина либо конкретная, либо по имени из стилевика)
```json
    "line": {}
```

конвертирует определенный размер точек из GeoGebra в другой заданный размер (величина либо конкретная, либо по имени из стилевика)
```json
    "dot": {}
```