window.utils.countdownbox = {

    init: function() {
        $('.countdownbox').each(function() {
            $this = $(this);
            var counter = $this.find('.counter');

            var endTime = parseInt($this.attr('data-datetime'), 10);
            var granularity = $this.attr('data-granularity');

            var interval = setInterval(function() {
                var timeLeft = Math.floor((new Date(endTime * 1000) - new Date()) / 1000);
                counter.html(baseline.prettyPrintTime(timeLeft, granularity, true));

                if (timeLeft <= 0) {
                    clearInterval(interval);
                }
            }, 1000);
        });
    }

};

window.utils.countdownbox.init();
