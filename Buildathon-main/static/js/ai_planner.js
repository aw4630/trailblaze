/**
 * AI Planner Module
 * Handles interaction with the OpenAI-driven planning API
 */

const AIPlannerModule = (function() {
    // Private variables
    const apiEndpoint = '/api/plan';
    
    // DOM elements (to be set on init)
    let plannerForm;
    let queryInput;
    let transportSelect;
    let loadingIndicator;
    let resultsContainer;
    let errorContainer;
    
    // Initialize the module
    function init(config) {
        // Set DOM elements from config
        plannerForm = document.getElementById(config.formId || 'planner-form');
        queryInput = document.getElementById(config.queryInputId || 'planner-query');
        transportSelect = document.getElementById(config.transportSelectId || 'transport-mode');
        loadingIndicator = document.getElementById(config.loadingId || 'loading-indicator');
        resultsContainer = document.getElementById(config.resultsId || 'plan-results');
        errorContainer = document.getElementById(config.errorId || 'plan-error');
        
        // Add event listeners
        if (plannerForm) {
            plannerForm.addEventListener('submit', handleFormSubmit);
        }
        
        console.log('AI Planner module initialized');
    }
    
    // Handle form submission
    async function handleFormSubmit(event) {
        event.preventDefault();
        
        // Get form data
        const query = queryInput.value.trim();
        const transportMode = transportSelect ? transportSelect.value : 'walking';
        
        if (!query) {
            showError('Please enter a search query');
            return;
        }
        
        try {
            showLoading(true);
            hideError();
            clearResults();
            
            // Call the planner API
            const plan = await createPlan(query, transportMode);
            
            // Display results
            displayPlanResults(plan);
            
        } catch (error) {
            console.error('Error creating plan:', error);
            showError(`Error creating plan: ${error.message || 'Unknown error'}`);
        } finally {
            showLoading(false);
        }
    }
    
    // Call the API to create a plan
    async function createPlan(query, transportMode = 'walking', maxIterations = 3) {
        const response = await fetch(apiEndpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                query: query,
                transport_mode: transportMode,
                max_iterations: maxIterations
            })
        });
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.message || `API returned status: ${response.status}`);
        }
        
        return await response.json();
    }
    
    // Display the plan results
    function displayPlanResults(plan) {
        if (!resultsContainer) return;
        
        // Clear previous results
        clearResults();
        
        // Create results container
        const resultsWrapper = document.createElement('div');
        resultsWrapper.className = 'plan-results-wrapper';
        
        // Add summary section if available
        if (plan.summary) {
            const summarySection = document.createElement('div');
            summarySection.className = 'plan-summary';
            summarySection.innerHTML = `<h3>Your Plan</h3><p>${plan.summary.replace(/\n/g, '<br>')}</p>`;
            resultsWrapper.appendChild(summarySection);
        }
        
        // Add venues section
        if (plan.venues && plan.venues.length > 0) {
            const venuesSection = createVenuesSection(plan.venues);
            resultsWrapper.appendChild(venuesSection);
        }
        
        // Add events section
        if (plan.events && plan.events.length > 0) {
            const eventsSection = createEventsSection(plan.events);
            resultsWrapper.appendChild(eventsSection);
        }
        
        // Add routes section
        if (plan.routes && plan.routes.length > 0) {
            const routesSection = createRoutesSection(plan.routes);
            resultsWrapper.appendChild(routesSection);
        }
        
        // Add metadata section
        const metaSection = document.createElement('div');
        metaSection.className = 'plan-metadata';
        metaSection.innerHTML = `
            <p><strong>Total Cost:</strong> $${plan.total_cost || '0.00'}</p>
            <p><strong>Total Duration:</strong> ${plan.total_duration_hours || '0'} hours</p>
            <p><small>Plan created in ${plan.iterations || '1'} iteration(s)</small></p>
        `;
        resultsWrapper.appendChild(metaSection);
        
        // Add verification issues if any
        if (plan.verification && plan.verification.has_issues) {
            const issuesSection = document.createElement('div');
            issuesSection.className = 'plan-issues';
            issuesSection.innerHTML = `<h4>Note:</h4><ul>
                ${plan.verification.issues.map(issue => `<li>${issue}</li>`).join('')}
            </ul>`;
            resultsWrapper.appendChild(issuesSection);
        }
        
        // Add to results container
        resultsContainer.appendChild(resultsWrapper);
    }
    
    // Create venues section
    function createVenuesSection(venues) {
        const section = document.createElement('div');
        section.className = 'venues-section';
        section.innerHTML = `<h3>Venues</h3>`;
        
        const venuesList = document.createElement('div');
        venuesList.className = 'venues-list';
        
        venues.forEach(venue => {
            const venueCard = document.createElement('div');
            venueCard.className = 'venue-card';
            venueCard.innerHTML = `
                <h4>${venue.name}</h4>
                <p>${venue.address || 'No address provided'}</p>
                ${venue.rating ? `<p>Rating: ${venue.rating} ⭐</p>` : ''}
                ${venue.price_level ? `<p>Price Level: ${getPrice(venue.price_level)}</p>` : ''}
                ${venue.open_now !== undefined ? `<p>${venue.open_now ? '✅ Open now' : '❌ Currently closed'}</p>` : ''}
                ${venue.phone_number ? `<p>Phone: ${venue.phone_number}</p>` : ''}
                ${venue.website ? `<p><a href="${venue.website}" target="_blank">Visit Website</a></p>` : ''}
            `;
            venuesList.appendChild(venueCard);
        });
        
        section.appendChild(venuesList);
        return section;
    }
    
    // Create events section
    function createEventsSection(events) {
        const section = document.createElement('div');
        section.className = 'events-section';
        section.innerHTML = `<h3>Events</h3>`;
        
        const eventsList = document.createElement('div');
        eventsList.className = 'events-list';
        
        // Sort events by start time
        const sortedEvents = [...events].sort((a, b) => {
            const aTime = a.start_time ? new Date(a.start_time) : new Date(0);
            const bTime = b.start_time ? new Date(b.start_time) : new Date(0);
            return aTime - bTime;
        });
        
        sortedEvents.forEach(event => {
            const eventCard = document.createElement('div');
            eventCard.className = 'event-card';
            eventCard.innerHTML = `
                <h4>${event.name}</h4>
                <p><strong>Venue:</strong> ${event.venue_name || 'No venue specified'}</p>
                ${event.start_time ? `<p><strong>Start:</strong> ${formatTime(event.start_time)}</p>` : ''}
                ${event.end_time ? `<p><strong>End:</strong> ${formatTime(event.end_time)}</p>` : ''}
                ${event.price !== undefined ? `<p><strong>Price:</strong> $${event.price}</p>` : ''}
                ${event.description ? `<p>${event.description}</p>` : ''}
                ${event.timing_issue ? `<p class="warning">⚠️ Timing conflict with another event</p>` : ''}
            `;
            eventsList.appendChild(eventCard);
        });
        
        section.appendChild(eventsList);
        return section;
    }
    
    // Create routes section
    function createRoutesSection(routes) {
        const section = document.createElement('div');
        section.className = 'routes-section';
        section.innerHTML = `<h3>Routes</h3>`;
        
        const routesList = document.createElement('div');
        routesList.className = 'routes-list';
        
        routes.forEach(route => {
            const routeCard = document.createElement('div');
            routeCard.className = 'route-card';
            
            // Format distance and duration
            const distance = route.distance_meters ? formatDistance(route.distance_meters) : 'Unknown distance';
            const duration = route.duration_seconds ? formatDuration(route.duration_seconds) : 'Unknown duration';
            
            routeCard.innerHTML = `
                <h4>From ${route.from} to ${route.to}</h4>
                <p><strong>Distance:</strong> ${distance}</p>
                <p><strong>Duration:</strong> ${duration}</p>
                <p><strong>Travel Mode:</strong> ${route.travel_mode || 'walking'}</p>
            `;
            
            // Add steps if available
            if (route.steps && route.steps.length > 0) {
                const stepsContainer = document.createElement('div');
                stepsContainer.className = 'route-steps';
                stepsContainer.innerHTML = '<h5>Directions:</h5>';
                
                const stepsList = document.createElement('ol');
                route.steps.forEach(step => {
                    const stepItem = document.createElement('li');
                    stepItem.innerHTML = step.instruction;
                    stepsList.appendChild(stepItem);
                });
                
                stepsContainer.appendChild(stepsList);
                routeCard.appendChild(stepsContainer);
            }
            
            routesList.appendChild(routeCard);
        });
        
        section.appendChild(routesList);
        return section;
    }
    
    // Helper function to format time
    function formatTime(timeString) {
        try {
            const date = new Date(timeString);
            return date.toLocaleString('en-US', {
                weekday: 'short',
                month: 'short', 
                day: 'numeric',
                hour: 'numeric',
                minute: '2-digit'
            });
        } catch (e) {
            return timeString;
        }
    }
    
    // Helper function to format distance
    function formatDistance(meters) {
        if (meters < 1000) {
            return `${meters} meters`;
        } else {
            return `${(meters / 1000).toFixed(1)} km`;
        }
    }
    
    // Helper function to format duration
    function formatDuration(seconds) {
        const minutes = Math.floor(seconds / 60);
        if (minutes < 60) {
            return `${minutes} minutes`;
        } else {
            const hours = Math.floor(minutes / 60);
            const remainingMinutes = minutes % 60;
            if (remainingMinutes === 0) {
                return `${hours} hour${hours !== 1 ? 's' : ''}`;
            } else {
                return `${hours} hour${hours !== 1 ? 's' : ''} ${remainingMinutes} min`;
            }
        }
    }
    
    // Helper function to show price level
    function getPrice(priceLevel) {
        if (priceLevel === 0 || priceLevel === null || priceLevel === undefined) return 'Unknown';
        return '$'.repeat(priceLevel);
    }
    
    // Show/hide loading indicator
    function showLoading(isLoading) {
        if (loadingIndicator) {
            loadingIndicator.style.display = isLoading ? 'block' : 'none';
        }
    }
    
    // Show error message
    function showError(message) {
        if (errorContainer) {
            errorContainer.textContent = message;
            errorContainer.style.display = 'block';
        }
    }
    
    // Hide error message
    function hideError() {
        if (errorContainer) {
            errorContainer.textContent = '';
            errorContainer.style.display = 'none';
        }
    }
    
    // Clear results
    function clearResults() {
        if (resultsContainer) {
            resultsContainer.innerHTML = '';
        }
    }
    
    // Public API
    return {
        init: init,
        createPlan: createPlan
    };
})();

// Initialize on DOMContentLoaded
document.addEventListener('DOMContentLoaded', function() {
    // Check if planner form exists
    if (document.getElementById('planner-form')) {
        AIPlannerModule.init({
            formId: 'planner-form',
            queryInputId: 'planner-query',
            transportSelectId: 'transport-mode',
            loadingId: 'loading-indicator',
            resultsId: 'plan-results',
            errorId: 'plan-error'
        });
    }
}); 