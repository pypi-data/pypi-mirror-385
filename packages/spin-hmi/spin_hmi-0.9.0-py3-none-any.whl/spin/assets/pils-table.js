const PILSTABLE_INNER_TEMPLATE = `
  <div>
    <button id="pilstable-{dev}-read"><img src="s/refresh.svg"> (Re)read table</button>
    <span style="padding-left: 2em">Click on a value to change it.</span>
  </div>
  <div style="overflow: scroll; max-height: 80vh; margin: 1em 0">
    <table id="pilstable-{dev}">
      <thead></thead>
      <tbody></tbody>
    </table>
  </div>
`;

var PilsTable = {
    do_read: function(dev) {
        Spin.send_request(dev, "", "read-table", "", "");
    },

    handle_reply: function(event) {
        if (event.detail.action === "pilscell") {
            let {row, col, value} = event.detail.data;
            let cell = $(`#pilstable-${event.detail.key} tbody ` +
                         `tr:nth-child(${row + 1}) td:nth-child(${col + 1})`);
            cell.textContent = value;
            return;
        }
        if (event.detail.action !== "pilstable")
            return;
        let {rows, cols, data} = event.detail.data;
        let tbl = $(`#pilstable-${event.detail.key}`);
        let thead = tbl.querySelector("thead");
        thead.innerHTML = "";
        let tr = document.createElement("tr");
        for (let j = 0; j < cols.length; j++) {
            let th = document.createElement("th");
            th.textContent = cols[j][0];
            tr.appendChild(th);
        }
        thead.appendChild(tr);
        let tbody = tbl.querySelector("tbody");
        tbody.innerHTML = "";
        for (let i = 0; i < rows; i++) {
            let tr = document.createElement("tr");
            for (let j = 0; j < cols.length; j++) {
                let td = document.createElement("td");
                td.textContent = data[i][j];
                // If the column is writable, let the user edit it.
                if (cols[j][1] !== null) {
                    td.style.cursor = "pointer";
                    td.addEventListener("click", function() {
                        Spin.input_show(cols[j][1], (value) => {
                            Spin.send_request(event.detail.key, "", "write-cell", "",
                                              {row: i, col: j, value: value});
                        });
                    });
                }
                tr.appendChild(td);
            }
            tbody.appendChild(tr);
        }
    },

    handle_element: function(event) {
        if (event.detail.context !== "pilstable")
            return;
        let dev = event.detail.key;
        event.detail.element.innerHTML = PILSTABLE_INNER_TEMPLATE.replaceAll("{dev}", dev);
        $(`#pilstable-${dev}-read`).addEventListener("click", this.do_read.bind(this, dev));
        event.preventDefault();
    }
};

window.addEventListener("spincustomelement", PilsTable.handle_element.bind(PilsTable));
window.addEventListener("spinreply", PilsTable.handle_reply.bind(PilsTable));
