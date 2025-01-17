#query che ritorna tutti i punti GPS del tragitto
get_points_query = '''SELECT distinct * 
					  FROM tragitto
					  ORDER BY time;'''

delete_tragittof_query = ''' DELETE FROM tragitto_filtered'''

insert_points_query = '''INSERT INTO tragitto_filtered (id, geom, track_fid, track_seg_id, track_seg_point_id, ele, time) VALUES (%s,%s,%s,%s,%s,%s,%s)'''

#query che calcola la distanza tra due punti
distance_query = '''SELECT st_distance(p1.geom::geography, p2.geom::geography)
					FROM tragitto as p1, tragitto as p2
					WHERE p1.id = %s AND p2.id = %s'''

#filtra prendendo un punto ogni t secondi minimo
def time_filter(connection, t):
	print('-'*100)
	print("FILTERING:")
	print("filtering by time...")
	cursor = connection.cursor()
	cursor.execute(get_points_query)
	points = cursor.fetchall()
	points_filtered = []
	cursor.execute(delete_tragittof_query)
	connection.commit()

	dt = 0
	for i, p in enumerate(points[:-1]):
		dt = dt + (points[i+1][6] - points[i][6]).total_seconds()
		if dt >= t:
			points_filtered.append(p)
			dt = dt - t

	if dt >= t: #l'ultimo punto
		points_filtered.append(points[-1])

	print("number of points after filter: {}".format(len(points_filtered)))

	for e in points_filtered:
		data = (e[0], e[1], e[2], e[3], e[4], e[5], e[6], )
		cursor.execute(insert_points_query, data)
	connection.commit()


#filtra prendendo un punto ogni t metri minimo
def distance_filter(connection, t):
	print('-'*100)
	print("FILTERING:")
	print("filtering by distance...")
	cursor = connection.cursor()
	cursor.execute(get_points_query)
	points = cursor.fetchall()
	points_filtered = []
	cursor.execute(delete_tragittof_query)
	connection.commit()

	ds = 0
	for i, p in enumerate(points[:-1]):
		data = (points[i][0], points[i+1][0], )
		cursor.execute(distance_query, data)
		for row in cursor.fetchall():
			ds = ds + row[0]
		if ds >= t:
			points_filtered.append(p)
			ds = ds - t
	if ds >= t: #l'ultimo punto
		points_filtered.append(points[-1])

	print("number of points after filter: {}".format(len(points_filtered)))

	for e in points_filtered:
		data = (e[0], e[1], e[2], e[3], e[4], e[5], e[6], )
		cursor.execute(insert_points_query, data)
	connection.commit()