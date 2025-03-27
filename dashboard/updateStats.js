/* UPDATE THESE VALUES TO MATCH YOUR SETUP */

const PROCESSING_STATS_API_URL = "http://elaw24skytrain.canadacentral.cloudapp.azure.com:8100/stats"
const ANALYZER_API_URL = {
    stats: "http://elaw24skytrain.canadacentral.cloudapp.azure.com:8101/stats",
    station: "http://elaw24skytrain.canadacentral.cloudapp.azure.com:8101/status",
    maintenance: "http://elaw24skytrain.canadacentral.cloudapp.azure.com:8101/maintenance"
}

// This function fetches and updates the general statistics
const makeReq = (url, cb) => {
    fetch(url)
        .then(res => res.json())
        .then((result) => {
            console.log("Received data: ", result)
            cb(result);
        }).catch((error) => {
            updateErrorMessages(error.message)
        })
}

const updateCodeDiv = (result, elemId) => document.getElementById(elemId).innerText = JSON.stringify(result)

const getLocaleDateStr = () => (new Date()).toLocaleString()

const getStats = () => {
    document.getElementById("last-updated-value").innerText = getLocaleDateStr()
    
    makeReq(PROCESSING_STATS_API_URL, (result) => {
        const output = `Maximum Passengers: ${result.max_pg_readings}\n` + 
                `Number of Station Wait: ${result.num_sw_readings}\n` + 
                `Last Updated: ${result.last_updated}\n` +
                `Maximum Trains: ${result.max_tr_readings}\n` +
                `Number of Maintenance Inventory: ${result.num_my_readings}` + 
                `Last Updated: ${result.last_updated}\n`;

        document.getElementById("processing-stats").innerText = output; 
    });


    makeReq(ANALYZER_API_URL.stats, (result) => {
        const output = `Station Wait Events: ${result.num_station_count}\n` + 
                    `Maintenance Inventory Events: ${result.num_maintenance_count}`;

        document.getElementById("analyzer-stats").innerText = output; 
    });
    // makeReq(ANALYZER_API_URL.station, (result) => updateCodeDiv(result, "event-station"))
    // makeReq(ANALYZER_API_URL.maintenance, (result) => updateCodeDiv(result, "event-maintenance"))

    const randomIndex = Math.floor(Math.random() * 25);
    const stationWaitURL = `${ANALYZER_API_URL.station}?index=${randomIndex}`;
    const maintenanceInventoryURL = `${ANALYZER_API_URL.maintenance}?index=${randomIndex}`;

    makeReq(stationWaitURL, (result) => updateCodeDiv(result, "event-station"));
    makeReq(maintenanceInventoryURL, (result) => updateCodeDiv(result, "event-maintenance"));
}

const updateErrorMessages = (message) => {
    const id = Date.now()
    console.log("Creation", id)
    msg = document.createElement("div")
    msg.id = `error-${id}`
    msg.innerHTML = `<p>Something happened at ${getLocaleDateStr()}!</p><code>${message}</code>`
    document.getElementById("messages").style.display = "block"
    document.getElementById("messages").prepend(msg)
    setTimeout(() => {
        const elem = document.getElementById(`error-${id}`)
        if (elem) { elem.remove() }
    }, 7000)
}

const setup = () => {
    getStats()
    setInterval(() => getStats(), 4000) // Update every 4 seconds
}

document.addEventListener('DOMContentLoaded', setup)