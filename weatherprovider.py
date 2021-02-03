class WeatherProvider:

    # Return the cardinal direction based on the wind direction degree
    def cardinal_direction(self, degree):
        dirs = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
        ix = round(degree / (360. / len(dirs)))
        return dirs[ix % len(dirs)]
