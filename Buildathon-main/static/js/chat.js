/**
 * Broadway Show & Event Planner - Chat Interface
 * Handles user interactions, location requests, and displaying chat messages
 */

document.addEventListener('DOMContentLoaded', function() {
    // DOM elements
    const chatForm = document.getElementById('chat-form');
    const messageInput = document.getElementById('message-input');
    const messagesContainer = document.getElementById('messages');
    
    // User location storage
    let userLocation = null;
    
    // Initialize the chat interface
    function initChat() {
        // Add event listener for the chat form
        if (chatForm) {
            chatForm.addEventListener('submit', handleChatSubmit);
        }
        
        // Add a welcome message
        addSystemMessage("Welcome to the Broadway Show & Event Planner! How can I help you today?");
    }
    
    // Handle chat form submission
    async function handleChatSubmit(event) {
        event.preventDefault();
        
        const userMessage = messageInput.value.trim();
        if (!userMessage) return;
        
        // Clear the input
        messageInput.value = '';
        
        // Add user message to the chat
        addUserMessage(userMessage);
        
        // Add an initial "generating" message
        const generatingMsgId = addSystemMessage("I'm generating a plan for you now...", true);
        
        try {
            // Send the message to the server
            const response = await sendChatMessage(userMessage);
            
            // Check if we need to request location
            if (response.location_requested && !userLocation) {
                requestUserLocation();
            }
            
            // Remove the generating message
            removeMessage(generatingMsgId);
            
            // Add the AI response to the chat
            addSystemMessage(response.text_response || response.response);
            
            // Display any events or plans
            if (response.events && response.events.length > 0) {
                displayEvents(response.events);
            }
            
            if (response.plan) {
                displayPlan(response.plan);
            }
        } catch (error) {
            // Remove the generating message
            removeMessage(generatingMsgId);
            
            // Add an error message
            addSystemMessage(`Sorry, there was an error: ${error.message}`);
        }
    }
    
    // Send a chat message to the server
    async function sendChatMessage(message) {
        // Prepare the request body
        const requestBody = {
            message: message
        };
        
        // Add location if available
        if (userLocation) {
            requestBody.location = userLocation;
        }
        
        // Send the request
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestBody)
        });
        
        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }
        
        return await response.json();
    }
    
    // Request the user's location
    function requestUserLocation() {
        // Check if geolocation is available
        if (!navigator.geolocation) {
            addSystemMessage("Your browser doesn't support geolocation. I'll continue with default location settings.");
            return;
        }
        
        // Add a message about requesting location
        addSystemMessage("To provide you with the most accurate information, I'd like to know your location. This helps me find nearby events and calculate travel times.");
        
        // Request the user's location
        navigator.geolocation.getCurrentPosition(
            // Success callback
            function(position) {
                userLocation = {
                    latitude: position.coords.latitude,
                    longitude: position.coords.longitude
                };
                
                // Send the location to the server
                updateUserLocation(userLocation);
                
                addSystemMessage("Thanks! I've updated your location. This will help me provide more relevant suggestions.");
            },
            // Error callback
            function(error) {
                console.error("Error getting location:", error);
                addSystemMessage("I couldn't access your location. I'll continue with default location settings.");
            },
            // Options
            {
                enableHighAccuracy: true,
                timeout: 5000,
                maximumAge: 0
            }
        );
    }
    
    // Update the user's location on the server
    async function updateUserLocation(location) {
        try {
            const response = await fetch('/api/profile', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    latitude: location.latitude,
                    longitude: location.longitude
                })
            });
            
            if (!response.ok) {
                console.error("Failed to update location on server");
            }
        } catch (error) {
            console.error("Error updating location:", error);
        }
    }
    
    // Add a user message to the chat
    function addUserMessage(message) {
        const messageElement = document.createElement('div');
        messageElement.className = 'message user-message';
        messageElement.innerText = message;
        messagesContainer.appendChild(messageElement);
        scrollToBottom();
    }
    
    // Add a system message to the chat
    function addSystemMessage(message, isTemporary = false) {
        const messageElement = document.createElement('div');
        messageElement.className = 'message system-message';
        if (isTemporary) {
            messageElement.className += ' temporary';
        }
        messageElement.innerText = message;
        messagesContainer.appendChild(messageElement);
        scrollToBottom();
        
        // Return an ID for the message so it can be removed if needed
        return Date.now().toString();
    }
    
    // Remove a message from the chat
    function removeMessage(messageId) {
        const temporaryMessages = document.querySelectorAll('.message.temporary');
        if (temporaryMessages.length > 0) {
            temporaryMessages[0].remove();
        }
    }
    
    // Display events in the chat interface
    function displayEvents(events) {
        if (events.length === 0) return;
        
        const eventsContainer = document.createElement('div');
        eventsContainer.className = 'events-container';
        
        const eventsTitle = document.createElement('h3');
        eventsTitle.innerText = 'Events';
        eventsContainer.appendChild(eventsTitle);
        
        events.forEach(event => {
            const eventElement = document.createElement('div');
            eventElement.className = 'event-card';
            
            const eventName = document.createElement('h4');
            eventName.innerText = event.name;
            eventElement.appendChild(eventName);
            
            const eventDetails = document.createElement('p');
            eventDetails.innerHTML = `
                <strong>Venue:</strong> ${event.venue}<br>
                <strong>Time:</strong> ${event.start_time}<br>
                <strong>Price:</strong> $${event.price}
            `;
            eventElement.appendChild(eventDetails);
            
            eventsContainer.appendChild(eventElement);
        });
        
        messagesContainer.appendChild(eventsContainer);
        scrollToBottom();
    }
    
    // Display a plan in the chat interface
    function displayPlan(plan) {
        if (!plan) return;
        
        const planContainer = document.createElement('div');
        planContainer.className = 'plan-container';
        
        const planTitle = document.createElement('h3');
        planTitle.innerText = 'Your Plan';
        planContainer.appendChild(planTitle);
        
        const totalInfo = document.createElement('p');
        totalInfo.innerHTML = `
            <strong>Total Duration:</strong> ${plan.total_duration_hours || 0} hours<br>
            <strong>Total Cost:</strong> $${plan.total_cost || 0}
        `;
        planContainer.appendChild(totalInfo);
        
        messagesContainer.appendChild(planContainer);
        scrollToBottom();
    }
    
    // Scroll the messages container to the bottom
    function scrollToBottom() {
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
    
    // Initialize the chat interface
    initChat();
}); 