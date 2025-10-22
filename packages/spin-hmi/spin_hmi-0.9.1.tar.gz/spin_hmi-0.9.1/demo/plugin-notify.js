var notify_elements = [];

window.addEventListener("spincustomelement", (event) => {
    if (event.detail.context == "demoplugin") {
        notify_elements.push(event.detail.element);
        event.preventDefault();
    }
})

window.addEventListener("spinreply", (event) => {
    if (event.detail.action == "demoplugin-notify") {
        for (var el of notify_elements) {
            el.textContent = event.detail.data;
        }
    }
});
