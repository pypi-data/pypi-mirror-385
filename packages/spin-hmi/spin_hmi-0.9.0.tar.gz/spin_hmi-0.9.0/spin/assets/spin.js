// Status constants
const State = {
    OK: "ok",
    WARN: "warn",
    BUSY: "busy",
    DISABLED: "disabled",
    ERROR: "error",
    UNKNOWN: "unknown",
};

const LABEL = /^@([\w.]+)(?: "(.*?)")?((?: \w+(?:=[^ ]*)?)*)$/;
const PLOT_COMMON = /(?: "(.*?)")?((?: \w+(?:=[^ @]*)?)*)/;
const PLOT_ITEM = /@([\w.]+)(?: "(.*?)")?((?: \w+(?:=[^ @]*)?)*)/g;
const KEYVAL = /(\w+)(?:=([^ ]*))?/g;
const $ = document.querySelector.bind(document);
const $$ = document.querySelectorAll.bind(document);
const AUTO_PLOT_INTERVAL = 5000; // millis

Chart.defaults.font.family = "Open Sans,HelveticaNeue-Light,Helvetica Neue Light,Helvetica Neue,Helvetica,Arial,sans-serif";

var Spin = {
    current_socket: null,
    numeric_keyboard: null,
    stringy_keyboard: null,
    keyboard_callback: null,
    confirm_callback: null,
    reconnect_timeout: 0,  // On startup, "re"connect immediately.
    all_errors: {},
    display_elements: {},
    plot_descriptors: [],
    plot_elements: {},
    plot_interval: null,

    connect: function() {
        let ws = new WebSocket(`ws://${location.host}/ws`);
        ws.addEventListener("open", this.on_connect.bind(this));
        ws.addEventListener("close", this.on_disconnect.bind(this));
        ws.addEventListener("message", this.on_message.bind(this));
        this.current_socket = ws;
    },

    reconnect: function() {
        setTimeout(this.connect.bind(this), this.reconnect_timeout);
        this.reconnect_timeout = 2000;
        this.process_common_update(State.ERROR,
                                   {"hostinfo": "(disconnected)",
                                    "version": "Disconnected"});
    },

    on_connect: function() {
        console.log("connected to spin backend");
        this.clear_all_errors();
        document.documentElement.style.backgroundColor = "";
        let event = new CustomEvent("spinconnect");
        window.dispatchEvent(event);
    },

    on_disconnect: function() {
        console.log("disconnected, trying reconnect in", this.reconnect_timeout, "ms");
        document.documentElement.style.backgroundColor = "#ffcccc";
        let event = new CustomEvent("spindisconnect");
        window.dispatchEvent(event);
        this.reconnect();
    },

    on_message: function(event) {
        let data = JSON.parse(event.data);

        // this is set if it's a Reply
        if (data.action !== undefined) {
            this.process_reply(data);
        } else if (data.key == "__common__") {
            this.process_common_update(data.state, data.value);
        } else {
            this.process_update(data);
            let event = new CustomEvent("spinupdate", {detail: data});
            window.dispatchEvent(event);
        }
    },

    send_request: function(key, transform, action, intent, data) {
        this.current_socket.send(
            JSON.stringify({"key": key, "transform": transform, "action": action,
                            "intent": intent, "data": data}));
    },

    set_tooltip: function(element, tip) {
        if (element.namespaceURI.endsWith("svg")) {
            let title = element.querySelector("title");
            if (title !== null) {
                title.textContent = tip;
            } else {
                title = document.createElementNS(element.namespaceURI, "title");
                title.textContent = tip;
                element.appendChild(title);
            }
        } else {
            element.setAttribute("title", tip);
        }
    },

    test_condition: function(spec, value) {
        let [negative, conds] = spec;
        for (let [op, val, invert] of conds) {
            switch (op) {
            case ">":
                if (invert && value <= val) return !negative;
                if (value > val) return !negative;
                break;
            case "<":
                if (invert && value >= val) return !negative;
                if (value < val) return !negative;
                break;
            case "=":
                if (invert && String(value) != val) return !negative;
                if (value == val) return !negative;
            }
        }
        return negative;
    },

    process_update: function(data) {
        this.handle_error(data.key, data.state == State.ERROR ? data.state_str : null);

        for (let desc of this.display_elements[data.key] || []) {
            let value = data.value;

            if (desc.transform) {
                switch (desc.transform[0]) {
                case "bits":
                    let [_, first, num] = desc.transform;
                    value = (value >> first) & ((1 << num) - 1);
                    break;
                case "scale":
                    value = value * desc.transform[1];
                    break;
                default:
                }
            }
            for (let cel of desc.text_els) {
                let text;
                if (data.value === null) {
                    text = "???";
                } else if (desc.format) {
                    let unit = data.unit.replace("%", "%%");
                    text = sprintf(desc.format.replace("{unit}", unit), value);
                } else {
                    text = String(value);
                }
                cel.textContent = text;
                // this should make it styled according to state
                cel.dataset.state = data.state;
                this.set_tooltip(cel, data.state_str);
            }

            for (let cel of desc.color_els) {
                cel.dataset.state = data.state;
                if (desc.highlight) {
                    if (this.test_condition(desc.highlight, value)) {
                        cel.dataset.state = "special";
                    }
                }
            }

            if (desc.show_if) {
                if (!this.test_condition(desc.show_if, value)) {
                    desc.element.dataset.state = "hidden";
                } else {
                    desc.element.dataset.state = data.state;
                }
            }

            if (desc.show_if_status) {
                if (!desc.show_if_status.includes(data.state)) {
                    desc.element.dataset.state = "hidden";
                } else {
                    desc.element.dataset.state = data.state;
                }
            }
        }

        for (let desc of this.display_elements[data.key + "-state"] || []) {
            desc.element.textContent = data.state_str;
        }

        let now = new Date().getTime();
        for (let desc of this.plot_elements[data.key] || []) {
            this.add_plot_point(now, desc, data.value);
        }
    },

    add_plot_point: function(now, curve, value) {
        let limit = now - curve.plot.interval * 60000;
        let array = curve.plot.chart.data.datasets[curve.index].data;
        var cut = 0;
        while (array.length > cut && array[cut].x < limit) {
            cut++;
        }
        array.splice(0, cut);
        array.push({x: now, y: value});
        curve.plot.chart.update();
    },

    auto_plot_update: function() {
        let now = new Date().getTime();
        let limit = now - AUTO_PLOT_INTERVAL + 500;
        for (let plot of this.plot_descriptors) {
            for (let curve of plot.curves) {
                let array = plot.chart.data.datasets[curve.index].data;
                if (array[array.length - 1].x < limit) {
                    this.add_plot_point(now, curve, array[array.length - 1].y);
                }
            }
        }
    },

    process_common_update: function(state, data) {
        for (let el of $$("[data-common=hostinfo]")) {
            el.textContent = data.hostinfo;
            el.dataset.state = state;
        }
        for (let el of $$("[data-common=version]")) {
            el.textContent = data.version;
        }
    },

    process_reply: function(data) {
        switch (data.action) {
        case "error":
            this.error_show(data.data);
            break;
        case "input":
            this.input_show(
                data.data,
                (value) => this.send_request(data.key, data.transform, "input", "", value));
            break;
        case "confirm":
            this.confirm_show(
                data.data.what, data.data.prompt,
                () => this.send_request(data.key, data.transform, "confirm",
                                        data.data.intent, data.data.data));
            break;
        case "progress":
            this.progress_show(data.data[0], data.data[1]);
            break;
        case "restart":
            // Server is restarting (most likely due to changed config),
            // schedule a full reload in 5 seconds
            console.log("server restarting, schedule full reload...");
            setTimeout(() => window.location.reload(true), 5000);
            break;
        default:
            let event = new CustomEvent("spinreply", {detail: data});
            window.dispatchEvent(event);
        }
    },

    clear_all_errors: function() {
        for (let key of Object.keys(this.all_errors)) {
            this.handle_error(key, null);
        }
    },

    handle_error: function(key, what) {
        if (what === null) {
            if (this.all_errors.hasOwnProperty(key)) {
                let node = this.all_errors[key];
                node.remove();
                delete this.all_errors[key];
            }
            if (Object.keys(this.all_errors).length === 0) {
                $("#info-button").style.display = "inline";
                $("#error-button").style.display = "none";
                $("#no-error").style.display = "block";
            }
            return;
        }
        let node;
        if (this.all_errors.hasOwnProperty(key)) {
            node = this.all_errors[key];
        } else {
            node = $("#error-row").content.cloneNode(true).children[0];
            this.all_errors[key] = node;
            $("#info-errorlist").appendChild(node);
            let date = luxon.DateTime.now();
            node.children[2].textContent = date.toISODate() + " " +
                date.toISOTime({precision: "minutes", includeOffset: false});
        }
        node.children[0].textContent = key;
        node.children[1].textContent = what;
        $("#error-button").style.display = "inline";
        $("#info-button").style.display = "none";
        $("#no-error").style.display = "none";
    },

    parse_conds: function(val, invert=false) {
        return [invert, val.split(",").map((s) => this.parse_cond(s))];
    },

    parse_cond: function(val, invert=false) {
        while (val[0] == "!") {
            invert = !invert;
            val = val.substring(1);
        }
        var cond = "=";
        if (val.substring(0, 2) == ">=") {
            invert = !invert;
            cond = "<";
            val = this.maybe_float(val.substring(2));
        } else if (val.substring(0, 1) == ">") {
            cond = ">";
            val = this.maybe_float(val.substring(1));
        } else  if (val.substring(0, 2) == "<=") {
            invert = !invert;
            cond = ">";
            val = this.maybe_float(val.substring(2));
        } else if (val.substring(0, 1) == "<") {
            cond = "<";
            val = this.maybe_float(val.substring(1));
        } else if (val.substring(0, 1) == "=") {
            val = this.maybe_float(val.substring(1));
        }
        return [cond, val, invert];
    },

    parse_statuses: function(val, invert=false) {
        let parts = val.split(",");
        let matches = invert ? Object.values(State) : [];
        for (let part of parts) {
            part = part.trim().toUpperCase();
            if (State.hasOwnProperty(part)) {
                if (invert) {
                    let idx = matches.indexOf(State[part]);
                    if (idx >= 0)
                        matches.splice(idx, 1);
                } else {
                    matches.push(State[part]);
                }
            }
        }
        return matches;
    },

    maybe_float: function(val) {
        let parsed = parseFloat(val);
        if (!isNaN(parsed))
            return parsed;
        return val;
    },

    parse_toggle: function(val) {
        if (!val)
            return null;
        // Parse two comma-separated values.
        let parts = val.split(",");
        return [this.maybe_float(parts[0]), this.maybe_float(parts[1])];
    },

    preprocess_element: function(el, label) {
        if (!label.startsWith("@"))
            return;
        let match = label.match(LABEL);
        if (match === null)
            return;
        let [_, key, fmt, rest] = match;

        let descriptor = {
            "element": el,
            "transform": null,
            "format": fmt || null,
            "intent": null,
            "highlight": null,
            "show_if": null,
            "show_if_status": null,
            "text_els": [],
            "color_els": [],
        };

        let opts = (rest || "").matchAll(KEYVAL);
        for (let [_, mkey, mval] of opts) {
            switch (mkey) {
            // special
            case "status": key += "-state"; break;
            // transforms
            case "bit":    descriptor.transform = ["bits", parseInt(mval) || 0, 1]; break;
            case "bits":
                let [frombit, tobit] = mval.split("-");
                descriptor.transform = ["bits", parseInt(frombit) || 0,
                                        tobit - frombit + 1 || 0];
                break;
            case "scale":  descriptor.transform = ["scale", parseFloat(mval) || 1]; break;
            // display/presentation
            case "hl":     descriptor.highlight = this.parse_conds(mval); break;
            case "nohl":   descriptor.highlight = this.parse_conds(mval, true); break;
            case "show":   descriptor.show_if = this.parse_conds(mval); break;
            case "hide":   descriptor.show_if = this.parse_conds(mval, true); break;
            case "showstatus":
                descriptor.show_if_status = this.parse_statuses(mval); break;
            case "hidestatus":
                descriptor.show_if_status = this.parse_statuses(mval, true); break;
            // action intents
            case "toggle": descriptor.intent = [mkey, this.parse_toggle(mval)]; break;
            case "input":
            case "stop":
            case "reset":  descriptor.intent = [mkey, null]; break;
            case "set":    descriptor.intent = [mkey, this.maybe_float(mval)]; break;
            case "run":    descriptor.intent = [mkey, mval]; break;
            // custom
            case "custom":
                console.log("Found custom field:", key, "for context", mval);
                let event = new CustomEvent("spincustomelement", {
                    detail: {
                        element: el,
                        context: mval,
                        key: key,
                        options: opts,
                    },
                    // Let the receiving code decide whether to also apply the
                    // default processing to receive updates.
                    cancelable: true});
                if (!window.dispatchEvent(event))
                    return;
                break;
            }
        }
        console.log("Found field:", key, "with", descriptor);

        let handle_el = (el) => {
            if (el.tagName == "text" || el.tagName == "SPAN" || el.tagName == "DIV") {
                // If it's a text element that has exactly one <tspan> child,
                // use that for the content to preserve formattings.
                if (el.children.length == 1 && el.children[0].tagName == "tspan") {
                    el = el.children[0];
                }
                if (fmt !== undefined) {
                    descriptor.text_els.push(el);
                }
                if (key == "hostinfo") {
                    el.dataset.common = "hostinfo";
                }
            }
            if (el.tagName == "rect" || el.tagName == "ellipse" ||
                el.tagName == "path" ||
                el.tagName == "SPAN" || el.tagName == "DIV") {
                descriptor.color_els.push(el);
            }
        }

        // If it's a group element, handle its contents.
        if (el.tagName == "g") {
            for (let cel of el.children) {
                handle_el(cel);
            }
        } else {
            handle_el(el);
        }

        if (descriptor.intent)
            el.dataset.intentKey = key;

        // Initially hide all conditionally shown elements.
        if (descriptor.show_if || descriptor.show_if_status)
            el.dataset.state = "hidden";

        if (key in this.display_elements) {
            this.display_elements[key].push(descriptor);
        } else {
            this.display_elements[key] = [descriptor];
        }
    },

    preprocess_plot: function(el, label) {
        let plot = {
            element: el,
            interval: 60,
            fontsize: 16,
            yscale: "linear",
            legend: "bottom",
            title: null,
            curves: [],
        };

        let cmatch = label.match(PLOT_COMMON);
        if (cmatch) {
            let [_, title, rest] = cmatch;
            if (title)
                plot.title = title;
            for (let [_, mkey, mval] of (rest || "").matchAll(KEYVAL)) {
                switch (mkey) {
                case "fontsize": plot.fontsize = parseInt(mval) || 16; break;
                case "legend":   plot.legend = mval; break;
                case "interval": plot.interval = parseFloat(mval) || 60; break;
                case "logscale": plot.yscale = "logarithmic"; break;
                }
            }
        }

        var use_y2 = false;
        for (let match of label.matchAll(PLOT_ITEM)) {
            let [_, key, lbl, rest] = match;

            let curve = {
                plot: plot,
                index: plot.curves.length,
                label: lbl || key,
                color: null,
                y2: false,
            };

            for (let [_, mkey, mval] of (rest || "").matchAll(KEYVAL)) {
                switch (mkey) {
                case "color": curve.color = mval; break;
                case "y2":    curve.y2 = true; use_y2 = true; break;
                }
            }

            if (key in this.plot_elements) {
                this.plot_elements[key].push(curve);
            } else {
                this.plot_elements[key] = [curve];
            }
            plot.curves.push(curve);
        }

        let datasets = [];
        for (let curve of plot.curves) {
            datasets.push({
                data: [],
                label: curve.label,
                borderColor: curve.color,
                yAxisID: curve.y2 ? "y2" : "y",
            });
        }

        plot.chart = new Chart(el, {
            type: "line",
            data: {datasets: datasets},
            options: {
                animation: false,
                parsing: false,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        type: "timestack",
                        ticks: {font: {size: plot.fontsize}},
                    },
                    y: {
                        type: plot.yscale,
                        ticks: {font: {size: plot.fontsize}},
                    },
                    y2: {
                        type: plot.yscale,
                        position: "right",
                        ticks: {font: {size: plot.fontsize}},
                        display: use_y2,
                    }
                },
                events: ["mousemove", "mouseout", "click", "touchstart",
                         "touchmove", "dblclick"],
                plugins: {
                    legend: {
                        display: plot.legend != "none",
                        position: plot.legend,
                        labels: {font: {size: plot.fontsize}},
                    },
                    title: {
                        display: plot.title !== null,
                        text: plot.title,
                        font: {size: plot.fontsize * 1.5},
                    },
                    zoom: {
                        pan: {enabled: true},
                        zoom: {wheel: {enabled: true},
                               pinch: {enabled: true}},
                    },
                }
            },
            plugins: [{id: "dblclick",
                       afterEvent: (chart, evt, opts) => {
                           if (evt.event.type === "dblclick")
                               if (chart.isZoomedOrPanned())
                                   chart.resetZoom();
                       }
                      }]
        });

        this.plot_descriptors.push(plot);
        if (this.plot_interval === null)
            this.plot_interval = setInterval(() => this.auto_plot_update(), AUTO_PLOT_INTERVAL);
    },

    preprocess: function() {
        // Move SVG trees into the main document
        for (let el of $$("object")) {
            if (el.contentDocument) {
                let svg = el.contentDocument.children[0];
                for (let attr of ["style", "class"]) {
                    if (el.hasAttribute(attr)) {
                        svg.setAttribute(attr, el.getAttribute(attr));
                    }
                }
                el.replaceWith(svg);
                svg.style.display = "block";
            }
        }

        // Handle plots from inkscape:label (SVG)
        for (let svg_el of $$("[*|label]")) {
            let label = svg_el.getAttribute("inkscape:label");
            if (label.startsWith("!plot ")) {
                let foreign_el = document.createElementNS(svg_el.namespaceURI, "foreignObject");
                for (let attr of ["x", "y", "width", "height", "transform"]) {
                    if (svg_el.hasAttribute(attr)) {
                        foreign_el.setAttribute(attr, svg_el.getAttribute(attr));
                    }
                }
                let canvas_el = document.createElement("canvas");
                foreign_el.appendChild(canvas_el);
                svg_el.replaceWith(foreign_el);
                this.preprocess_plot(canvas_el, label.substring(5));
            } else {
                this.preprocess_element(svg_el, svg_el.getAttribute("inkscape:label"));
                svg_el.removeAttribute("inkscape:label");
            }
        }

        // Apply from data-spin (HTML)
        for (let el of $$("[data-spin]")) {
            this.preprocess_element(el, el.dataset.spin);
            delete el.dataset.spin;
        }

        // Handle plots from data-spin-plot (HTML)
        for (let el of $$("canvas[data-spin-plot]")) {
            this.preprocess_plot(el, el.dataset.spinPlot);
            delete el.dataset.spinPlot;
        }
    },

    on_click: function(event) {
        if (FORCE_READONLY) return;

        let el = event.target;
        while (el !== null) {
            if (el.dataset.intentKey) {
                for (let desc of this.display_elements[el.dataset.intentKey]) {
                    if (desc.element === el) {
                        console.log("Clicked on", desc);
                        this.send_request(el.dataset.intentKey,
                                          desc.transform, "click",
                                          desc.intent[0], desc.intent[1]);
                        return;
                    }
                }
            }
            el = el.parentElement;
        }
    },

    send_file: function(key, file, data) {
        var reader = new FileReader();
        reader.addEventListener(
            "load",
            () => {
                this.send_request(key,
                    "",
                    "upload",
                    "",
                    {
                        "filename": file.name,
                        "contents": reader.result,
                        ...data,
                    },
                );
            },
        );
        reader.readAsDataURL(file);
    },

    input_show: function(valuetype, callback) {
        this.keyboard_callback = callback;
        if (valuetype[0] == "int" || valuetype[0] == "float") {
            $("#numeric-overlay").style.display = "flex";
            $("#numeric-input").dataset.type = valuetype[0];
            $("#numeric-input").dataset.min = valuetype[1];
            $("#numeric-input").dataset.max = valuetype[2];
            $("#numeric-input").focus();
        } else if (valuetype[0] == "str") {
            $("#stringy-overlay").style.display = "flex";
            $("#stringy-input").focus();
        } else if (valuetype[0] == "choice") {
            let choice = $("#choice-input");
            choice.replaceChildren();
            for (let text of valuetype[1]) {
                let opt = document.createElement("option");
                opt.value = text;
                opt.textContent = text;
                choice.appendChild(opt);
            }
            $("#choice-overlay").style.display = "flex";
        }
    },

    on_numeric_keyboard_change: function(input) {
        $("#numeric-input").value = input;
        this.validate_numeric_input();
    },

    on_numeric_keyboard_press: function(button) {
        if (button === "{escape}") {
        } else if (button === "{enter}") {
            let data = $("#numeric-input").dataset;
            let number = +$("#numeric-input").value;
            if (data.type == "int") {
                number = Math.round(number);
            }
            if (number < data.min || number > data.max) {
                // out of validation range
                return;
            }
            this.keyboard_callback(number);
        } else {
            return;
        }
        this.numeric_keyboard_cancel();
    },

    numeric_keyboard_cancel: function() {
        this.keyboard_callback = null;
        this.numeric_keyboard.setInput("");
        $("#numeric-input").value = "";
        $("#numeric-input").style.color = "";
        $("#numeric-overlay").style.display = "none";
    },

    on_numeric_input_change: function(event) {
        this.numeric_keyboard.setInput($("#numeric-input").value);
        this.validate_numeric_input();
    },

    validate_numeric_input: function() {
        let data = $("#numeric-input").dataset;
        let number = +$("#numeric-input").value;
        if (Number.isNaN(number) || number < data.min || number > data.max) {
            $("#numeric-input").style.color = "red";
        } else {
            $("#numeric-input").style.color = "";
        }
    },

    on_stringy_keyboard_change: function(input) {
        $("#stringy-input").value = input;
    },

    on_stringy_keyboard_press: function(button) {
        if (button === "{shift}") {
            let cur_lay = this.stringy_keyboard.options.layoutName;
            let new_lay = currentLayout === "default" ? "shift" : "default";
            this.stringy_keyboard.setOptions({layoutName: new_lay});
            return;
        } else if (button === "{escape}") {
        } else if (button === "{enter}") {
            this.keyboard_callback($("#stringy-input").value);
        } else {
            return;
        }
        this.stringy_keyboard_cancel();
    },

    stringy_keyboard_cancel: function() {
        this.keyboard_callback = null;
        this.stringy_keyboard.setInput("");
        $("#stringy-input").value = "";
        $("#stringy-overlay").style.display = "none";
    },

    on_stringy_input_change: function(event) {
        this.stringy_keyboard.setInput($("#stringy-input").value);
    },

    choice_keyboard_submit: function() {
        this.keyboard_callback($("#choice-input").value);
        this.choice_keyboard_cancel();
    },

    choice_keyboard_cancel: function() {
        this.keyboard_callback = null;
        $("#choice-overlay").style.display = "none";
    },

    init_clock: function() {
        for (let el of $$("#nav-clock")) {
            let update = () => {
                el.textContent = luxon.DateTime.now().toLocaleString(
                    luxon.DateTime.TIME_24_WITH_SECONDS);
            }
            update();
            setInterval(update, 1000);
        }
    },

    init_keyboards: function() {
        let Keyboard = window.SimpleKeyboard.default;
        this.numeric_keyboard = new Keyboard(".numeric-keyboard", {
            onChange: this.on_numeric_keyboard_change.bind(this),
            onKeyPress: this.on_numeric_keyboard_press.bind(this),
            theme: "hg-theme-default hg-layout-numeric numeric-theme",
            layout: {
                default: ["1 2 3",
                          "4 5 6",
                          "7 8 9",
                          ". 0 -",
                          "{escape} {bksp} {enter}"]
            },
            display: {
                "{escape}": "cancel",
                "{shift}": "⇧",
                "{bksp}": "⌫",
                "{enter}": "enter ↵",
            },
            inputName: "numeric"
        });
        this.stringy_keyboard = new Keyboard(".stringy-keyboard", {
            onChange: this.on_stringy_keyboard_change.bind(this),
            onKeyPress: this.on_stringy_keyboard_press.bind(this),
            theme: "hg-theme-default",
            layout: {
                default: [
                    "` 1 2 3 4 5 6 7 8 9 0 - = {bksp}",
                    "q w e r t y u i o p [ ] \\",
                    "a s d f g h j k l ; '",
                    "{shift} z x c v b n m , . / {shift}",
                    "{escape} {space} {enter}",
                ],
                shift: [
                    "~ ! @ # $ % ^ & * ( ) _ + {bksp}",
                    "Q W E R T Y U I O P { } |",
                    'A S D F G H J K L : "',
                    "{shift} Z X C V B N M < > ? {shift}",
                    "{escape} {space} {enter}",
                ],
            },
            display: {
                "{escape}": "cancel",
                "{shift}": "⇧",
                "{bksp}": "⌫",
                "{enter}": "enter ↵",
                "{space}": " ",
            },
            inputName: "stringy"
        });
        $("#numeric-input").addEventListener("input", this.on_numeric_input_change.bind(this));
        $("#numeric-input").addEventListener("keyup", (ev) => {
            if (ev.key === "Enter" || ev.keyCode === 13) {
                this.on_numeric_keyboard_press("{enter}");
            }
        });
        $("#stringy-input").addEventListener("input", this.on_stringy_input_change.bind(this));
        $("#stringy-input").addEventListener("keyup", (ev) => {
            if (ev.key === "Enter" || ev.keyCode === 13) {
                this.on_stringy_keyboard_press("{enter}");
            }
        });
    },

    error_show: function(text) {
        $("#error-message").textContent = text;
        $("#error-overlay").style.display = "flex";
    },

    error_ok: function() {
        $("#error-overlay").style.display = "none";
    },

    confirm_show: function(what, prompt, callback) {
        this.confirm_callback = callback;
        $("#confirm-what").textContent = what;
        $("#confirm-message").textContent = prompt;
        $("#confirm-overlay").style.display = "flex";
    },

    confirm_ok: function() {
        this.confirm_callback();
        this.confirm_cancel();
    },

    confirm_cancel: function() {
        this.confirm_callback = null;
        $("#confirm-overlay").style.display = "none";
    },

    progress_show: function(text, fraction) {
        if (fraction >= 1) {
            $("#progress-overlay").style.display = "none";
        } else {
            $("#progress-text").textContent = text;
            $("#progress-bar").style.setProperty("--progress", 100 * fraction);
            $("#progress-overlay").style.display = "flex";
        }
    },

    resync: function() {
        this.reconnect_timeout = 10;
        this.current_socket.close();
        // close all overlays
        this.confirm_cancel();
        this.error_ok();
        this.progress_show("", 1);
        this.numeric_keyboard_cancel();
        this.stringy_keyboard_cancel();
        this.choice_keyboard_cancel();
    },

    toggle_info: function() {
        let ovl = $("#info-overlay");
        let btn = $("#info-button");
        let btn2 = $("#error-button");
        if (ovl.style.display == "block") {
            ovl.style.display = "none";
            btn.style.filter = "none";
            btn2.style.filter = "none";
        } else {
            ovl.style.display = "block";
            btn.style.filter = "drop-shadow(0px 0px 2px black)";
            btn2.style.filter = "drop-shadow(0px 0px 2px black)";
        }
    },

    toggle_control: function(url_tmpl) {
        let url = url_tmpl.replace("{host}", location.hostname);
        let ovl = $("#control-overlay");
        let iframe = $("#control-inner");
        let btn = $("#control-button");
        if (ovl.style.display == "block") {
            ovl.style.display = "none";
            btn.style.filter = "none";
            iframe.src = "about:blank";
        } else {
            iframe.src = url;
            ovl.style.display = "block";
            btn.style.filter = "drop-shadow(0px 0px 2px black)";
        }
    },

    on_resize: function() {
        let el = $("#content");
        el.style.transform = "";
        let factor = window.innerWidth / el.scrollWidth;
        if (factor < 1) {
            el.style.transform = `scale(${factor})`;
        }
    },

    startup_phase1: function() {
        this.preprocess();
    },

    auto_logout: function() {
        // in case we're on a protected page, try to access the URL again
        // with wrong credentials to make the browser forget the right ones
        const url = `${location.protocol}//${location.host}${location.pathname}`;
        const xhr = new XMLHttpRequest();
        xhr.open("GET", url, true, "dummy", "dummy");
        xhr.send();
    },

    startup: function() {
        // preprocess again to catch content in loaded SVGs
        this.preprocess();
        this.init_clock();
        this.init_keyboards();
        let event = new CustomEvent("spinstartup");
        window.dispatchEvent(event);
        document.body.addEventListener("click", this.on_click.bind(this));
        window.addEventListener("resize", this.on_resize.bind(this));
        this.on_resize();
        this.reconnect();
        if (PAGE_HAS_AUTH)
            this.auto_logout();
    }
};

document.addEventListener("DOMContentLoaded", () => Spin.startup_phase1());
window.addEventListener("load", () => Spin.startup());
