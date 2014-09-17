"""
Test to plot frontlines in matplotlib using markers
"""

import numpy as np
import matplotlib as mpl
import matplotlib.mlab as mlab



def draw_frontline(x, y, ax, line_style="-", line_color='k', line_width=1, line_alpha=1,
					marker_style="polygon", marker_num_sides=3, marker_angle=0,
					marker_size=12, marker_interval=24, marker_offset=0,
					marker_face_color='k', marker_edge_color='k', marker_edge_width=1,
					marker_aspect_ratio=1., marker_alternate_sides=False,
					marker_theta1=0, marker_theta2=180,
					marker_alpha=1, zorder=None):
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
		array-like, Y coordinates of points defining hte line.
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
	:param marker_style:
		str, style of front marker,
		one of ("polygon", "star", "asterisk", "circle", "arc",
		"arrow", "ellipse", "rectangle").
		Polygons, stars, asterisks and circles are implemented as
		matplotlib markers; arcs, arrows, ellipses and rectangles as
		matplotlib patches.
		marker_style may also be a matplotlib patch instance, but
		in that case, it will not be rotated following line curvature.
		(default: "polygon")
	:param marker_num_sides:
		int, number of sides of front marker. Only applies to polygons, stars,
		and asterisks.
		(default: 3)
	:param marker_angle:
		float, angle in degrees of front marker with respect to line.
		(default: 0)
	:param marker_size:
		int, size of front marker in points.
		(default: 12)
	:param marker_interval:
		int or array-like, interval of front marker along line
		positive int: interval between markers in points
		negative int (or zero): number of markers along line
		array-like: distances along line, in range [0,1].
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
	:param marker_alpha:
		float, alpha transparency for front marker.
		(default: 1)
	:param zorder:
		int, sets the zorder for both the line and the front markers.
		(default: None)
	"""
	#TODO: add more (fancy) arrow properties

	## Plot line first
	ax.plot(x, y, lw=line_width, color=line_color, ls=line_style, alpha=line_alpha, zorder=zorder)

	## Transforms between data domain and display domain
	forward_transform = ax.transData
	inverse_transform = ax.transData.inverted()

	## Compute marker coordinates in data units
	## based on cumulative distance along line in display units
	display_data_coords = forward_transform.transform(zip(x,y))
	display_data_x, display_data_y = zip(*display_data_coords)
	display_data_angles = np.arctan2(np.diff(display_data_y), np.diff(display_data_x))
	display_distance = mlab.distances_along_curve(display_data_coords)
	display_cum_distance = np.concatenate([[0.], np.cumsum(display_distance)])
	start_distance = marker_size/2.
	end_distance = display_cum_distance[-1] - marker_size/2+1
	if isinstance(marker_interval, (list, np.ndarray)):
		display_marker_distances = np.interp(marker_interval, [0.,1.], [start_distance, end_distance])
	elif marker_interval > 0:
		display_marker_distances = np.arange(start_distance, end_distance, marker_interval)
	elif marker_interval <= 0:
		display_marker_distances = np.linspace(start_distance, end_distance, np.abs(marker_interval))
	display_marker_x = np.interp(display_marker_distances, display_cum_distance, display_data_x)
	display_marker_y = np.interp(display_marker_distances, display_cum_distance, display_data_y)
	display_marker_angles = np.interp(display_marker_distances, display_cum_distance[1:], display_data_angles)
	if marker_alternate_sides:
		display_marker_angles[1::2] += np.pi
	display_marker_x += (marker_offset * np.cos(display_marker_angles + np.pi/2))
	display_marker_y += (marker_offset * np.sin(display_marker_angles + np.pi/2))
	marker_coords = inverse_transform.transform(zip(display_marker_x, display_marker_y))


	## Regular markers
	if marker_style in ["polygon", "star", "asterisk", "circle"]:
		marker_style_code = {"polygon": 0, "star": 1, "asterisk": 2, "circle": 3}[marker_style]
		if marker_num_sides == 0:
			marker_style_code = 3
		for i, (marker_x, marker_y) in enumerate(marker_coords):
			angle = np.degrees(display_marker_angles[i]) + marker_angle
			marker = (marker_num_sides, marker_style_code, angle)
			ax.plot(marker_x, marker_y, linestyle='None', marker=marker, markersize=marker_size, mec=marker_edge_color, mfc=marker_face_color, mew=marker_edge_width, alpha=marker_alpha, zorder=zorder)


	## Patches
	elif marker_style in ["arc", "arrow", "ellipse", "rectangle"] or isinstance(marker_style, mpl.patches.Patch):
		for i in range(len(display_marker_x)):
			dmx, dmy = display_marker_x[i], display_marker_y[i]
			angle = np.degrees(display_marker_angles[i]) + marker_angle
			if marker_style == "arc":
				patch = mpl.patches.Arc((0, 0), marker_size, marker_size * marker_aspect_ratio, theta1=marker_theta1, theta2=marker_theta2, angle=angle)
			elif marker_style == "arrow":
				dx = np.cos(display_marker_angles[i]) * marker_size / 2
				dy = np.sin(display_marker_angles[i]) * marker_size / 2
				patch = mpl.patches.FancyArrow(0, 0, dx, dy, width=marker_edge_width, length_includes_head=False, head_width=marker_size/2*marker_aspect_ratio, head_length=marker_size/2, shape=u'right', overhang=0, head_starts_at_zero=False)
				#patch = mpl.patches.Arrow(0, 0, dx, dy)
			elif marker_style == "ellipse":
				patch = mpl.patches.Ellipse((0, 0), marker_size, marker_size * marker_aspect_ratio, angle=angle)
			elif marker_style == "rectangle":
				patch = mpl.patches.Rectangle((0, 0), marker_size, marker_size * marker_aspect_ratio, angle=angle)
			elif isinstance(marker_style, mpl.patches.Patch):
				patch = marker_style
			## Shift patch back half its width if needed
			if marker_style in ("arrow", "rectangle"):
				dmx += (-np.cos(display_marker_angles[i]) * marker_size / 2)
				dmy += (-np.sin(display_marker_angles[i]) * marker_size / 2)
			tf = mpl.transforms.Affine2D().translate(dmx, dmy)
			#patch.set_transform(tf)
			## Copy tranformed vertices to a new patch, otherwise patches
			## do not move with curve if plot is translated
			## As a bonus, arc patches can be filled
			path = patch.get_path().cleaned(transform=(patch.get_transform() + tf + inverse_transform))
			vertices, codes = path.vertices, path.codes
			if marker_style == "arc":
				codes = np.concatenate([codes[:-1], [mpl.path.Path.CLOSEPOLY]])

			# Note: the following lines work too, but in the case of arcs,
			# some points seem to disappear
			#patch.set_transform(tf + inverse_transform)
			#vertices = patch.get_verts()
			#codes = [mpl.path.Path.MOVETO] + [mpl.path.Path.LINETO] * (len(vertices) - 2) + [mpl.path.Path.CLOSEPOLY]
			path = mpl.path.Path(vertices, codes)
			patch = mpl.patches.PathPatch(path, ec=marker_edge_color, fc=marker_face_color, lw=marker_edge_width, alpha=marker_alpha)
			patch.set_zorder(zorder)
			ax.add_patch(patch)



if __name__ == "__main__":
	import pylab

	## Line data
	x = np.linspace(0, 2*np.pi, 100)
	y = np.sin(x)

	## Marker definition
	marker_style = "asterisk"
	#marker_style = mpl.patches.Polygon([[0,0], [10,0], [10,10], [0,10]], closed=True)
	marker_num_sides = 2
	marker_angle = 0
	marker_size = 5
	marker_edge_color = 'k'
	marker_face_color = 'r'
	marker_edge_width = 1
	marker_alpha = 0.75
	marker_offset = (marker_size / 2) - marker_edge_width / 2
	#marker_offset = 0
	#marker_interval = 40
	#marker_interval = -20
	#marker_interval = [0., 0.5, 1.]
	marker_interval = np.linspace(0,1,11)
	marker_aspect_ratio = 0.75
	marker_theta1 = 0
	marker_theta2 = 180
	marker_alternate_sides = False

	## Line style
	line_style = "-"
	line_color = 'k'
	line_width = 2
	line_alpha = 1

	## Initiate figure
	## We need to plot line first to obtain transforms
	## Note that, once the transforms are obtained, the figure scale
	## must not be changed anymore, otherwise the marker angles will be wrong
	## Simple translation is still allowed, however
	fig = pylab.figure()
	ax = fig.add_subplot(111)
	pylab.axis((-1, 7, -1.1, 1.1))

	zorder = 1
	draw_frontline(x, y, ax, line_color=line_color, line_width=line_width,
				line_alpha=line_alpha, marker_style=marker_style,
				marker_num_sides=marker_num_sides, marker_angle=marker_angle,
					marker_size=marker_size, marker_interval=marker_interval,
					marker_offset=marker_offset, marker_edge_color=marker_edge_color,
					marker_face_color=marker_face_color, marker_edge_width=marker_edge_width,
					marker_aspect_ratio=marker_aspect_ratio, marker_alternate_sides=marker_alternate_sides,
					marker_alpha=marker_alpha, marker_theta1=marker_theta1, marker_theta2=marker_theta2,
					zorder=zorder)


	## Changing plot limits screws marker angles up!
	#xmin, xmax, ymin, ymax =  pylab.axis()
	#pylab.axis((xmin-5, xmax+5, ymin, ymax))
	pylab.show()
