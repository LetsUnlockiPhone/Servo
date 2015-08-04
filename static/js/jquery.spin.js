/*

You can now create a spinner using any of the variants below:

$("#el").spin(); // Produces default Spinner using the text color of #el.
$("#el").spin("small"); // Produces a 'small' Spinner using the text color of #el.
$("#el").spin("large", "white"); // Produces a 'large' Spinner in white (or any valid CSS color).
$("#el").spin({ ... }); // Produces a Spinner using your custom settings.

$("#el").spin(false); // Kills the spinner.

*/

(function($) {
	$.fn.spin = function(opts, color) {
		var presets = {
			"tiny": { lines: 9, length: 2, width: 2, radius: 4, trail: 70, speed: 1 },
			"small": { lines: 8, length: 4, width: 3, radius: 5 },
			"large": { lines: 10, length: 8, width: 4, radius: 8 }
		};

        var overlay = $('<div class="overlay" style="position: absolute; background: rgba(0,0,0,0.7); z-index: 10000;"></div>');

		if (Spinner) {
			return this.each(function() {
				var $this = $(this),
					data = $this.data();

				if (data.spinner) {
					data.spinner.stop();
					delete data.spinner;
				}
				if (opts !== false) {
					if (typeof opts === "string") {
						if (opts in presets) {
							opts = presets[opts];
						} else {
							opts = presets['tiny'];
						}
						if (color) {
							opts.color = color;
						}
					}
					else {
						opts = presets['tiny'];
					}

                    overlay.css({

                        width: $this.innerWidth(),
                        height: $this.innerHeight(),
                        left: 0,
                        top: 0
                    });

                    overlay.appendTo(this);

                    opts = {
                        lines: 13, // The number of lines to draw
                        length: 20, // The length of each line
                        width: 10, // The line thickness
                        radius: 30, // The radius of the inner circle
                        corners: 1, // Corner roundness (0..1)
                        rotate: 0, // The rotation offset
                        direction: 1, // 1: clockwise, -1: counterclockwise
                        color: '#fff', // #rgb or #rrggbb
                        speed: 1, // Rounds per second
                        trail: 60, // Afterglow percentage
                        shadow: false, // Whether to render a shadow
                        hwaccel: false, // Whether to use hardware acceleration
                        className: 'spinner', // The CSS class to assign to the spinner
                        zIndex: 2e9, // The z-index (defaults to 2000000000)
                        top: 'auto', // Top position relative to parent in px
                        left: 'auto' // Left position relative to parent in px
                    };

                    data.spinner = new Spinner($.extend({color: $this.css('color')}, opts)).spin(this);
				}
                else{

                    $this.find('.overlay').remove();
                }

			});
		} else {
			throw "Spinner class not available.";
		}
	};
})(jQuery);