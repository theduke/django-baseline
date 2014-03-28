
(function($) {

	/*
	 * For really old browsers, add a stub log function to prevent exceptions
	 * when logging.
	 */
	if (!('console' in window)) {
		window.console = {
			log: function() {

			}
		}
	}

	window.baseline = {};

	/**
	 * Pretty print an amount of seconds as x years, x months,
	 * days, hours, seconds.
	 *
	 * Use granularity to limit shown values:
	 * Options: sec, min, hour, day, mon, year
	 *
	 * Set html to true for html rendered output.
	 */
	window.baseline.prettyPrintTime = function(seconds, granularity, html) {
		if (!granularity) {
			granularity = 'sec';
		}

		map = {
			year: 1,
			mon: 2,
			day: 3,
			hour: 4,
			min: 5,
			sec: 6
		};

		granularity = map[granularity];

		parts = []

		var minute = 60;
		var hour = minute * 60;
		var day = hour * 24;
		var month = day * 30;
		var year = day * 365;

		var years = Math.floor(seconds / year);
		seconds = seconds % year;

		var months = Math.floor(seconds / month);
		seconds = seconds % month;

		var days = Math.floor(seconds / day);
		seconds = seconds % day;

		var hours = Math.floor(seconds / hour);
		seconds = seconds % hour;

		var minutes = Math.floor(seconds / minute);
		seconds = seconds % minute;

		if (years) {
			parts.push([years, years > 1 ? 'years' : 'year']);
		}
		if (granularity > 1 && (months || years)) {
			parts.push([months, months > 1 ? 'months' : 'month']);
		}
		if (granularity > 2 && (days || months || years)) {
			parts.push([days, days > 1 ? 'days' : 'day']);
		}
		if (granularity > 3 && (hours || days || months || years)) {
			parts.push([hours, hours > 1 ? 'hours' : 'hour']);
		}
		if (granularity > 4 && (minutes || hours || days || months || years)) {
			parts.push([minutes, minutes > 1 ? 'minutes' : 'minute']);
		}

		if (granularity > 5) {
			parts.push([seconds, seconds > 1 ? 'seconds' : 'second']);
		}

		var output = parts;
		if (html) {
			output = '<div class="datetime">';
			for (var key in parts) {
				output += '<div class="part">'
					+ '<div class="number">' + parts[key][0] + '</div>'
					+ '<div class="unit">' + parts[key][1] + '</div>'
					+ '</div>';
			}
			output += '</div>';
		}

		return output;
	};

})(jQuery);
