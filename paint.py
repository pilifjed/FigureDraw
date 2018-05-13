import json
from PIL import Image, ImageDraw, ImageShow
import argparse, sys


class JsonParser:
    def __init__(self, filename):
        with open(filename, "r") as read_file:
            rawdata = json.load(read_file)

        rawfigures = rawdata['Figures']
        palette = rawdata['Palette']
        rawScreen = rawdata['Screen']

        figs = []
        ln = 0
        for fig in rawfigures:
            if 'color' in fig:
                color = fig['color']
            else:
                color = 'fg_color'

            try:
                t = fig['type']

                if (t == 'point'):
                    coord = (fig['x'], fig['y'])
                    figs.append(Point(coord, color))

                elif (t == 'polygon'):
                    points = [tuple(x) for x in fig['points']]
                    figs.append(Polygon(points, color))

                elif (t == 'rectangle'):
                    poz = (fig['x'], fig['y'])
                    size = (fig['width'], fig['height'])
                    figs.append(Rectangle(poz, size, color))

                elif (t == 'square'):
                    poz = (fig['x'], fig['y'])
                    size = fig['size']
                    figs.append(Square(poz, size, color))

                elif (t == 'circle'):
                    poz = (fig['x'], fig['y'])
                    radius = fig['radius']
                    figs.append(Circle(poz, radius, color))

            except KeyError as e:
                print("Error while parsing JSON file. Bad syntax in line " + str(ln) + " of file " + filename + "\n" +
                      "Following figure will be ignored: " + str(fig) + "\n" +
                      "Lacking parameter: " + str(e))
            ln += 1

        screen_params = (
            rawScreen.get('bg_color'),
            rawScreen.get('fg_color'),
            (rawScreen.get('width'), rawScreen.get('height'))
        )

        if screen_params[0] == None:
            screen_params[0] = (255, 255, 255)
        if screen_params[1] == None:
            screen_params[1] = (0, 0, 0)
        if screen_params[2][0] == None:
            screen_params[2][0] = 640
        if screen_params[2][1] == None:
            screen_params[2][1] = 480

        self.screen = Screen(screen_params, figs, palette)
        self.screen.normalize_colors()
        self.screen.draw_figures()

    def __str__(self):
        return str(vars(self))

    def __repr__(self):
        return self.__str__()


class Screen:
    def __init__(self, bg_fg_size, figures, palette={}):
        self.bg_color = bg_fg_size[0]
        self.fg_color = bg_fg_size[1]
        self.size = bg_fg_size[2]
        self.palette = palette
        self.figures = figures
        self.canv = Image.new("RGB", self.size, self.bg_color)

    def parse_color(self, color):
        if color[0] == '#':
            return color
        if color[0] == '(':
            return eval(color)
        else:
            replace = self.palette.get(color)
            if replace != None:
                return replace
            else:
                return color

    def normalize_colors(self):
        for fig in self.figures:
            if fig.color == "fg_color":
                fig.color = self.fg_color
            fig.color = self.parse_color(fig.color)

    def draw_figures(self):
        for fig in self.figures:
            fig.draw_on(self)

    def __str__(self):
        return str(vars(self))

    def __repr__(self):
        return self.__str__()

    def display(self):
        self.canv.show()

    def save(self, fname):
        self.canv.save(fname, "PNG")


class Figure:
    def __init__(self, color):
        self.color = color

    def get_type(self):
        return type(self).__name__

    def __str__(self):
        tmp = vars(self)
        tmp['type'] = self.get_type()
        return "\n\t" + str(tmp)

    def __repr__(self):
        return self.__str__()


class Point(Figure):
    def __init__(self, poz, color='fg_color'):
        super(Point, self).__init__(color)
        self.poz = poz

    def draw_on(self, screen):
        draw = ImageDraw.Draw(screen.canv)
        draw.point([self.poz], fill=self.color)
        del draw


class Polygon(Figure):
    def __init__(self, points, color='fg_color'):
        super(Polygon, self).__init__(color)
        self.points = points

    def draw_on(self, screen):
        draw = ImageDraw.Draw(screen.canv)
        draw.polygon(self.points, fill=self.color)
        del draw


class Rectangle(Figure):
    def __init__(self, poz, size, color='fg_color'):
        super(Rectangle, self).__init__(color)
        self.poz = poz
        self.size = size

    def draw_on(self, screen):
        draw = ImageDraw.Draw(screen.canv)
        draw.rectangle([(self.poz[0] - self.size[0] / 2, self.poz[1] - self.size[1] / 2),
                        (self.poz[0] + self.size[0] / 2, self.poz[1] + self.size[1] / 2)], fill=self.color)
        del draw


class Square(Rectangle):
    def __init__(self, poz, size, color='fg_color'):
        super(Square, self).__init__(poz, (size, size), color)


class Circle(Figure):
    def __init__(self, poz, radius, color='fg_color'):
        super(Circle, self).__init__(color)
        self.poz = poz
        self.radius = radius

    def draw_on(self, screen):
        draw = ImageDraw.Draw(screen.canv)
        draw.ellipse([(self.poz[0] - self.radius, self.poz[1] - self.radius),
                      (self.poz[0] + self.radius, self.poz[1] + self.radius)], fill=self.color)
        del draw


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("fname", help="Name of file which is supposed to be parsed")
    parser.add_argument("-o", "--output", help="Output will be saved to file")
    args = parser.parse_args()

    engine = JsonParser(args.fname)

    engine.screen.display()

    if args.output:
        engine.screen.save(args.output + ".png")


if __name__ == '__main__':
    main()
