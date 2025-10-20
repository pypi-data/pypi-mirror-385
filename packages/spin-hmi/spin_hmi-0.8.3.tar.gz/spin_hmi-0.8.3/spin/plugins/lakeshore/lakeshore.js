const LAKESHORE_INNER_TEMPLATE = `<div>
  <button disabled="disabled" id="{button}">Scan Curves</button>
  <div class="curvescroll">
    <table class="curvetable" id="{table}">
      <thead>
        <tr>
          <th scope="col">Index</th>
          <th scope="col">Name</th>
          <th scope="col">Serial Number</th>
          <th scope="col">Format</th>
          <th scope="col">Limit</th>
          <th scope="col">Coefficient</th>
          <th scope="col">Download</th>
          <th scope="col">Upload</th>
        </tr>
      </thead>
      <tbody>
      </tbody>
    </table>
  </div>
</div>`;

var PluginLakeshore = {
    devices: [],

    clear_curves: function(device) {
        for (let el of document.querySelectorAll(`#curvetable-${device} tbody tr`)) {
            el.remove();
        }
    },

    scan_curves: function(device) {
        Spin.send_request(device, "", "scan", "", "");
    },

    add_curve: function(device, curve) {
        // add table row with button and fileselect for upload, button for download
        // TODO: how to do this in a nicer way?
        let row = document.getElementById(`curvetable-${device}`).tBodies[0].insertRow(-1);
        for (let key of ["idx", "name", "serial", "fmt", "limit", "coeff"]) {
            let cell = row.insertCell(-1);
            cell.appendChild(document.createTextNode(curve[key]));
        }
        let dlbutton = document.createElement("button");
        dlbutton.textContent = "Download";
        dlbutton.addEventListener("click", (ev) => {PluginLakeshore.init_download_curve(device, curve["idx"])});
        row.insertCell(-1).appendChild(dlbutton);

        let ulbutton = document.createElement("button");
        ulbutton.textContent = "Upload";
        ulbutton.addEventListener("click", (ev) => {PluginLakeshore.choose_file(device, curve["idx"])});
        let input = document.createElement("input");
        input.hidden = true;
        input.setAttribute("id", `input-${device}-${curve["idx"]}`);
        input.setAttribute("type", "file");
        let uploadcell = row.insertCell(-1);
        uploadcell.appendChild(input);
        uploadcell.appendChild(ulbutton);
    },

    choose_file: function(device, curve) {
        // TODO: ask for confirmation
        let input = document.getElementById(`input-${device}-${curve}`);

        input.addEventListener("change", this.do_upload.bind(this, device, curve), { once: true });

        input.click();
    },

    do_upload: function(device, curve, event) {
        let file = event.target.files[0];
        Spin.send_file(device, file, {"idx": curve});
    },

    init_download_curve: function(device, curveidx) {
        Spin.send_request(device, "", "download", "", curveidx);
    },

    download_curve: function(name, file) {
        // trigger a download in the client
        var blob = new Blob([file], {type: "text/plain;charset=utf-8"});
        saveAs(blob, `${name}.340`);
    },

    handle_reply: function(event) {
        if (event.detail.action != "plugin-lakeshore") {
            return;
        }
        data = event.detail.data;
        switch (data.reason) {
            case "reset":
                this.clear_curves(event.detail.key);
                break;
            case "curve-found":
                this.add_curve(event.detail.key, data.curve);
                break;
            case "curve-ready":
                this.download_curve(data.curvename, data.file);
                break;
        }
    },

    enable_buttons: function(enabled) {
        for (let key of this.devices) {
            document.getElementById(`curvescanbtn-${key}`).disabled = !enabled;
            for (let el of document.querySelectorAll(`#curvetable-${key} tbody tr button`)) {
                el.disabled = !enabled;
            }
        }
    },

    startup: function() {
        if (this.devices.length == 0) {
            // not configured for the site
            return;
        }
        console.log("set up lakeshore plugin");
        window.addEventListener("spinreply", this.handle_reply.bind(this));
        window.addEventListener("spinconnect", () => this.enable_buttons(true));
        window.addEventListener("spindisconnect", () => this.enable_buttons(false));
    },

    handle_element: function(event) {
        let det = event.detail;
        if (det.context !== "lakeshore") {
            return;
        }
        let el = det.element;
        el.innerHTML = LAKESHORE_INNER_TEMPLATE.replace("{dev}", det.key)
            .replace("{button}", `curvescanbtn-${det.key}`)
            .replace("{table}", `curvetable-${det.key}`);
        document.getElementById(`curvescanbtn-${det.key}`).addEventListener(
            "click", this.scan_curves.bind(this, det.key));
        this.devices.push(det.key);
        event.preventDefault();
    },
};

window.addEventListener("spincustomelement", PluginLakeshore.handle_element.bind(PluginLakeshore));
window.addEventListener("spinstartup", () => { PluginLakeshore.startup() });
