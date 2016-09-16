"""
Test to plot frontlines in matplotlib using markers

Author: Kris Vanneste, Royal Observatory of Belgium, 2014
"""

from types import MethodType
import numpy as np
import matplotlib as mpl
import matplotlib.mlab as mlab


class FrontlineLegendHandler(object):
	pass


def draw_frontline(x, y, ax, line_style="-", line_color='k', line_width=1, line_alpha=1,
					marker_shape="polygon", marker_num_sides=3, marker_angle=0,
					marker_size=12, marker_interval=24, marker_offset=0,
					marker_face_color='k', marker_edge_color='k', marker_edge_width=1,
					marker_aspect_ratio=1., marker_alternate_sides=False,
					marker_theta1=0, marker_theta2=180, marker_arrow_shape="full",
					marker_arrow_overhang=0, marker_arrow_length_includes_head=False,
					marker_arrow_head_starts_at_zero=False,
					marker_alpha=1, zorder=None, **kwargs):
	"""
	Draw a "frontline" in matplotlib,
	this is a line decorated with a pattern that is repeated at regular
	distances (independent of location of points making up the line),
	and keeping the same orientation with respect to that line.
	Examples are faults on geological maps, weather fronts, topographic
	highs and lows, etc.

	The easiest way to accomplish this is using markers or patches.
	However, the drawback of this solution is that the aspect ratio of
	the matplotlib axes should not be changed after the frontline is
	drawn. Doing so modifies the line curvature, resulting in a mismatch
	with the angles at which the markers have been drawn previously.
	Simple translation does not have this problem.

	:param x:
		array-like, X coordinates of points defining the line.
	:param y:
		array-like, Y coordinates of points defining the line.
	:param axes:
		axes instance in which frontline should be drawn.
	:param line_style:
		matplotlib linestyle definition.
		(default: "-")
	:param line_color:
		matplotlib color definition for line.
		(default: 'k')
	:param line_width:
		matplotlib line width in points.
		(default: 1)
	:param line_alpha:
		float, alpha transparency for line.
		(default: 1)
	:param marker_shape:
		str, style of front marker,
		one of ("polygon", "star", "asterisk", "circle", "arc",
		"arrow", "ellipse", "rectangle").
		Polygons, stars, asterisks and circles are implemented as
		matplotlib markers; arcs, arrows, ellipses and rectangles as
		matplotlib patches.
		marker_shape may also be a matplotlib patch instance, in that
		case, it is recommended to set lower left coordinate at (0, 0).
		(default: "polygon")
	:param marker_num_sides:
		int, number of sides of front marker. Only applies to polygons, stars,
		and asterisks.
		(default: 3)
	:param marker_angle:
		float, angle in degrees of front marker with respect to line.
		Does not apply to circles.
		(default: 0)
	:param marker_size:
		int, size of front marker in points.
		(default: 12)
	:param marker_interval:
		int, str or array-like, interval of front marker along line.
		- positive int: interval between markers in points
		- negative int (or zero): number of markers along line
		- str: marker interval will be rounded to closest value that
			results in even spacing along the line
		- array-like: distances along line, in range [0,1].
		(default: 24)
	:param marker_offset:
		int, offset of front marker with respect to line.
		(default: 0)
	:param marker_face_color:
		matplotlib color definition for fill color of front marker.
		(default: 'k')
	:param marker_edge_color:
		matplotlib color definition for line color of front marker.
		(default: 'k')
	:param marker_edge_width:
		int, line width of front marker in points.
		(default: 1)
	:param marker_aspect_ratio:
		float, aspect ratio of width (direction perpendicular to line)
		to length (direction along line) of front marker. Only applies
		to arcs, arrows, ellipses and rectangles.
		(default: 1.)
	:param marker_alternate_sides:
		bool, whether or not front markers should alternate between
		two sides of line.
		(default: False)
	:param marker_theta1:
		float, starting angle in degrees. Only applies to arcs.
		(default: 0)
	:param marker_theta2:
		float, ending angle in degrees. Only applies to arcs.
		(default: 180)
	:param marker_arrow_shape:
		str, arrow shape, one of ["full", "left", "right"].
		Only applies to arrows.
		(default: "full")
	:param marker_arrow_overhang:
		float, fraction that the arrow is swept back (0 means triangular shape).
		Can be negative or greater than one. Only applies to arrows.
		(default: 0.)
	:param marker_arrow_length_includes_head:
		bool, True if head is to be counted in calculating arrow length.
		Only applies to arrows.
		(default: False)
	:param marker_arrow_head_starts_at_zero:
		bool, if True, arrow head starts being drawn at coordinate 0 instead of
		ending at coordinate 0. Only applies to arrows.
		(default: False)
	:param marker_alpha:
		float, alpha transparency for front marker.
		(default: 1)
	:param zorder:
		int, sets the zorder for both the line and the front markers.
		(default: None)
	:param kwargs:
		remaining keyword arguments for matplotlib plot command

	:return:
		instance of :class:`FrontlineLegendHandler`, which can be passed
		(in handler_map dictionary) to matplotlib legend function
	"""
	dpi = ax.get_figure().dpi

	#legend_artist = None
	legend_handler = None

	def pt2pixel(val):
		#return val * (dpi / 72.)
		## Correct for a slight mismatch with dash lengths
		return val * (dpi / 72.) * 1.004

	## Plot line first
	if not line_style in ("None", None):
		ax.plot(x, y, lw=line_width, color=line_color, ls=line_style, alpha=line_alpha, zorder=zorder, **kwargs)

	## Transforms between data domain and display domain
	pt_to_pixel_transform = ax.get_figure().dpi_scale_trans.frozen().scale(1./72)
	forward_transform = ax.transData
	inverse_transform = ax.transData.inverted()

	## Compute cumulative distance along line and angles in pixel domain
	display_data_coords = forward_transform.transform(zip(x,y))
	display_data_x, display_data_y = zip(*display_data_coords)
	display_data_angles = np.arctan2(np.diff(display_data_y), np.diff(display_data_x))
	display_distance = mlab.distances_along_curve(display_data_coords)
	display_cum_distance = np.concatenate([[0.], np.cumsum(display_distance)])

	if marker_shape == "asterisk" and marker_num_sides <= 2:
		marker_length = 0
	else:
		marker_length = marker_size
	## Make sure marker_offset is 2D (along line / perpendicular to line)
	if isinstance(marker_offset, (int, float)):
		marker_offset = np.array([0, marker_offset])
	else:
		marker_offset = np.asarray(marker_offset[:2])

	## Convert points to pixels (1 pt = 1/72 inch)
	marker_length_px = pt2pixel(marker_length)
	marker_size_px = pt2pixel(marker_size)
	marker_offset_px = pt2pixel(marker_offset)

	## Compute marker coordinates in data units based on
	## interpolation of cumulative distance along line in display units
	start_distance = marker_length_px/2. + marker_offset_px[0]
	end_distance = display_cum_distance[-1] - marker_length_px/2
	if isinstance(marker_interval, (list, np.ndarray)):
		marker_interval_px = pt2pixel(np.asarray(marker_interval))
		display_marker_distances = np.interp(marker_interval_px, [0.,1.], [start_distance, end_distance])
	elif isinstance(marker_interval, str):
		marker_interval_px = pt2pixel(float(marker_interval))
		num_markers = np.abs(np.round((end_distance - start_distance) / marker_interval_px)) + 1
		display_marker_distances = np.linspace(start_distance, end_distance, num_markers)
	elif marker_interval > 0:
		marker_interval_px = pt2pixel(marker_interval)
		display_marker_distances = np.arange(start_distance, end_distance, marker_interval_px)
	elif marker_interval <= 0:
		display_marker_distances = np.linspace(start_distance, end_distance, np.abs(marker_interval))
	display_marker_x = np.interp(display_marker_distances, display_cum_distance, display_data_x)
	display_marker_y = np.interp(display_marker_distances, display_cum_distance, display_data_y)
	display_marker_angles = np.interp(display_marker_distances, display_cum_distance[1:], display_data_angles)
	if marker_alternate_sides:
		display_marker_angles[1::2] += np.pi
	display_marker_x += (marker_offset_px[1] * np.cos(display_marker_angles + np.pi/2))
	display_marker_y += (marker_offset_px[1] * np.sin(display_marker_angles + np.pi/2))
	marker_coords = inverse_transform.transform(zip(display_marker_x, display_marker_y))


	## Regular markers
	if marker_shape in ["polygon", "star", "asterisk", "circle"]:
		marker_shape_code = {"polygon": 0, "star": 1, "asterisk": 2, "circle": 3}[marker_shape]
		if marker_num_sides == 0:
			marker_shape_code = 3
		if marker_shape_code in (0,1,3):
			## Convert marker size in diamter to size in area
			# TODO: find correct conversion for different shapes
			radius = marker_size / 2
			marker_size = radius * (radius ** 2) / (marker_size)
		for i, (marker_x, marker_y) in enumerate(marker_coords):
			angle = np.degrees(display_marker_angles[i]) + marker_angle
			marker = (marker_num_sides, marker_shape_code, angle)
			ax.plot(marker_x, marker_y, linestyle='None', marker=marker, markersize=marker_size, mec=marker_edge_color, mfc=marker_face_color, mew=marker_edge_width, alpha=marker_alpha, zorder=zorder)

		def legend_artist(self, legend, orig_handle, fontsize, handlebox):
			## Note: In matplotlib versions 1.3.X and maybe also 1.4.X,
			## the 'self' property needs to be removed...
			# TODO: marker_alternate_sides!
			marker = (marker_num_sides, marker_shape_code, marker_angle)
			x0, y0 = handlebox.xdescent, handlebox.ydescent
			width, height = handlebox.width, handlebox.height

			x = np.array([x0, x0+width])
			y = np.ones_like(x) * (y0 + height / 2. - marker_size / 4.)
			line1 = mpl.lines.Line2D(x, y, lw=line_width, color=line_color, ls=line_style, alpha=line_alpha)
			x = np.arange(x0, x0+width, marker_interval_px)
			y = np.ones_like(x) * (y0 + height / 2. - marker_size / 4.)
			line2 = mpl.lines.Line2D(x, y, linestyle='None', marker=marker, markersize=marker_size, mec=marker_edge_color, mfc=marker_face_color, mew=marker_edge_width, alpha=marker_alpha)

			handlebox.add_artist(line1)
			handlebox.add_artist(line2)
			return (line1, line2)

		if mpl.__version__ <= "1.3.1":
			legend_handler = legend_artist
		else:
			#legend_handler = type('FrontlineLegendHandler',  (), {'legend_artist': classmethod(legend_artist)})()
			legend_handler = FrontlineLegendHandler()
			legend_handler.legend_artist = MethodType(legend_artist, legend_handler, FrontlineLegendHandler)

	## Patches
	elif marker_shape in ["arc", "arrow", "ellipse", "rectangle"] or isinstance(marker_shape, mpl.patches.Patch):
		for i in range(len(display_marker_x)):
			dmx, dmy = display_marker_x[i], display_marker_y[i]
			angle = np.degrees(display_marker_angles[i]) + marker_angle
			if marker_shape == "arc":
				patch = mpl.patches.Arc((0, 0), marker_size_px, marker_size_px * marker_aspect_ratio, theta1=marker_theta1, theta2=marker_theta2, angle=angle)
			elif marker_shape == "arrow":
				dx = np.cos(np.radians(angle)) * marker_length_px / 2
				dy = np.sin(np.radians(angle)) * marker_length_px / 2
				patch = mpl.patches.FancyArrow(0, 0, dx, dy, width=marker_edge_width, head_width=marker_size_px/2*marker_aspect_ratio, head_length=marker_size_px/2, shape=marker_arrow_shape, overhang=marker_arrow_overhang, length_includes_head=marker_arrow_length_includes_head, head_starts_at_zero=marker_arrow_head_starts_at_zero)
			elif marker_shape == "ellipse":
				patch = mpl.patches.Ellipse((0, 0), marker_size_px, marker_size_px * marker_aspect_ratio, angle=angle)
			elif marker_shape == "rectangle":
				patch = mpl.patches.Rectangle((0, 0), marker_size_px, marker_size_px * marker_aspect_ratio, angle=angle)
			elif isinstance(marker_shape, mpl.patches.Patch):
				patch = marker_shape
				tf = pt_to_pixel_transform + mpl.transforms.Affine2D().rotate_deg(angle)
				patch.set_transform(tf)
			## Shift patch back half its width if needed
			if marker_shape in ("arrow", "rectangle") or isinstance(marker_shape, mpl.patches.Patch):
				dmx += (-np.cos(np.radians(angle)) * marker_length_px / 2)
				dmy += (-np.sin(np.radians(angle)) * marker_length_px / 2)
			tf = mpl.transforms.Affine2D().translate(dmx, dmy)

			## Copy tranformed vertices to a new patch, otherwise patches
			## do not move with curve if plot is translated
			path = patch.get_path()
			path = path.cleaned(transform=(patch.get_transform() + tf + inverse_transform))
			vertices, codes = path.vertices, path.codes
			if marker_shape == "arc":
				## Modify code to make filling of arc patches possible
				codes = np.concatenate([codes[:-1], [mpl.path.Path.CLOSEPOLY]])

			# Note: the following lines work too, but in the case of arcs,
			# some points seem to disappear
			#patch.set_transform(tf + inverse_transform)
			#vertices = patch.get_verts()
			#codes = [mpl.path.Path.MOVETO] + [mpl.path.Path.LINETO] * (len(vertices) - 2) + [mpl.path.Path.CLOSEPOLY]

			## Copy patch and apply color and linewidth options
			path = mpl.path.Path(vertices, codes)
			patch = mpl.patches.PathPatch(path, ec=marker_edge_color, fc=marker_face_color, lw=marker_edge_width, alpha=marker_alpha)
			patch.set_zorder(zorder)
			ax.add_patch(patch)

		# TODO: custom legend handler for patches

	return legend_handler



