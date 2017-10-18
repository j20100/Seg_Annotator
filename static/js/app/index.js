/** Index page renderer.
 */
define(["../helper/pagination",
        "../helper/segment-viewer",
        "../helper/util"],
function(Pagination, Viewer, util) {
  function createLabelOptions(params, labels) {
    var container = document.createElement("div"),
        select = document.createElement("select"),
        option;
    {
      option = document.createElement("option");
      option.appendChild(document.createTextNode("all"));
      select.appendChild(option);
    }
    for (var i = 0; i < labels.length; ++i) {
      option = document.createElement("option");
      option.appendChild(document.createTextNode(labels[i]));
      if (labels[i] === params.label) {
        option.selected = true;
      }
      select.appendChild(option);
    }
    select.onchange = function(event) {
      window.location = util.makeQueryParams(params, {
        label: (event.target.value === "all") ? null : event.target.value
      });
    };
    container.className = "edit-top-menu-id";
    container.appendChild(select);
    return container;
  }

  function wait(ms){
     var start = new Date().getTime();
     var end = start;
     while(end < start + ms) {
       end = new Date().getTime();
    }
  }

  function load_annot(annotationURL) {
    var fileURL = new FormData();
    var request = new XMLHttpRequest();
    var x = 0;
    var newURL = 'no image';
    fileURL.append("URL", annotationURL)
    request.open("POST", "https://remote.ivisolutions.ca:5000/updater", false);
    request.send(fileURL)
    if(request.status === 200) {
        newURL = request.responseText;
        if (newURL != 'no image'){
          x = 1;
          return newURL;
        }
    };
  }

  function render(data, params) {
    var container = document.createElement("div"),
    pagination = new Pagination(data.imageURLs.length, params);
    document.body.appendChild(pagination.render());
    document.body.appendChild(createLabelOptions(params, data.labels));
    var annotURL = "none";

    for (var i = pagination.begin(); i < pagination.end(); ++i) {

      annotURL = load_annot(data.annotationURLs[i])

      //while (annotURL == undefined)
    //    annotURL = load_annot(data.annotationURLs[i])
    //    wait(100);

      var viewer = new Viewer(data.imageURLs[i], annotURL, {
                                width: (params.width || 480),
                                height: (params.height || 320),
                                colormap: data.colormap,
                                labels: data.labels,
                                excludedLegends: [0],
                                overlay: i.toString()
                              }),
          anchor = document.createElement("a");
      anchor.appendChild(viewer.container);
      anchor.href = util.makeQueryParams({ view: "edit", id: i });
      container.className = "edit-top-menu-block";
      container.appendChild(anchor);
      document.body.appendChild(container);

    }
  }

  return render;
});
