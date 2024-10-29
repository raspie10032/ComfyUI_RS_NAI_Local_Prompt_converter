import { app } from "../../scripts/app.js";

function findWidgetByName(node, name) {
    return node.widgets.find((w) => w.name === name);
}

app.registerExtension({
    name: "Comfy.NAIPromptExtractor",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "NAIPromptExtractor") {  // Change node name
            const onNodeCreated = nodeType.prototype.onNodeCreated;
            
            nodeType.prototype.onNodeCreated = function() {
                if (onNodeCreated) {
                    onNodeCreated.apply(this, arguments);
                }
                
                const uploadWidget = {
                    type: "button",
                    name: "upload_file",
                    text: "Choose file to upload",
                    callback: () => {
                        const input = document.createElement("input");
                        input.type = "file";
                        input.accept = "image/*";
                        input.style.display = "none";
                        document.body.appendChild(input);

                        input.onchange = async () => {
                            const file = input.files[0];
                            if (!file) return;

                            try {
                                const formData = new FormData();
                                formData.append("image", file);

                                const resp = await fetch("/upload/image", {
                                    method: "POST",
                                    body: formData,
                                });

                                const data = await resp.json();
                                
                                if (data.name) {
                                    const fileWidget = findWidgetByName(this, "original_file");
                                    if (fileWidget) {
                                        fileWidget.value = data.name;
                                    }

                                    const reloadWidget = findWidgetByName(this, "reload_files");
                                    if (reloadWidget) {
                                        reloadWidget.value = true;
                                    }
                                }
                            } catch (error) {
                                console.error("Upload failed:", error);
                                alert("Upload failed: " + error.message);
                            }

                            document.body.removeChild(input);
                        };

                        input.click();
                    }
                };

                const widgetIndex = this.widgets.findIndex(w => w.name === "original_file");
                if (widgetIndex !== -1) {
                    this.widgets.splice(widgetIndex + 1, 0, uploadWidget);
                }
            };
        }
    }
});