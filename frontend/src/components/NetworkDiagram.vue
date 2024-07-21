<template>
    <div>
        <div class="offcanvas offcanvas-end" tabindex="-1" id="offcanvasRight" aria-labelledby="offcanvasRightLabel">
            <div class="offcanvas-header">
                <div class="header-content">
                    <img :src="`./src/components/icons/${selectedNodeDeviceType}.png`" alt="Icon" class="sidebar-icon">
                    <h5 class="offcanvas-title" id="offcanvasRightLabel">{{ sidebarTitle }}</h5>
                </div>
                <button type="button" class="btn-close" data-bs-dismiss="offcanvas" aria-label="Close"></button>
            </div>
            <div class="offcanvas-body">
                <div v-if="selectedElementType === 'node'">
                    <p><strong>Mgmt IP address:</strong> {{ selectedNodeDevice }}</p>
                    <p><strong>Platform:</strong> {{ selectedNodeDeviceType }}</p>
                    <p><strong>Level:</strong> {{ selectedNodeLevel }}</p>
                    <p><strong>Version:</strong> {{ selectedNodeVersion }}</p>
                    <p><strong>Uptime:</strong> {{ selectedNodeUptime }}</p>
                    <p><strong>Serial:</strong> {{ selectedNodeSerial }}</p>
                </div>
                <div v-else-if="selectedElementType === 'edge'">
                    <!-- <p><strong>From:</strong> {{ selectedEdgeFrom }}</p>
                    <p><strong>To:</strong> {{ selectedEdgeTo }}</p>
                    <p><strong>Title:</strong> {{ selectedEdgeTitle }}</p> -->
                    <p>{{ selectedEdgeTitle }}</p>
                </div>
                <div v-if="selectedElementType === 'info_blocked_links'">
                <p><strong>Number of devices with blocked interfaces: {{ blocked_interfaces.length }}</strong></p>
                <p><strong>Number of blocked interfaces: {{ totalBlockedInterfaces }}</strong></p>
                <ul>
                <li v-for="(item, index) in blocked_interfaces" :key="index">
                    <strong>Device: {{ Object.keys(item)[0] }}</strong>
                    <ul>
                    <li v-for="(intf, interfaceIndex) in item[Object.keys(item)[0]].interfaces" :key="interfaceIndex">
                        Interface: {{ intf }}
                    </li>
                    </ul>
                </li>
                </ul>
            </div>
            </div>
        </div>
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
                    &nbsp;&nbsp;
                    <label>
                        <input type="checkbox" v-model="checked" @change="infoBlockedLinks">
                        Show blocked link information
                    </label>
                    &nbsp;&nbsp;
                    <span class="elapsed-time">Elapsed time: {{ elapsed_time.value }} {{ elapsed_time.unit }}</span>
                </div>
                <div id="mynetwork"></div>
            </div>
        </div>
    </div>
</template>

<script>
import axios from "axios";
import { Network } from 'vis-network';
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap';

