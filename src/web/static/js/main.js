const socket = io();

socket.on("connect", () => {
    console.log("Connected to WebSocket");
});

socket.on("sos_triggered", (data) => {
    showNotification(
        "SOS Alert!",
        `${data.user.name} has triggered an SOS`,
        "danger",
    );
    if (typeof refreshSOSList === "function") {
        refreshSOSList();
    }
    if (typeof updateMap === "function") {
        updateMap();
    }
});

socket.on("sos_location_update", (data) => {
    if (typeof updateSOSLocation === "function") {
        updateSOSLocation(data);
    }
});

socket.on("sos_resolved", (data) => {
    showNotification(
        "SOS Resolved",
        "An SOS event has been resolved",
        "success",
    );
    if (typeof refreshSOSList === "function") {
        refreshSOSList();
    }
});

function showNotification(title, message, type = "info") {
    const notification = document.createElement("div");
    notification.className = `alert alert-${type} notification-popup`;
    notification.innerHTML = `
        <strong>${title}</strong><br>
        ${message}
    `;

    notification.style.position = "fixed";
    notification.style.top = "20px";
    notification.style.right = "20px";
    notification.style.zIndex = "9999";
    notification.style.minWidth = "300px";
    notification.style.animation = "slideIn 0.3s ease";

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.animation = "slideOut 0.3s ease";
        setTimeout(() => notification.remove(), 300);
    }, 5000);
}

function initMap(
    elementId,
    locations = [],
    center = [20.5937, 78.9629],
    zoom = 5,
) {
    const map = L.map(elementId).setView(center, zoom);

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: "&copy; OpenStreetMap contributors",
    }).addTo(map);

    locations.forEach((loc) => {
        const markerColor = loc.type === "sos" ? "red" : "blue";
        const marker = L.marker([loc.latitude, loc.longitude], {
            icon: L.divIcon({
                className: "custom-marker",
                html: `<div style="background: ${markerColor}; width: 20px; height: 20px; border-radius: 50%; border: 3px solid white;"></div>`,
                iconSize: [20, 20],
            }),
        }).addTo(map);

        if (loc.popup) {
            marker.bindPopup(loc.popup);
        }
    });

    return map;
}

function formatDate(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now - date;
    const seconds = Math.floor(diff / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);

    if (seconds < 60) return "Just now";
    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    if (days < 7) return `${days}d ago`;

    return date.toLocaleDateString();
}

function formatDuration(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;

    if (hours > 0) {
        return `${hours}h ${minutes}m ${secs}s`;
    } else if (minutes > 0) {
        return `${minutes}m ${secs}s`;
    } else {
        return `${secs}s`;
    }
}

function showLoading(element) {
    element.innerHTML = '<div class="loading"></div>';
}

function hideLoading(element) {
    const loader = element.querySelector(".loading");
    if (loader) loader.remove();
}

async function apiRequest(url, method = "GET", data = null, token = null) {
    const headers = {
        "Content-Type": "application/json",
    };

    if (token) {
        headers["Authorization"] = `Bearer ${token}`;
    }

    const options = {
        method,
        headers,
    };

    if (data && method !== "GET") {
        options.body = JSON.stringify(data);
    }

    try {
        const response = await fetch(url, options);
        return await response.json();
    } catch (error) {
        console.error("API request failed:", error);
        return { success: false, message: error.message };
    }
}

document.addEventListener("DOMContentLoaded", () => {
    const flashMessages = document.querySelectorAll(".alert");
    flashMessages.forEach((msg) => {
        setTimeout(() => {
            msg.style.animation = "slideOut 0.3s ease";
            setTimeout(() => msg.remove(), 300);
        }, 5000);
    });

    const forms = document.querySelectorAll("form");
    forms.forEach((form) => {
        form.addEventListener("submit", (e) => {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML =
                    '<span class="loading"></span> Processing...';
            }
        });
    });
});

const CSS_ANIMATIONS = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
`;

const style = document.createElement("style");
style.textContent = CSS_ANIMATIONS;
document.head.appendChild(style);