if __name__ == "__main__":
	import pylab

	## Line data
	x = np.linspace(0, 2*np.pi, 100)
	y = np.sin(x)

	## Marker definition
	for example in ["polygon", "rectangle", "asterisk", "arrow1", "arrow2", "arc", "circle", "star", "patch"]:
		## Defaults
		marker_shape = "polygon"
		marker_num_sides = 4
		marker_size = 20
		marker_offset = 0
		marker_interval = 40
		marker_angle = 0
		marker_aspect_ratio = 1
		marker_edge_color = 'k'
		marker_face_color = 'r'
		marker_edge_width = 1
		marker_alpha = 0.5
		marker_theta1 = 0
		marker_theta2 = 180
		marker_arrow_shape = "full"
		marker_arrow_overhang = 0
		marker_arrow_head_starts_at_zero = False
		marker_arrow_length_includes_head = False
		marker_alternate_sides = False

		## Line style
		line_style = "-"
		line_color = 'k'
		line_width = 2
		line_alpha = 1
		kwargs = {}

		if example == "polygon":
			marker_shape = "polygon"
			marker_num_sides = 3
			marker_angle = 0
			marker_size = 15
			marker_offset = (marker_size / 2)
			kwargs["dashes"] = [marker_size, marker_interval-marker_size]
			title = "Thrust fault"

		elif example == "rectangle":
			marker_shape = "rectangle"
			marker_size = 15
			marker_aspect_ratio = 1
			title = "Rectangle"

		elif example == "asterisk":
			marker_shape = "asterisk"
			marker_num_sides = 1
			marker_interval = '40'
			marker_edge_width = line_width
			title = "Normal fault, marker interval rounded to align with line length"

		elif example == "arrow1":
			marker_shape = "arrow"
			marker_arrow_shape = "right"
			marker_offset = marker_size / 2
			marker_interval = [0.,0.,0.5,0.5,1.0,1.0]
			marker_alternate_sides = True
			title = "Right-lateral strike-slip fault"

		elif example == "arrow2":
			marker_shape = "arrow"
			marker_angle = 180
			marker_arrow_shape = "left"
			marker_offset = marker_size / 2
			marker_interval = [0.,0.,0.5,0.5,1.0,1.0]
			marker_alternate_sides = True
			title = "Left-lateral strike-slip fault"

		elif example == "arc":
			marker_shape = "arc"
			marker_interval = -20
			marker_alternate_sides = True
			marker_face_color = marker_edge_color = line_color = 'b'
			title = "Arc, fixed number of markers, alternating sides"

		elif example == "circle":
			marker_shape = "circle"
			marker_size = 15
			marker_edge_color = line_color = 'g'
			marker_edge_width = line_width
			marker_face_color = 'w'
			marker_interval = np.linspace(0,1,11)
			title = "Circle, marker interval array"

		elif example == "star":
			marker_shape = "star"
			marker_num_sides = 6
			marker_size = 10
			title = "Star"

		elif example == "patch":
			marker_shape = mpl.patches.Polygon([[0,0], [0,marker_size], [marker_size/2,marker_size/2], [marker_size, marker_size], [marker_size,0]], closed=True)
			marker_offset = [marker_size/4, 0]
			kwargs["dashes"] = [marker_size/2,marker_size/2]
			title = "Arbitrary patch, aligned with dashes"


		## Initiate figure
		fig = pylab.figure()
		ax = fig.add_subplot(111)
		pylab.axis((-1, 7, -1.1, 1.1))

		zorder = 1
		draw_frontline(x, y, ax, line_color=line_color, line_width=line_width,
					line_alpha=line_alpha, marker_shape=marker_shape,
					marker_num_sides=marker_num_sides, marker_angle=marker_angle,
					marker_size=marker_size, marker_interval=marker_interval,
					marker_offset=marker_offset, marker_edge_color=marker_edge_color,
					marker_face_color=marker_face_color, marker_edge_width=marker_edge_width,
					marker_aspect_ratio=marker_aspect_ratio, marker_alternate_sides=marker_alternate_sides,
					marker_alpha=marker_alpha, marker_theta1=marker_theta1, marker_theta2=marker_theta2,
					marker_arrow_shape=marker_arrow_shape, marker_arrow_overhang=marker_arrow_overhang,
					marker_arrow_head_starts_at_zero=marker_arrow_head_starts_at_zero,
					marker_arrow_length_includes_head=marker_arrow_length_includes_head,
					zorder=zorder, **kwargs)


		## Changing plot limits screws marker angles up!
		#xmin, xmax, ymin, ymax =  pylab.axis()
		#pylab.axis((xmin-5, xmax+5, ymin, ymax))
		pylab.title(title)
		pylab.show()