export default {
    name: "NetworkDiagram",
    data() {
        return {
            nodes: [],
            edges: [],
            edges_with_blocked_links: [],
            blocked_interfaces: [],
            results: [],
            isLoading: false,
            errorMessage: '',
            useFilteredEdges: false,
            network: null,
            elapsed_time: 0,
            sidebarTitle: '',
            selectedNodeDevice: '',
            selectedNodeDeviceType: '',
            selectedNodeLevel: '',
            selectedNodeVersion: '',
            selectedNodeUptime: '',
            selectedNodeSerial: '',
            selectedElementType: '',
            selectedEdgeFrom: '',
            selectedEdgeTo: '',
            selectedEdgeTitle: '',
            checked: false,
            offcanvas: null
        }
    },
    mounted() {
        this.getNodesAndEdges()
            .then(() => {
                this.initNetwork();
                this.initOffcanvas();
            })
            .catch(err => {
                console.log(err);
            });
    },
    computed: {
        totalBlockedInterfaces() {
        return this.blocked_interfaces.reduce((total, item) => {
            const deviceKey = Object.keys(item)[0];
            return total + item[deviceKey].interfaces.length;
        }, 0);
        }
    },
    methods: {
        initOffcanvas() {
            const offcanvasElement = document.getElementById('offcanvasRight');
            this.offcanvas = new bootstrap.Offcanvas(offcanvasElement);
            
            offcanvasElement.addEventListener('hidden.bs.offcanvas', this.handleOffcanvasHidden);
        },
        handleOffcanvasHidden() {
            if (this.selectedElementType === 'info_blocked_links') {
                this.checked = false;
            }
        },
        getNodesAndEdges() {
            this.isLoading = true;
            this.errorMessage = '';
            
            const protocol = import.meta.env.VITE_API_PROTOCOL;
            const host = import.meta.env.VITE_API_HOST;
            const port = import.meta.env.VITE_API_PORT;
            const endpoint = import.meta.env.VITE_API_ENDPOINT_STP_GRAPH;
            const url = `${protocol}://${host}:${port}${endpoint}`;
            
            return axios
                .get(url)
                .then(response => {
                    this.nodes = response.data.nodes;
                    this.edges = response.data.edges;
                    this.edges_with_blocked_links = response.data.edges_with_blocked_links;
                    this.blocked_interfaces = response.data.blocked_interfaces;
                    this.elapsed_time = response.data.elapsed_time;
                    this.results = response.data.results;
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
                const selected_edge = this.getEdgeAt(params.pointer.DOM);
                if (selected_node != null) {
                    //console.log("Click event. node id: " + selected_node);

                    // Look for the selected node within results variable
                    const selectedNodeResult = self.results.find(result => result.id === selected_node);

                    if (selectedNodeResult) {
                        // Save data to show in sidebar
                        self.sidebarTitle = selectedNodeResult.label;
                        self.selectedElementType = 'node';

                        self.selectedNodeDevice = selectedNodeResult.device;
                        self.selectedNodeDeviceType = selectedNodeResult.device_type;
                        self.selectedNodeLevel = selectedNodeResult.level;
                        self.selectedNodeVersion = selectedNodeResult.version;
                        self.selectedNodeUptime = selectedNodeResult.uptime;
                        self.selectedNodeSerial = selectedNodeResult.serial;

                        // Show sidebar
                        const offcanvasElement = document.getElementById('offcanvasRight');
                        const offcanvas = new bootstrap.Offcanvas(offcanvasElement);
                        offcanvas.show();

                    } else {
                        console.log("No info found for the selected node");
                        self.selectedNode = null;
                    }
                } else if (selected_edge != null) {     
                    // Look for the selected edge within edges or edges_with_blocked_links
                    let selectedEdgeResult = null;
                    
                    if (self.useFilteredEdges) {
                        selectedEdgeResult = self.edges_with_blocked_links.find(edge => edge.id === selected_edge);
                    } else {
                        selectedEdgeResult = self.edges.find(edge => edge.id === selected_edge);
                    }

                    if (selectedEdgeResult) {
                        // Save data to show in sidebar
                        self.sidebarTitle = 'Link information'
                        self.selectedElementType = 'edge';

                        self.selectedNodeDeviceType = "information"
                        //self.selectedEdgeFrom = selectedEdgeResult.from;
                        //self.selectedEdgeTo = selectedEdgeResult.to;
                        self.selectedEdgeTitle = selectedEdgeResult.title;

                        // Show sidebar
                        const offcanvasElement = document.getElementById('offcanvasRight');
                        const offcanvas = new bootstrap.Offcanvas(offcanvasElement);
                        offcanvas.show();

                    } else {
                        console.log("No info found for the selected edge");
                        self.selectedEdge = null;
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
        infoBlockedLinks() {
            if (this.checked) {
                this.selectedElementType = 'info_blocked_links';
                this.sidebarTitle = 'Information';
                this.selectedNodeDeviceType = "information";

                this.offcanvas.show();
            } else {
                this.offcanvas.hide();
            }
        },
        beforeUnmount() {
        // Clean up the event listener when the component is destroyed
        const offcanvasElement = document.getElementById('offcanvasRight');
        offcanvasElement.removeEventListener('hidden.bs.offcanvas', this.handleOffcanvasHidden);
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
    background-color: #333;
}

.checkbox-container {
    margin: 10px;
    color: #ffffff;
    background-color: #333;
    display: flex;
    align-items: center;
}

#mynetwork {
    width: 100%;
    height: 877px;
    border: 1px solid #333;
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
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
    z-index: 10;
}

.offcanvas-title {
    font-weight: bold;
}

.offcanvas-body p {
    margin: 0;
    padding: 8px 0;
}

.offcanvas-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.header-content {
    display: flex;
    align-items: center;
}

.checkbox-container {
    display: flex;
    align-items: center;
}

.elapsed-time {
    /* margin-left: 15px; */
    margin-left: auto;
    color: #ffffff;
}

.check-button {
    margin-left: 55px;
}

.sidebar-icon {
    width: 24px;
    /* Ajusta el tamaño de la imagen según sea necesario */
    height: 24px;
    margin-right: 10px;
    /* Espacio entre la imagen y el título */
    object-fit: contain;
    /* Asegura que la imagen se escale correctamente */
}
</style>
