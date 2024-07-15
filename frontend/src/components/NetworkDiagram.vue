<template>
    <div v-if="isLoading" class="loading-container">
        <div class="loading-message">
            <span class="loading-spinner"></span>
            Loading...
        </div>
    </div>
    <div v-else>
        <div v-if="errorMessage" class="error-message">
            {{ errorMessage }}
        </div>
        <div v-else>
            <div class="checkbox-container">
                <label>
                    <input type="checkbox" v-model="useFilteredEdges" @change="toggleEdges">
                    Show blocked links
                </label>
                <span class="elapsed-time">Elapsed time: {{ elapsed_time.value }} {{ elapsed_time.unit }}</span>
            </div>

            <!-- <b-sidebar id="node-info-sidebar" title="Node Information" right shadow>
                <div class="px-3 py-2">
                    <p v-if="selectedNode">
                        <strong>Device:</strong> {{ selectedNode.device }}<br>
                        <strong>Device Type:</strong> {{ selectedNode.device_type }}<br>
                        <strong>Label:</strong> {{ selectedNode.label }}<br>
                        <strong>Level:</strong> {{ selectedNode.level }}
                    </p>
                    <p v-else>No node selected</p>
                </div>
            </b-sidebar> -->

            <div id="mynetwork"></div>
        </div>
    </div>
</template>

<script>
import axios from "axios";
import { Network } from 'vis-network';
//import { BSidebar } from 'bootstrap-vue'

export default {
    name: "NetworkDiagram",
    // components: {
    //     BSidebar
    // },
    data() {
        return {
            nodes: [],
            edges: [],
            edges_with_blocked_links: [],
            results: [],
            isLoading: false,
            errorMessage: '',
            useFilteredEdges: false,
            network: null,
            elapsed_time: 0,
            selectedNode: null,
        }
    },
    mounted() {
        this.getNodesAndEdges()
            .then(() => {
                this.initNetwork();
            })
            .catch(err => {
                console.log(err);
            });
    },
    methods: {
        getNodesAndEdges() {
            this.isLoading = true;
            this.errorMessage = '';
            const apiUrl = `${import.meta.env.VITE_API_PROTOCOL}://${import.meta.env.VITE_API_HOST}:${import.meta.env.VITE_API_PORT}${import.meta.env.VITE_API_ENDPOINT}`;
            return axios
                .get(apiUrl)
                .then(response => {
                    this.nodes = response.data.nodes;
                    this.edges = response.data.edges;
                    this.edges_with_blocked_links = response.data.edges_with_blocked_links;
                    this.elapsed_time = response.data.elapsed_time;
                    this.results = response.data.results;
                    console.log("results: ", response.data.results);
                })
                .catch(error => {
                    this.error_description = error.response.data.detail;
                    this.status_code = error.response.status;
                    this.errorMessage = `${this.error_description}. Status code: ${this.status_code}`;
                })
                .finally(() => {
                    this.isLoading = false;
                });
        },
        initNetwork() {
            const container = document.getElementById('mynetwork');
            const data = {
                nodes: this.nodes,
                edges: this.edges
            };
            const options = this.getNetworkOptions();
            this.updateNetwork(container, data, options);
        },
        updateNetwork(container, data, options) {
            if (this.network) {
                this.network.destroy();
            }
            this.network = new Network(container, data, options);

            // Save a reference to 'this' for use it within the callback function
            const self = this;

            // onClick event handler
            this.network.on("click", function (params) {
                const selected_node = this.getNodeAt(params.pointer.DOM);
                if (selected_node != null) {
                    console.log("Click event -> node id: " + selected_node);
                    
                    // Look for the selected node within results variable
                    const selectedResult = self.results.find(result => result.id === selected_node);
                    
                    if (selectedResult) {
                        console.log("device:", selectedResult.device);
                        console.log("device_type:", selectedResult.device_type);
                        console.log("label:", selectedResult.label);
                        console.log("level:", selectedResult.level);
                        
                        // Aquí puedes hacer lo que necesites con selectedResult.device y selectedResult.label
                        self.selectedNode = selectedResult;
                        self.$root.$emit('bv::toggle::sidebar', 'node-info-sidebar');
                    } else {
                        console.log("No se encontró información para el nodo seleccionado");
                        self.selectedNode = null;
                    }
                }
            });

        },
        toggleEdges() {
            const container = document.getElementById('mynetwork');
            const data = {
                nodes: this.nodes,
                edges: this.useFilteredEdges ? this.edges_with_blocked_links : this.edges
            };
            const options = this.getNetworkOptions();

            this.updateNetwork(container, data, options);
        },
        getNetworkOptions() {
            return {
                nodes: {
                    font: {
                        size: 18,
                        color: "#000000"
                    },
                    borderWidth: 1,
                    shadow: true,
                },
                edges: {
                    smooth: {
                        enabled: true,
                        type: "cubicBezier",
                        forceDirection: "vertical",
                        roundness: 0.5
                    }
                },
                interaction: {
                    hover: true,
                    tooltipDelay: 50
                },
                layout: {
                    hierarchical: {
                        direction: "DU",
                        sortMethod: 'directed'
                    }
                },
                physics: {
                    enabled: true,
                    stabilization: false
                }
            };
        }
    },
}
</script>

<style>
html,
body {
    height: 100%;
    margin: 0;
    padding: 0;
}

.checkbox-container {
    margin: 10px;
    color: #ffffff;
    display: flex;
    align-items: center;
}

#mynetwork {
    width: 100%;
    height: 877px;
    border: 1px solid lightgray;
    background-color: #333;
}

h2 {
    text-align: center;
}

.loading-container {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh;
}

.loading-message {
    display: flex;
    flex-direction: column;
    align-items: center;
    font-size: 18px;
    color: #fdfdfd;
}

.loading-spinner {
    display: inline-block;
    width: 24px;
    height: 24px;
    border-radius: 50%;
    border: 4px solid #ccc;
    border-top-color: #888;
    animation: spin 1s ease-in-out infinite;
    margin-bottom: 8px;
}

@keyframes spin {
    0% {
        transform: rotate(0deg);
    }

    100% {
        transform: rotate(360deg);
    }
}

.error-message {
    margin: 16px;
    padding: 16px;
    background-color: #ffdddd;
    color: #ff0000;
    border: 1px solid #ff0000;
    border-radius: 4px;
}

.vis-tooltip {
    position: absolute;
    visibility: visible;
    background-color: #f9f9f9;
    border: 1px solid #d3d3d3;
    border-radius: 4px;
    padding: 8px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    color: #333;
    font-size: 16px;
    z-index: 1000;
    white-space: nowrap;
    pointer-events: none;
    transition: opacity 0.3s ease;
    opacity: 1;
}

.elapsed-time {
    margin-left: 10px;
    font-size: 14px;
}

.b-sidebar {
    background-color: #f8f9fa;
    color: #333;
}

.b-sidebar-header {
    background-color: #e9ecef;
    border-bottom: 1px solid #dee2e6;
}
</style>
