importScripts('https://www.gstatic.com/firebasejs/10.7.1/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/10.7.1/firebase-messaging-compat.js');

/**
 * Helper to find an existing Odoo tab and focus it, or open a new one.
 */
async function openDiscussChannel(channelId, action) {
    const discussURLRegexes = [
        new RegExp("/odoo/discuss"),
        new RegExp("/web"),
        new RegExp("/yarics/discuss"), // Matches your custom URL
    ];

    let targetClient;

    // 1. Search for an existing open tab
    const clientsList = await self.clients.matchAll({
        type: "window",
        includeUncontrolled: true
    });

    for (const client of clientsList) {
        // Check if the tab URL matches any of our Odoo patterns
        if (!targetClient && discussURLRegexes.some((r) => r.test(new URL(client.url).pathname))) {
            targetClient = client;
        }
    }

    // 2. Open or Focus
    if (!targetClient) {
        // No tab found? Open a new one with your specific URL format
        if (self.clients.openWindow) {
            await self.clients.openWindow(`/yarics/discuss?active_id=discuss.channel_${channelId}`);
        }
    } else {
        // Tab found? Focus it and tell Odoo to switch chats
        await targetClient.focus();
        targetClient.postMessage({
            action: "OPEN_CHANNEL",
            data: { id: channelId }
        });
    }
}

self.addEventListener('push', function (event) {
    let data = {};
    if (event.data) {
        try {
            data = event.data.json();
            if (data.notification) {
                data = {
                    title: data.notification.title,
                    body: data.notification.body,
                    icon: data.notification.icon,
                    url: data.data ? data.data.url : '/'
                };
            }
        } catch (e) {
            data = { title: 'Notification', body: event.data.text() };
        }
    } else {
        data = { title: 'New Message', body: 'You have a new notification.' };
    }

    const options = {
        body: data.body,
        icon: data.icon || '/web/static/img/logo.png',
        badge: data.badge || '/web/static/img/logo.png',
        data: data.url || '/' // Pass the URL to the click listener
    };

    event.waitUntil(
        self.registration.showNotification(data.title, options)
    );
});

self.addEventListener("notificationclick", (event) => {
    event.notification.close();

    const urlString = event.notification.data;
    let promise;

    // --- SMART PARSING LOGIC ---
    let isChat = false;
    let channelId = null;

    try {
        if (typeof urlString === 'string') {
            // Handle both '?' and '#' style URLs
            const queryPart = urlString.split('?')[1] || urlString.split('#')[1];

            if (queryPart) {
                const urlParams = new URLSearchParams(queryPart);

                // Case A: Standard Odoo ID (id=100)
                if (urlParams.has('id')) {
                    channelId = urlParams.get('id');
                }
                // Case B: Your Custom URL (active_id=discuss.channel_100)
                else if (urlParams.has('active_id')) {
                    const activeId = urlParams.get('active_id');
                    // Remove the text prefix to get just the number
                    channelId = activeId.replace('discuss.channel_', '');
                }

                // Verify it is a chat
                const model = urlParams.get('model');
                if ((model === 'discuss.channel' || urlString.includes('discuss.channel_')) && channelId) {
                    isChat = true;
                }
            }
        }
    } catch (e) {
        console.error("Error parsing notification URL:", e);
    }

    // --- DECISION ---
    if (isChat && channelId) {
        // It's a chat! Use smart focus
        promise = openDiscussChannel(channelId, 'discuss');
    } else {
        // It's something else (Settings, Project, etc.), just open the link
        promise = clients.openWindow(urlString);
    }

    event.waitUntil(promise);
});