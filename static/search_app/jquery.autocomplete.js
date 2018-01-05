var options = {

  url: function(phrase) {
    return "/proxy_stations?term=" + phrase;
  },

  getValue: function(element) {
    return element.title;
  },

  ajaxSettings: {
    method: "GET",
    data: {
      dataType: "json"
    }
  },

  requestDelay: 400
};

$("#id_station_from").easyAutocomplete(options);
$("#id_station_till").easyAutocomplete(options);
