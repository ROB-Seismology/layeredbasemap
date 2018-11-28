# Source: https://stackoverflow.com/questions/44143395/align-arbitrarily-rotated-text-annotations-relative-to-the-text-not-the-boundin

from __future__ import absolute_import, division, print_function, unicode_literals


from matplotlib import pyplot as plt
from matplotlib import patches, text
import numpy as np
import math


class TextTrueAlign(text.Text):
    """
    A Text object that always aligns relative to the text, not
    to the bounding box; also when the text is rotated.
    """
    def __init__(self, x, y, text, **kwargs):
        super(TextTrueAlign, self).__init__(x,y,text, **kwargs)
        self.__Ha = self.get_ha()
        self.__Va = self.get_va()
        self.__Rotation = self.get_rotation()
        self.__Position = self.get_position()

    def draw(self, renderer, *args, **kwargs):
        """
        Overload of the Text.draw() function
        """
        self.update_position()
        super(TextTrueAlign, self).draw(renderer, *args, **kwargs)

    def update_position(self):
        """
        As the (center/center) alignment always aligns to the center of the
        text, even upon rotation, we make use of this here. The algorithm
        first computes the (x,y) offset for the un-rotated text between
        centered alignment and the alignment requested by the user. This offset
        is then transformed according to the requested rotation angle and the
        aspect ratio of the graph. Finally the transformed offset is used to
        shift the text such that the alignment point coincides with the
        requested coordinate also when the text is rotated.
        """

        #resetting to the original state:
        self.set_rotation(0)
        self.set_va(self.__Va)
        self.set_ha(self.__Ha)
        self.set_position(self.__Position)

        ax = self.axes
        xy = self.__Position

        ##determining the aspect ratio:
        ##from https://stackoverflow.com/questions/41597177/get-aspect-ratio-of-axes
        ##data limits
        xlim = ax.get_xlim()
        ylim = ax.get_ylim()
        ## Axis size on figure
        figW, figH = ax.get_figure().get_size_inches()
        ## Ratio of display units
        _, _, w, h = ax.get_position().bounds
        ##final aspect ratio
        aspect = ((figW * w)/(figH * h))*(ylim[1]-ylim[0])/(xlim[1]-xlim[0])


        ##from https://stackoverflow.com/questions/5320205/matplotlib-text-dimensions
        ##getting the current renderer, so that
        ##get_window_extent() works
        renderer = ax.figure.canvas.get_renderer()

        ##computing the bounding box for the un-rotated text
        ##aligned as requested by the user
        bbox1  = self.get_window_extent(renderer=renderer)
        bbox1d = ax.transData.inverted().transform(bbox1)

        width  = bbox1d[1,0]-bbox1d[0,0]
        height = bbox1d[1,1]-bbox1d[0,1]

        ##re-aligning text to (center,center) as here rotations
        ##do what is intuitively expected
        self.set_va('center')
        self.set_ha('center')

        ##computing the bounding box for the un-rotated text
        ##aligned to (center,center)
        bbox2 = self.get_window_extent(renderer=renderer)
        bbox2d = ax.transData.inverted().transform(bbox2)

        ##computing the difference vector between the two
        ##alignments
        dr = np.array(bbox2d[0]-bbox1d[0])

        ##computing the rotation matrix, which also accounts for
        ##the aspect ratio of the figure, to stretch squeeze
        ##dimensions as needed
        rad = np.deg2rad(self.__Rotation)
        rot_mat = np.array([
            [math.cos(rad), math.sin(rad)*aspect],
            [-math.sin(rad)/aspect, math.cos(rad)]
        ])

        ##computing the offset vector
        drp = np.dot(dr,rot_mat)

        ##setting new position
        self.set_position((xy[0]-drp[0],xy[1]-drp[1]))

        ##setting rotation value back to the one requested by the user
        self.set_rotation(self.__Rotation)




if __name__ == '__main__':
    fig, axes = plt.subplots(3,3, figsize=(10,10), dpi=100)
    aligns = [ (va,ha) for va in ('top', 'center', 'bottom')
               for ha in ('left', 'center', 'right')]

    xys = [[i,j] for j in np.linspace(0.9,0.1,5) for i in np.linspace(0.1,0.9,5)]
    degs = np.linspace(0,360,25)

    for ax, align in zip(axes.reshape(-1), aligns):

        ax.set_xlim([-0.1,1.1])
        ax.set_ylim([-0.1,1.1])

        for deg,xy in zip(degs,xys):
            x, y = xy
            ax.plot(x,y,'r.')
            text = TextTrueAlign(
                x = xy[0],
                y = xy[1],
                text='test',
                axes = ax,
                rotation = deg,
                va = align[0],
                ha = align[1],
                bbox=dict(facecolor='none', edgecolor='blue', pad=0.0),
            )
            ax.add_artist(text)
            ax.set_title('alignment = {}'.format(align))

    fig.tight_layout()
    plt.show()
