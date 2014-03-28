(function($) {

    $.fn.serializeObject = function(){
        var data = {};

        rawData = this.serializeArray();
        for (var key in rawData) {
            data[rawData[key]['name']] = rawData[key]['value'];
        }

        return data;
    };

}(jQuery));
