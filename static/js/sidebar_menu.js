// Set the behavior of the sidebar menu

$(document).on("click", "#menu-toggle", function(e) {
        e.preventDefault();
        $("#wrapper").toggleClass("toggled");
    });

$(document).on("click", "#menu-toggle-2", function(e) {
    e.preventDefault();
    $("#wrapper").toggleClass("toggled-2");
    $('#menu ul').hide();
});

function initMenu() {
    $('#menu ul').hide();
    $('#menu ul').children('.current').parent().show();
    $('#menu li a').click(function() {
        var checkElement = $(this).next();
        if((checkElement.is('ul')) && (checkElement.is(':visible'))) {
            return false;
        }
        if((checkElement.is('ul')) && (!checkElement.is(':visible'))) {
            $('#menu ul:visible').slideUp('normal');
            checkElement.slideDown('normal');
            return false;
        }
    });

    // To prevent collapsed DataTable from displaying huge scrollbar
    setTimeout(function() {$(window).trigger('resize');}, 1);
}

$(document).ready(function() {initMenu();});

function setHeightSidebar() {
    // Adjust height of sidebar-wrapper
    var menu_height = document.getElementById("menu").offsetHeight;
    var footer_height = document.getElementById("footer").offsetHeight;
    var height = $(window).height();
    height -= document.getElementById("bs-example-navbar-collapse-1").offsetHeight;
    height -= footer_height;
    var content = document.getElementById("page-content-wrapper").offsetHeight;
    document.getElementById("sidebar-wrapper").style.height = Math.max(height, menu_height+footer_height, content) + "px"
}

window.onresize = function(event) {
    setHeightSidebar();
}
