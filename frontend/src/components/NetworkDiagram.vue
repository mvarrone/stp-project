<template>
<div>
    <div class="offcanvas offcanvas-end" tabindex="-1" id="offcanvasRight" aria-labelledby="offcanvasRightLabel">
    <div class="offcanvas-header">
        <h5 class="offcanvas-title" id="offcanvasRightLabel">{{ selectedNodeLabel }}</h5>
        <button type="button" class="btn-close" data-bs-dismiss="offcanvas" aria-label="Close"></button>
    </div>
    <div class="offcanvas-body">
        <p><strong>Device:</strong> {{ selectedNodeDevice }}</p>
        <p><strong>Device Type:</strong> {{ selectedNodeDeviceType }}</p>
        <p><strong>Level:</strong> {{ selectedNodeLevel }}</p>
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
    results: [],
    isLoading: false,
    errorMessage: '',
    useFilteredEdges: false,
    network: null,
    elapsed_time: 0,
    // Propiedades para almacenar la información del nodo seleccionado
    selectedNodeLabel: '',
    selectedNodeDevice: '',
    selectedNodeDeviceType: '',
    selectedNodeLevel: ''
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
        // Save data to show in sidebar
        self.selectedNodeLabel = selectedResult.label;
        self.selectedNodeDevice = selectedResult.device;
        self.selectedNodeDeviceType = selectedResult.device_type;
        self.selectedNodeLevel = selectedResult.level;
        
        // Show sidebar
        const offcanvasElement = document.getElementById('offcanvasRight');
        const offcanvas = new bootstrap.Offcanvas(offcanvasElement);
        offcanvas.show();
        
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
</style>
